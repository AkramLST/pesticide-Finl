from database.connection import get_connection


def get_all_products(include_secret: bool = False):
    conn = get_connection()
    sql = (
        "SELECT p.*, s.name as supplier_name FROM products p "
        "LEFT JOIN suppliers s ON p.supplier_id = s.id "
        "WHERE p.is_active = 1"
    )
    params = []
    if not include_secret:
        sql += " AND COALESCE(p.secret_product, 0) = 0"
    sql += " ORDER BY p.name"
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_product_by_id(product_id: int):
    conn = get_connection()
    row = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def insert_product(data: dict) -> int:
    conn = get_connection()
    try:
        c = conn.cursor()
        c.execute("""
            INSERT INTO products
                (name, description, brand, category, formulation, batch_number,
                 purchase_price, sale_price, supplier_paid_amount, quantity, unit_type, weight,
                 supplier_id, sub_category, manufacturing_date, expiry_date,
                 low_stock_threshold, image, secret_product)
            VALUES
                (:name, :description, :brand, :category, :formulation, :batch_number,
                 :purchase_price, :sale_price, :supplier_paid_amount, :quantity, :unit_type, :weight,
                 :supplier_id, :sub_category, :manufacturing_date, :expiry_date,
                 :low_stock_threshold, :image, :secret_product)
        """, data)
        new_id = c.lastrowid

        # Keep the original stock purchase immutable so sales do not reduce the
        # amount owed to the supplier when they reduce products.quantity.
        if data.get("supplier_id"):
            quantity = int(data.get("quantity", 0) or 0)
            unit_cost = float(data.get("purchase_price", 0) or 0)
            paid = float(data.get("supplier_paid_amount", 0) or 0)
            c.execute("""
                INSERT INTO supplier_purchases
                    (supplier_id, product_id, batch_number, quantity, unit_cost,
                     total_amount, amount_paid, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data["supplier_id"], new_id, data.get("batch_number", ""),
                quantity, unit_cost, quantity * unit_cost, paid,
                f"Initial stock purchase for {data.get('name', '')}",
            ))
        conn.commit()
        return new_id
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def update_product(product_id: int, data: dict):
    conn = get_connection()
    conn.execute("""
        UPDATE products SET
            name=:name, description=:description, brand=:brand, category=:category,
            formulation=:formulation, batch_number=:batch_number,
            purchase_price=:purchase_price, sale_price=:sale_price,
            quantity=:quantity, unit_type=:unit_type, weight=:weight, supplier_id=:supplier_id,
            sub_category=:sub_category, manufacturing_date=:manufacturing_date, expiry_date=:expiry_date,
            low_stock_threshold=:low_stock_threshold, image=:image,
            secret_product=:secret_product,
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


def get_category_metrics(include_secret: bool = False) -> list:
    conn = get_connection()
    products = get_all_products(include_secret=include_secret)
    metrics = []
    for category in ("Seeds", "Fertilizers", "Pesticides"):
        rows = [p for p in products if p.get("category") == category]
        total_qty = sum(p.get("quantity", 0) or 0 for p in rows)
        stock_value = sum((p.get("purchase_price", 0) or 0) * (p.get("quantity", 0) or 0) for p in rows)
        total_products = len(rows)
        low_stock = sum(1 for p in rows if 0 < (p.get("quantity", 0) or 0) <= (p.get("low_stock_threshold", 5) or 5))
        sale_rows = conn.execute(
            """
            SELECT COALESCE(SUM(si.subtotal), 0) AS total_sales,
                   COALESCE(SUM((si.subtotal) - (p.purchase_price * si.quantity)), 0) AS total_income
            FROM sale_items si
            JOIN sales s ON si.sale_id = s.id
            JOIN products p ON si.product_id = p.id
            WHERE s.is_deleted = 0 AND p.category = ?
            """,
            (category,),
        ).fetchone()
        metrics.append({
            "category": category,
            "stock_quantity": total_qty,
            "stock_value": stock_value,
            "total_sales": float(sale_rows["total_sales"] or 0) if sale_rows else 0.0,
            "total_income": float(sale_rows["total_income"] or 0) if sale_rows else 0.0,
            "total_products": total_products,
            "low_stock": low_stock,
        })
    conn.close()
    return metrics
