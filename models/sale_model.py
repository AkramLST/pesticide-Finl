from database.connection import get_connection


def get_all_sales():
    conn = get_connection()
    rows = conn.execute("""
        SELECT s.*, c.name as customer_name, u.name as seller_name
        FROM sales s
        LEFT JOIN customers c ON s.customer_id = c.id
        LEFT JOIN users u ON s.sold_by = u.id
        WHERE s.is_deleted = 0
        ORDER BY s.sale_date DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_sale_by_id(sale_id: int):
    conn = get_connection()
    row = conn.execute("SELECT * FROM sales WHERE id=?", (sale_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


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
            COALESCE(SUM(remaining_amount), 0) as total_pending
        FROM sales WHERE is_deleted=0
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


def get_settings_value(key: str) -> str:
    conn = get_connection()
    row = conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    conn.close()
    return row["value"] if row else ""
