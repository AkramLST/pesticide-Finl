from database.connection import get_connection


def get_all_suppliers():
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM suppliers WHERE is_active=1 ORDER BY name"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_supplier_by_id(supplier_id: int):
    conn = get_connection()
    row = conn.execute("SELECT * FROM suppliers WHERE id=?", (supplier_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_supplier_balance(supplier_id: int) -> dict:
    """Return supplier purchases, payments and current outstanding amount."""
    conn = get_connection()
    row = conn.execute("""
        SELECT
            COALESCE(s.opening_balance, 0) AS opening_balance,
            COALESCE((SELECT SUM(total_amount) FROM supplier_purchases
                      WHERE supplier_id=s.id), 0) AS purchase_total,
            COALESCE((SELECT SUM(amount_paid) FROM supplier_purchases
                      WHERE supplier_id=s.id), 0) AS paid_at_purchase,
            COALESCE((SELECT SUM(amount_paid) FROM supplier_payments
                      WHERE supplier_id=s.id), 0) AS later_payments
        FROM suppliers s
        WHERE s.id=?
    """, (supplier_id,)).fetchone()
    conn.close()
    if not row:
        return {"purchase_total": 0.0, "total_paid": 0.0, "outstanding": 0.0}
    data = dict(row)
    gross = float(data["opening_balance"] or 0) + float(data["purchase_total"] or 0)
    paid = float(data["paid_at_purchase"] or 0) + float(data["later_payments"] or 0)
    return {**data, "total_paid": paid, "outstanding": max(0.0, gross - paid)}


def insert_supplier(data: dict) -> int:
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO suppliers (name, phone, email, address, notes, opening_balance)
        VALUES (:name, :phone, :email, :address, :notes, :opening_balance)
    """, {
        "name": data.get("name", ""),
        "phone": data.get("phone", ""),
        "email": data.get("email", ""),
        "address": data.get("address", ""),
        "notes": data.get("notes", ""),
        "opening_balance": data.get("opening_balance", 0) or 0,
    })
    new_id = c.lastrowid
    conn.commit()
    conn.close()
    return new_id


def update_supplier(supplier_id: int, data: dict):
    conn = get_connection()
    conn.execute("""
        UPDATE suppliers SET name=:name, phone=:phone, email=:email,
            address=:address, notes=:notes, opening_balance=:opening_balance,
            updated_at=datetime('now','localtime')
        WHERE id=:id
    """, {
        "id": supplier_id,
        "name": data.get("name", ""),
        "phone": data.get("phone", ""),
        "email": data.get("email", ""),
        "address": data.get("address", ""),
        "notes": data.get("notes", ""),
        "opening_balance": data.get("opening_balance", 0) or 0,
    })
    conn.commit()
    conn.close()


def delete_supplier(supplier_id: int):
    conn = get_connection()
    conn.execute("UPDATE suppliers SET is_active=0 WHERE id=?", (supplier_id,))
    conn.commit()
    conn.close()
