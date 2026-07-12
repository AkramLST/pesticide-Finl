from database.connection import get_connection
from models.payment_model import get_sale_payments


def get_all_sales():
    conn = get_connection()
    rows = conn.execute("""
        SELECT s.*, c.name as customer_name, u.name as seller_name,
               COALESCE(pay.total_paid, s.paid_amount) AS paid_amount_calc,
               COALESCE(pay.remaining_amount, s.remaining_amount) AS remaining_amount_calc,
               COALESCE(pay.last_payment_date, s.created_at) AS last_payment_date
        FROM sales s
        LEFT JOIN customers c ON s.customer_id = c.id
        LEFT JOIN users u ON s.sold_by = u.id
        LEFT JOIN (
            SELECT sale_id,
                   SUM(amount_paid) AS total_paid,
                   MAX(remaining_balance) AS remaining_amount,
                   MAX(payment_date) AS last_payment_date
            FROM payments
            WHERE sale_id IS NOT NULL
            GROUP BY sale_id
        ) pay ON pay.sale_id = s.id
        WHERE s.is_deleted = 0
        ORDER BY s.sale_date DESC
    """).fetchall()
    conn.close()
    result = []
    for r in rows:
        row = dict(r)
        paid_calc = row.pop("paid_amount_calc", None)
        rem_calc = row.pop("remaining_amount_calc", None)
        if paid_calc is not None:
            row["paid_amount"] = paid_calc
        if rem_calc is not None:
            row["remaining_amount"] = rem_calc
        result.append(row)
    return result


def get_sale_by_id(sale_id: int):
    conn = get_connection()
    row = conn.execute("""
        SELECT s.*, c.name as customer_name, c.phone as customer_phone,
               c.address as customer_address, u.name as seller_name,
               COALESCE(pay.total_paid, s.paid_amount) AS paid_amount_calc,
               COALESCE(pay.remaining_amount, s.remaining_amount) AS remaining_amount_calc
        FROM sales s
        LEFT JOIN customers c ON s.customer_id = c.id
        LEFT JOIN users u ON s.sold_by = u.id
        LEFT JOIN (
            SELECT sale_id,
                   SUM(amount_paid) AS total_paid,
                   MAX(remaining_balance) AS remaining_amount
            FROM payments
            WHERE sale_id IS NOT NULL
            GROUP BY sale_id
        ) pay ON pay.sale_id = s.id
        WHERE s.id=?
    """, (sale_id,)).fetchone()
    conn.close()
    if not row:
        return None
    data = dict(row)
    paid_calc = data.pop("paid_amount_calc", None)
    rem_calc = data.pop("remaining_amount_calc", None)
    if paid_calc is not None:
        data["paid_amount"] = paid_calc
    if rem_calc is not None:
        data["remaining_amount"] = rem_calc
    return data


def get_sale_items(sale_id: int):
    conn = get_connection()
    rows = conn.execute("""
        SELECT si.*, p.name as product_name
        FROM sale_items si
        LEFT JOIN products p ON si.product_id = p.id
        WHERE si.sale_id = ?
    """, (sale_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def insert_sale(sale_data: dict, items: list) -> int:
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO sales
            (invoice_number, customer_id, sold_by, total_amount, discount,
             paid_amount, remaining_amount, payment_method, notes)
        VALUES
            (:invoice_number, :customer_id, :sold_by, :total_amount, :discount,
             :paid_amount, :remaining_amount, :payment_method, :notes)
    """, sale_data)
    sale_id = c.lastrowid
    for item in items:
        c.execute("""
            INSERT INTO sale_items (sale_id, product_id, quantity, unit_price, discount, subtotal)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (sale_id, item["product_id"], item["quantity"],
              item["unit_price"], item["discount"], item["subtotal"]))
    conn.commit()
    conn.close()
    return sale_id


def update_sale_balances(sale_id: int):
    from models.payment_model import _recalc_sale  # local import to avoid cycles
    conn = get_connection()
    try:
        return _recalc_sale(conn, sale_id)
    finally:
        conn.close()


def soft_delete_sale(sale_id: int):
    conn = get_connection()
    conn.execute("UPDATE sales SET is_deleted=1 WHERE id=?", (sale_id,))
    conn.commit()
    conn.close()


def get_sales_summary():
    conn = get_connection()
    row = conn.execute("""
        SELECT
            COUNT(*) as total_sales,
            COALESCE(SUM(total_amount), 0) as total_revenue,
            COALESCE(SUM(COALESCE(pay.remaining_amount, s.remaining_amount)), 0) as total_pending
        FROM sales s
        LEFT JOIN (
            SELECT sale_id, MAX(remaining_balance) AS remaining_amount
            FROM payments
            WHERE sale_id IS NOT NULL
            GROUP BY sale_id
        ) pay ON pay.sale_id = s.id
        WHERE s.is_deleted=0
    """).fetchone()
    conn.close()
    return dict(row) if row else {}


def get_weekly_sales():
    conn = get_connection()
    rows = conn.execute("""
        SELECT date(sale_date) as day, COALESCE(SUM(total_amount),0) as total
        FROM sales
        WHERE is_deleted=0 AND sale_date >= date('now','-6 days')
        GROUP BY day ORDER BY day
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_top_products(limit: int = 5) -> list:
    """Return top-selling products by quantity sold."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT p.name, COALESCE(SUM(si.quantity), 0) as total_sold
        FROM sale_items si
        JOIN products p ON si.product_id = p.id
        GROUP BY si.product_id
        ORDER BY total_sold DESC
        LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_pending_sales() -> list:
    """Return sales with remaining_amount > 0."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT s.id, s.invoice_number, c.name as customer_name,
               COALESCE(pay.remaining_amount, s.remaining_amount) AS remaining_amount,
               s.sale_date
        FROM sales s
        LEFT JOIN customers c ON s.customer_id = c.id
        LEFT JOIN (
            SELECT sale_id, MAX(remaining_balance) AS remaining_amount
            FROM payments
            WHERE sale_id IS NOT NULL
            GROUP BY sale_id
        ) pay ON pay.sale_id = s.id
        WHERE s.is_deleted=0 AND COALESCE(pay.remaining_amount, s.remaining_amount) > 0
        ORDER BY s.sale_date DESC
        LIMIT 10
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_payment_history(sale_id: int):
    return get_sale_payments(sale_id)


def get_settings_value(key: str) -> str:
    conn = get_connection()
    row = conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    conn.close()
    return row["value"] if row else ""
