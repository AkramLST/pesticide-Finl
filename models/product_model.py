from database.connection import get_connection


def get_all_products():
    conn = get_connection()
    rows = conn.execute(
        "SELECT p.*, s.name as supplier_name FROM products p "
        "LEFT JOIN suppliers s ON p.supplier_id = s.id "
        "WHERE p.is_active = 1 ORDER BY p.name"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_product_by_id(product_id: int):
    conn = get_connection()
    row = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def insert_product(data: dict) -> int:
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO products
            (name, description, brand, category, formulation,
             purchase_price, sale_price, quantity, unit_type, weight,
             supplier_id, manufacturing_date, expiry_date, low_stock_threshold, image)
        VALUES
            (:name, :description, :brand, :category, :formulation,
             :purchase_price, :sale_price, :quantity, :unit_type, :weight,
             :supplier_id, :manufacturing_date, :expiry_date, :low_stock_threshold, :image)
    """, data)
    new_id = c.lastrowid
    conn.commit()
    conn.close()
    return new_id


def update_product(product_id: int, data: dict):
    conn = get_connection()
    conn.execute("""
        UPDATE products SET
            name=:name, description=:description, brand=:brand, category=:category,
            formulation=:formulation, purchase_price=:purchase_price, sale_price=:sale_price,
            quantity=:quantity, unit_type=:unit_type, weight=:weight, supplier_id=:supplier_id,
            manufacturing_date=:manufacturing_date, expiry_date=:expiry_date,
            low_stock_threshold=:low_stock_threshold, image=:image,
            updated_at=datetime('now','localtime')
        WHERE id=:id
    """, {**data, "id": product_id})
    conn.commit()
    conn.close()


def delete_product(product_id: int):
    conn = get_connection()
    conn.execute(
        "UPDATE products SET is_active=0, updated_at=datetime('now','localtime') WHERE id=?",
        (product_id,)
    )
    conn.commit()
    conn.close()


def deduct_stock(product_id: int, qty: int):
    conn = get_connection()
    conn.execute(
        "UPDATE products SET quantity = quantity - ?, updated_at=datetime('now','localtime') WHERE id=?",
        (qty, product_id)
    )
    conn.commit()
    conn.close()


def get_low_stock_products():
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM products WHERE is_active=1 AND quantity <= low_stock_threshold"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
