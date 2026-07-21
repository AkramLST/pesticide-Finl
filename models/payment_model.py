from typing import Optional

from database.connection import get_connection


def get_sale_payments(sale_id: int):
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT p.*, COALESCE(u.name, u.username, 'System') AS recorded_by_name
        FROM payments p
        LEFT JOIN users u ON p.recorded_by = u.id
        WHERE p.sale_id = ?
        ORDER BY datetime(p.payment_date) ASC, p.id ASC
        """,
        (sale_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_customer_payments(customer_id: int):
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT p.*, s.invoice_number,
               COALESCE(u.name, u.username, 'System') AS recorded_by_name
        FROM payments p
        LEFT JOIN sales s ON p.sale_id = s.id
        LEFT JOIN users u ON p.recorded_by = u.id
        WHERE p.customer_id = ?
        ORDER BY datetime(p.payment_date) ASC, p.id ASC
        """,
        (customer_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def _recalc_sale(conn, sale_id: int):
    row = conn.execute(
        """
        SELECT s.id, s.total_amount,
               COALESCE(SUM(p.amount_paid), 0) AS paid_total
        FROM sales s
        LEFT JOIN payments p ON p.sale_id = s.id
        WHERE s.id = ?
        GROUP BY s.id
        """,
        (sale_id,),
    ).fetchone()
    if not row:
        return None
    paid = float(row["paid_total"] or 0)
    total = float(row["total_amount"] or 0)
    remaining = max(0.0, total - paid)
    conn.execute(
        """
        UPDATE sales
        SET paid_amount = ?, remaining_amount = ?,
            updated_at = datetime('now','localtime')
        WHERE id = ?
        """,
        (paid, remaining, sale_id),
    )
    return {"paid_amount": paid, "remaining_amount": remaining, "total_amount": total}


def _recalc_customer(conn, customer_id: int):
    row = conn.execute(
        """
        SELECT
            COALESCE((SELECT opening_balance FROM customers WHERE id = ?), 0) AS opening_balance,
            COALESCE((
                SELECT SUM(amount_paid)
                FROM payments
                WHERE customer_id = ?
            ), 0) AS total_paid,
            COALESCE((
                SELECT SUM(remaining_amount)
                FROM sales
                WHERE customer_id = ? AND is_deleted = 0
            ), 0) AS total_pending
        """,
        (customer_id, customer_id, customer_id),
    ).fetchone()
    if not row:
        return None
    opening_balance = float(row["opening_balance"] or 0)
    paid = float(row["total_paid"] or 0)
    pending_sales = float(row["total_pending"] or 0)
    opening_paid_row = conn.execute(
        """
        SELECT COALESCE(SUM(amount_paid), 0) AS total_paid
        FROM payments
        WHERE customer_id = ? AND sale_id IS NULL
        """,
        (customer_id,),
    ).fetchone()
    opening_paid = float(opening_paid_row["total_paid"] or 0) if opening_paid_row else 0.0
    pending = max(0.0, opening_balance - opening_paid) + pending_sales
    conn.execute(
        """
        UPDATE customers
        SET total_paid = ?, total_pending = ?,
            last_purchase_date = datetime('now','localtime'),
            updated_at = datetime('now','localtime')
        WHERE id = ?
        """,
        (paid, pending, customer_id),
    )
    return {"total_paid": paid, "total_pending": pending}


def record_sale_payment(
    sale_id: int,
    amount: float,
    payment_method: str,
    notes: str = "",
    recorded_by: Optional[int] = None,
):
    conn = get_connection()
    try:
        sale = conn.execute(
            "SELECT id, customer_id, total_amount, paid_amount, remaining_amount FROM sales WHERE id=?",
            (sale_id,),
        ).fetchone()
        if not sale:
            raise ValueError("Sale not found.")

        amount = float(amount or 0)
        remaining = float(sale["remaining_amount"] or 0)
        if amount <= 0:
            raise ValueError("Payment amount must be greater than zero.")
        if amount > remaining:
            amount = remaining

        new_remaining = max(0.0, remaining - amount)
        conn.execute(
            """
            INSERT INTO payments
                (sale_id, customer_id, amount_paid, payment_method,
                 payment_date, notes, remaining_balance, recorded_by, created_at)
            VALUES
                (?, ?, ?, ?, datetime('now','localtime'), ?, ?, ?, datetime('now','localtime'))
            """,
            (
                sale_id,
                sale["customer_id"],
                amount,
                payment_method,
                notes,
                new_remaining,
                recorded_by,
            ),
        )
        sale_state = _recalc_sale(conn, sale_id)
        customer_state = None
        if sale["customer_id"]:
            customer_state = _recalc_customer(conn, sale["customer_id"])
        conn.commit()
        return {
            "amount_paid": amount,
            "remaining_amount": sale_state["remaining_amount"] if sale_state else new_remaining,
            "customer_state": customer_state,
        }
    finally:
        conn.close()


def record_customer_payment(
    customer_id: int,
    amount: float,
    payment_method: str,
    notes: str = "",
    recorded_by: Optional[int] = None,
):
    conn = get_connection()
    try:
        amount = float(amount or 0)
        if amount <= 0:
            raise ValueError("Payment amount must be greater than zero.")

        open_sales = conn.execute(
            """
            SELECT id, remaining_amount
            FROM sales
            WHERE customer_id = ? AND is_deleted = 0 AND remaining_amount > 0
            ORDER BY datetime(sale_date) ASC, id ASC
            """,
            (customer_id,),
        ).fetchall()
        if not open_sales:
            conn.execute(
                """
                INSERT INTO payments
                    (sale_id, customer_id, amount_paid, payment_method,
                     payment_date, notes, remaining_balance, recorded_by, created_at)
                VALUES
                    (NULL, ?, ?, ?, datetime('now','localtime'), ?, 0, ?, datetime('now','localtime'))
                """,
                (customer_id, amount, payment_method, notes, recorded_by),
            )
            customer_state = _recalc_customer(conn, customer_id)
            conn.commit()
            return {"allocations": [], "customer_state": customer_state}

        remaining_to_apply = amount
        allocations = []
        for sale in open_sales:
            if remaining_to_apply <= 0:
                break
            sale_remaining = float(sale["remaining_amount"] or 0)
            if sale_remaining <= 0:
                continue
            applied = min(remaining_to_apply, sale_remaining)
            conn.execute(
                """
                INSERT INTO payments
                    (sale_id, customer_id, amount_paid, payment_method,
                     payment_date, notes, remaining_balance, recorded_by, created_at)
                VALUES
                    (?, ?, ?, ?, datetime('now','localtime'), ?, ?, ?, datetime('now','localtime'))
                """,
                (
                    sale["id"],
                    customer_id,
                    applied,
                    payment_method,
                    notes,
                    sale_remaining - applied,
                    recorded_by,
                ),
            )
            _recalc_sale(conn, sale["id"])
            allocations.append({"sale_id": sale["id"], "amount": applied})
            remaining_to_apply -= applied

        if remaining_to_apply > 0:
            conn.execute(
                """
                INSERT INTO payments
                    (sale_id, customer_id, amount_paid, payment_method,
                     payment_date, notes, remaining_balance, recorded_by, created_at)
                VALUES
                    (NULL, ?, ?, ?, datetime('now','localtime'), ?, 0, ?, datetime('now','localtime'))
                """,
                (customer_id, remaining_to_apply, payment_method, notes, recorded_by),
            )
            allocations.append({"sale_id": None, "amount": remaining_to_apply})

        customer_state = _recalc_customer(conn, customer_id)
        conn.commit()
        return {"allocations": allocations, "customer_state": customer_state}
    finally:
        conn.close()


def _recalc_supplier(conn, supplier_id: int):
    row = conn.execute(
        """
        SELECT
            COALESCE((SELECT opening_balance FROM suppliers WHERE id = ?), 0) AS opening_balance,
            COALESCE((
                SELECT SUM(total_amount - amount_paid)
                FROM supplier_purchases
                WHERE supplier_id = ?
            ), 0) AS purchase_balance,
            COALESCE((
                SELECT SUM(amount_paid)
                FROM supplier_payments
                WHERE supplier_id = ?
            ), 0) AS total_paid
        """,
        (supplier_id, supplier_id, supplier_id),
    ).fetchone()
    if not row:
        return None
    opening_balance = float(row["opening_balance"] or 0)
    purchase_balance = float(row["purchase_balance"] or 0)
    total_paid = float(row["total_paid"] or 0)
    pending = max(0.0, opening_balance + purchase_balance - total_paid)
    conn.execute(
        """
        UPDATE suppliers
        SET total_transactions = ?, updated_at = datetime('now','localtime')
        WHERE id = ?
        """,
        (pending, supplier_id),
    )
    return {"total_paid": total_paid, "total_pending": pending}


def record_supplier_payment(
    supplier_id: int,
    amount: float,
    payment_method: str,
    notes: str = "",
    recorded_by: Optional[int] = None,
):
    conn = get_connection()
    try:
        amount = float(amount or 0)
        if amount <= 0:
            raise ValueError("Payment amount must be greater than zero.")

        conn.execute(
            """
            INSERT INTO supplier_payments
                (supplier_id, amount_paid, payment_method,
                 payment_date, notes, recorded_by, created_at)
            VALUES
                (?, ?, ?, datetime('now','localtime'), ?, ?, datetime('now','localtime'))
            """,
            (supplier_id, amount, payment_method, notes, recorded_by),
        )
        state = _recalc_supplier(conn, supplier_id)
        conn.commit()
        return state
    finally:
        conn.close()


def get_supplier_payment_summary():
    conn = get_connection()
    row = conn.execute(
        """
        SELECT
            COALESCE(SUM(opening_balance), 0) AS opening_total,
            COALESCE((SELECT SUM(total_amount) FROM supplier_purchases), 0) AS purchase_total,
            COALESCE((SELECT SUM(amount_paid) FROM supplier_purchases), 0) AS purchase_paid_total,
            COALESCE((SELECT SUM(amount_paid) FROM supplier_payments), 0) AS paid_total
        FROM suppliers
        WHERE is_active = 1
        """
    ).fetchone()
    conn.close()
    opening_total = float(row["opening_total"] or 0) if row else 0.0
    paid_total = float(row["paid_total"] or 0) if row else 0.0
    purchase_paid_total = float(row["purchase_paid_total"] or 0) if row else 0.0
    purchase_total = float(row["purchase_total"] or 0) if row else 0.0
    return {
        "total_paid": paid_total + purchase_paid_total,
        "total_pending": max(0.0, opening_total + purchase_total - paid_total - purchase_paid_total),
    }
