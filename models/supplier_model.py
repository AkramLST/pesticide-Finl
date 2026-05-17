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
        INSERT INTO suppliers (name, phone, email, address, notes)
        VALUES (:name, :phone, :email, :address, :notes)
    """, data)
    new_id = c.lastrowid
    conn.commit()
    conn.close()
    return new_id


def update_supplier(supplier_id: int, data: dict):
    conn = get_connection()
    conn.execute("""
        UPDATE suppliers SET name=:name, phone=:phone, email=:email,
            address=:address, notes=:notes, updated_at=datetime('now','localtime')
        WHERE id=:id
    """, {**data, "id": supplier_id})
    conn.commit()
    conn.close()


def delete_supplier(supplier_id: int):
    conn = get_connection()
    conn.execute("UPDATE suppliers SET is_active=0 WHERE id=?", (supplier_id,))
    conn.commit()
    conn.close()
