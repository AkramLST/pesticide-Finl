import hashlib
from database.connection import get_connection


def _hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def get_user_by_credentials(username: str, password: str):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM users WHERE username=? AND password_hash=? AND is_active=1",
        (username, _hash(password))
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_users():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM users ORDER BY name").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_user_by_id(user_id: int):
    conn = get_connection()
    row = conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def insert_user(data: dict) -> int:
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO users (name, username, password_hash, role, phone, email, profile_image)
        VALUES (:name, :username, :password_hash, :role, :phone, :email, :profile_image)
    """, {**data, "password_hash": _hash(data["password"])})
    new_id = c.lastrowid
    conn.commit()
    conn.close()
    return new_id


def update_user(user_id: int, data: dict):
    conn = get_connection()
    conn.execute("""
        UPDATE users SET name=:name, username=:username, role=:role,
            phone=:phone, email=:email, profile_image=:profile_image,
            updated_at=datetime('now','localtime')
        WHERE id=:id
    """, {**data, "id": user_id})
    conn.commit()
    conn.close()


def update_password(user_id: int, new_password: str):
    conn = get_connection()
    conn.execute(
        "UPDATE users SET password_hash=?, updated_at=datetime('now','localtime') WHERE id=?",
        (_hash(new_password), user_id)
    )
    conn.commit()
    conn.close()


def toggle_user_status(user_id: int, is_active: int):
    conn = get_connection()
    conn.execute("UPDATE users SET is_active=? WHERE id=?", (is_active, user_id))
    conn.commit()
    conn.close()


def update_last_login(user_id: int):
    conn = get_connection()
    conn.execute(
        "UPDATE users SET last_login=datetime('now','localtime') WHERE id=?",
        (user_id,)
    )
    conn.commit()
    conn.close()
