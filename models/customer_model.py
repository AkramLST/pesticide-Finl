from database.connection import get_connection
from models.payment_model import record_customer_payment


def get_all_customers():
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT c.*,
               COALESCE(c.opening_balance, 0) AS opening_balance_calc,
               COALESCE((
                   SELECT SUM(amount_paid)
                   FROM payments
                   WHERE customer_id = c.id
               ), 0) AS total_paid_calc,
               COALESCE((
                   SELECT SUM(remaining_amount)
                   FROM sales
                   WHERE customer_id = c.id AND is_deleted = 0
               ), 0) AS total_pending_calc,
               (
                   SELECT MAX(sale_date)
                   FROM sales
                   WHERE customer_id = c.id AND is_deleted = 0
               ) AS last_sale_calc
        FROM customers c
        WHERE c.is_active=1
        ORDER BY c.name
        """
    ).fetchall()
    customers = []
    for r in rows:
        row = dict(r)
        opening_calc = row.pop("opening_balance_calc", None)
        paid_calc = row.pop("total_paid_calc", None)
        pend_calc = row.pop("total_pending_calc", None)
        last_calc = row.pop("last_sale_calc", None)
        if opening_calc is not None:
            row["opening_balance"] = opening_calc
        if paid_calc is not None:
            row["total_paid"] = paid_calc
        if pend_calc is not None:
            opening_paid_row = conn.execute(
                """
                SELECT COALESCE(SUM(amount_paid), 0) AS total_paid
                FROM payments
                WHERE customer_id = ? AND sale_id IS NULL
                """,
                (row["id"],),
            ).fetchone()
            opening_paid = float(opening_paid_row["total_paid"] or 0) if opening_paid_row else 0.0
            row["total_pending"] = max(0.0, float(row.get("opening_balance", 0) or 0) - opening_paid) + pend_calc
        if last_calc is not None:
            row["last_purchase_date"] = last_calc
        customers.append(row)
    conn.close()
    return customers


def get_customer_by_id(customer_id: int):
    conn = get_connection()
    row = conn.execute("SELECT * FROM customers WHERE id=?", (customer_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def insert_customer(data: dict) -> int:
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO customers (name, phone, address, notes, opening_balance)
        VALUES (:name, :phone, :address, :notes, :opening_balance)
    """, {
        "name": data.get("name", ""),
        "phone": data.get("phone", ""),
        "address": data.get("address", ""),
        "notes": data.get("notes", ""),
        "opening_balance": data.get("opening_balance", 0) or 0,
    })
    new_id = c.lastrowid
    conn.commit()
    conn.close()
    return new_id


def update_customer(customer_id: int, data: dict):
    conn = get_connection()
    conn.execute("""
        UPDATE customers SET name=:name, phone=:phone, address=:address,
            notes=:notes, opening_balance=:opening_balance,
            updated_at=datetime('now','localtime')
        WHERE id=:id
    """, {
        "id": customer_id,
        "name": data.get("name", ""),
        "phone": data.get("phone", ""),
        "address": data.get("address", ""),
        "notes": data.get("notes", ""),
        "opening_balance": data.get("opening_balance", 0) or 0,
    })
    conn.commit()
    conn.close()


def delete_customer(customer_id: int):
    conn = get_connection()
    conn.execute("UPDATE customers SET is_active=0 WHERE id=?", (customer_id,))
    conn.commit()
    conn.close()


def update_customer_balance(customer_id: int, paid: float, pending: float):
    conn = get_connection()
    conn.execute("""
        UPDATE customers SET
            total_paid = total_paid + ?,
            total_pending = MAX(total_pending - ?, 0),
            last_purchase_date = datetime('now','localtime'),
            updated_at = datetime('now','localtime')
        WHERE id = ?
    """, (paid, pending, customer_id))
    conn.commit()
    conn.close()


def apply_customer_payment(customer_id: int, amount: float, payment_method: str,
                           notes: str = "", recorded_by=None):
    return record_customer_payment(customer_id, amount, payment_method, notes, recorded_by)
