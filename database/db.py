import sqlite3

DB_NAME = "database/pesticide.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        description TEXT,
        brand TEXT,
        category TEXT,
        formulation TEXT,
        price REAL,
        weight TEXT,
        quantity INTEGER,
        image TEXT
    )
    """)

    conn.commit()
    conn.close()


def insert_product(data):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO products
    (name, description, brand, category, formulation, price, weight, quantity, image)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, data)

    conn.commit()
    conn.close()


def get_products():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM products")

    products = cursor.fetchall()

    conn.close()

    return products

def delete_product(product_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))

    conn.commit()
    conn.close()
