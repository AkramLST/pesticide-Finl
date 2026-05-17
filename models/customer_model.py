from database.connection import get_connection


def get_all_customers():
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM customers WHERE is_active=1 ORDER BY name"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_customer_by_id(customer_id: int):
    conn = get_connection()
    row = conn.execute("SELECT * FROM customers WHERE id=?", (customer_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def insert_customer(data: dict) -> int:
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO customers (name, phone, address, notes)
        VALUES (:name, :phone, :address, :notes)
    """, data)
    new_id = c.lastrowid
    conn.commit()
    conn.close()
    return new_id


def update_customer(customer_id: int, data: dict):
    conn = get_connection()
    conn.execute("""
        UPDATE customers SET name=:name, phone=:phone, address=:address,
            notes=:notes, updated_at=datetime('now','localtime')
        WHERE id=:id
    """, {**data, "id": customer_id})
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
            total_pending = total_pending + ?,
            last_purchase_date = datetime('now','localtime'),
            updated_at = datetime('now','localtime')
        WHERE id = ?
    """, (paid, pending, customer_id))
    conn.commit()
    conn.close()
