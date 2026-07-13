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
