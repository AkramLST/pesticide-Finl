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


def get_supplier_purchase_entries(supplier_id: int) -> list:
    conn = get_connection()
    missing_prods = conn.execute("""
        SELECT p.id, p.name, p.batch_number, p.quantity, p.purchase_price, p.supplier_paid_amount
        FROM products p
        WHERE p.supplier_id = ? AND p.id NOT IN (
            SELECT product_id FROM supplier_purchases WHERE supplier_id = ? AND product_id IS NOT NULL
        )
    """, (supplier_id, supplier_id)).fetchall()

    if missing_prods:
        for p in missing_prods:
            qty = int(p["quantity"] or 0)
            cost = float(p["purchase_price"] or 0)
            paid = float(p["supplier_paid_amount"] or 0)
            conn.execute("""
                INSERT INTO supplier_purchases
                    (supplier_id, product_id, batch_number, quantity, unit_cost,
                     total_amount, amount_paid, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                supplier_id, p["id"], p["batch_number"] or "",
                qty, cost, qty * cost, paid,
                f"Initial stock purchase for {p['name'] or ''}"
            ))
        conn.commit()

    rows = conn.execute("""
        SELECT sp.*, p.name AS product_name, p.category, p.sale_price
        FROM supplier_purchases sp
        LEFT JOIN products p ON sp.product_id = p.id
        WHERE sp.supplier_id = ?
        ORDER BY datetime(sp.purchase_date) DESC, sp.id DESC
    """, (supplier_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


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
    try:
        old = conn.execute(
            "SELECT quantity, supplier_id FROM products WHERE id = ?",
            (product_id,),
        ).fetchone()
        old_quantity = int(old["quantity"] or 0) if old else 0
        old_supplier = old["supplier_id"] if old else None
        new_quantity = int(data.get("quantity", 0) or 0)
        new_supplier = data.get("supplier_id")

        existing_purchase = False
        if new_supplier:
            check = conn.execute(
                "SELECT COUNT(*) as cnt FROM supplier_purchases WHERE supplier_id=? AND product_id=?",
                (new_supplier, product_id)
            ).fetchone()
            existing_purchase = (check["cnt"] > 0) if check else False

        if new_supplier and not existing_purchase and new_quantity > 0:
            added_quantity = new_quantity
        else:
            added_quantity = max(0, new_quantity - old_quantity)

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

        if added_quantity > 0 and new_supplier:
            unit_cost = float(data.get("purchase_price", 0) or 0)
            conn.execute("""
                INSERT INTO supplier_purchases
                    (supplier_id, product_id, batch_number, quantity, unit_cost,
                     total_amount, amount_paid, notes)
                VALUES (?, ?, ?, ?, ?, ?, 0, ?)
            """, (
                new_supplier, product_id, data.get("batch_number", ""),
                added_quantity, unit_cost, added_quantity * unit_cost,
                f"Stock addition (+{added_quantity}) for {data.get('name', '')}",
            ))
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
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
