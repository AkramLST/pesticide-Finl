import sqlite3

DB_NAME = "database/pesticide.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    return conn


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
        active_ingredient TEXT,
        formulation TEXT,
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
    (name, description, brand, category, active_ingredient, formulation, image)
    VALUES (?, ?, ?, ?, ?, ?, ?)
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

