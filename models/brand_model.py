from database.connection import get_connection


def get_all_brands(include_inactive: bool = False):
    conn = get_connection()
    sql = "SELECT * FROM brands"
    if not include_inactive:
        sql += " WHERE is_active=1"
    sql += " ORDER BY name"
    rows = conn.execute(sql).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_brand_by_id(brand_id: int):
    conn = get_connection()
    row = conn.execute("SELECT * FROM brands WHERE id=?", (brand_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def insert_brand(name: str) -> int:
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO brands (name) VALUES (?)", (name.strip(),))
    new_id = c.lastrowid
    conn.commit()
    conn.close()
    return new_id


def update_brand(brand_id: int, name: str):
    conn = get_connection()
    conn.execute(
        "UPDATE brands SET name=?, updated_at=datetime('now','localtime') WHERE id=?",
        (name.strip(), brand_id),
    )
    conn.commit()
    conn.close()


def set_brand_active(brand_id: int, active: bool):
    conn = get_connection()
    conn.execute(
        "UPDATE brands SET is_active=?, updated_at=datetime('now','localtime') WHERE id=?",
        (1 if active else 0, brand_id),
    )
    conn.commit()
    conn.close()


def delete_brand(brand_id: int):
    set_brand_active(brand_id, False)
