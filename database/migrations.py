import hashlib
from database.connection import get_connection
from utils.config import ADMIN_USERS, DEFAULT_BRANDS
from utils.logger import get_logger

log = get_logger(__name__)


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def _add_column_if_missing(conn, table: str, column: str, definition: str):
    """Add a column to a table only if it doesn't already exist."""
    existing = [row[1] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()]
    if column not in existing:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
        log.info(f"Added column {table}.{column}")


def _upgrade_existing_tables(conn):
    """Add new columns to pre-existing tables from the old schema."""
    product_upgrades = [
        ("purchase_price",      "REAL    NOT NULL DEFAULT 0"),
        ("sale_price",          "REAL    NOT NULL DEFAULT 0"),
        ("unit_type",           "TEXT"),
        ("supplier_id",         "INTEGER"),
        ("sub_category",        "TEXT"),
        ("manufacturing_date",  "TEXT"),
        ("expiry_date",         "TEXT"),
        ("low_stock_threshold", "INTEGER NOT NULL DEFAULT 5"),
        ("barcode",             "TEXT"),
        ("secret_product",      "INTEGER NOT NULL DEFAULT 0"),
        ("is_active",           "INTEGER DEFAULT 1"),
        ("created_at",          "TEXT"),
        ("updated_at",          "TEXT"),
    ]
    for col, defn in product_upgrades:
        _add_column_if_missing(conn, "products", col, defn)

    payment_upgrades = [
        ("remaining_balance", "REAL NOT NULL DEFAULT 0"),
        ("recorded_by",       "INTEGER"),
        ("created_at",        "TEXT"),
    ]
    for col, defn in payment_upgrades:
        _add_column_if_missing(conn, "payments", col, defn)

    conn.commit()


def run_migrations():
    conn = get_connection()
    c = conn.cursor()

    c.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        name            TEXT    NOT NULL,
        username        TEXT    NOT NULL UNIQUE,
        password_hash   TEXT    NOT NULL,
        role            TEXT    NOT NULL DEFAULT 'Staff',
        phone           TEXT,
        email           TEXT,
        profile_image   TEXT,
        last_login      TEXT,
        is_active       INTEGER NOT NULL DEFAULT 1,
        created_at      TEXT    NOT NULL DEFAULT (datetime('now','localtime')),
        updated_at      TEXT    NOT NULL DEFAULT (datetime('now','localtime'))
    );

    CREATE TABLE IF NOT EXISTS suppliers (
        id                  INTEGER PRIMARY KEY AUTOINCREMENT,
        name                TEXT    NOT NULL,
        phone               TEXT,
        email               TEXT,
        address             TEXT,
        notes               TEXT,
        total_transactions  REAL    NOT NULL DEFAULT 0,
        is_active           INTEGER NOT NULL DEFAULT 1,
        created_at          TEXT    NOT NULL DEFAULT (datetime('now','localtime')),
        updated_at          TEXT    NOT NULL DEFAULT (datetime('now','localtime'))
    );

    CREATE TABLE IF NOT EXISTS products (
        id                  INTEGER PRIMARY KEY AUTOINCREMENT,
        name                TEXT    NOT NULL,
        description         TEXT,
        brand               TEXT,
        category            TEXT,
        sub_category        TEXT,
        formulation         TEXT,
        purchase_price      REAL    NOT NULL DEFAULT 0,
        sale_price          REAL    NOT NULL DEFAULT 0,
        quantity            INTEGER NOT NULL DEFAULT 0,
        unit_type           TEXT,
        weight              TEXT,
        supplier_id         INTEGER REFERENCES suppliers(id) ON DELETE SET NULL,
        manufacturing_date  TEXT,
        expiry_date         TEXT,
        low_stock_threshold INTEGER NOT NULL DEFAULT 5,
        image               TEXT,
        barcode             TEXT,
        secret_product      INTEGER NOT NULL DEFAULT 0,
        is_active           INTEGER NOT NULL DEFAULT 1,
        created_at          TEXT    NOT NULL DEFAULT (datetime('now','localtime')),
        updated_at          TEXT    NOT NULL DEFAULT (datetime('now','localtime'))
    );

    CREATE TABLE IF NOT EXISTS brands (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        name        TEXT    NOT NULL UNIQUE,
        is_active   INTEGER NOT NULL DEFAULT 1,
        created_at  TEXT    NOT NULL DEFAULT (datetime('now','localtime')),
        updated_at  TEXT    NOT NULL DEFAULT (datetime('now','localtime'))
    );

    CREATE TABLE IF NOT EXISTS customers (
        id                  INTEGER PRIMARY KEY AUTOINCREMENT,
        name                TEXT    NOT NULL,
        phone               TEXT,
        address             TEXT,
        notes               TEXT,
        total_paid          REAL    NOT NULL DEFAULT 0,
        total_pending       REAL    NOT NULL DEFAULT 0,
        last_purchase_date  TEXT,
        is_active           INTEGER NOT NULL DEFAULT 1,
        created_at          TEXT    NOT NULL DEFAULT (datetime('now','localtime')),
        updated_at          TEXT    NOT NULL DEFAULT (datetime('now','localtime'))
    );

    CREATE TABLE IF NOT EXISTS sales (
        id               INTEGER PRIMARY KEY AUTOINCREMENT,
        invoice_number   TEXT    NOT NULL UNIQUE,
        customer_id      INTEGER REFERENCES customers(id) ON DELETE SET NULL,
        sold_by          INTEGER REFERENCES users(id) ON DELETE SET NULL,
        sale_date        TEXT    NOT NULL DEFAULT (datetime('now','localtime')),
        total_amount     REAL    NOT NULL DEFAULT 0,
        discount         REAL    NOT NULL DEFAULT 0,
        paid_amount      REAL    NOT NULL DEFAULT 0,
        remaining_amount REAL    NOT NULL DEFAULT 0,
        payment_method   TEXT,
        notes            TEXT,
        is_deleted       INTEGER NOT NULL DEFAULT 0,
        created_at       TEXT    NOT NULL DEFAULT (datetime('now','localtime'))
    );

    CREATE TABLE IF NOT EXISTS sale_items (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        sale_id     INTEGER NOT NULL REFERENCES sales(id) ON DELETE CASCADE,
        product_id  INTEGER REFERENCES products(id) ON DELETE SET NULL,
        quantity    INTEGER NOT NULL DEFAULT 1,
        unit_price  REAL    NOT NULL DEFAULT 0,
        discount    REAL    NOT NULL DEFAULT 0,
        subtotal    REAL    NOT NULL DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS payments (
        id             INTEGER PRIMARY KEY AUTOINCREMENT,
        sale_id        INTEGER REFERENCES sales(id) ON DELETE CASCADE,
        customer_id    INTEGER REFERENCES customers(id) ON DELETE SET NULL,
        amount_paid    REAL    NOT NULL DEFAULT 0,
        payment_method TEXT,
        payment_date   TEXT    NOT NULL DEFAULT (datetime('now','localtime')),
        notes          TEXT,
        remaining_balance REAL NOT NULL DEFAULT 0,
        recorded_by    INTEGER REFERENCES users(id) ON DELETE SET NULL,
        created_at      TEXT    NOT NULL DEFAULT (datetime('now','localtime'))
    );

    CREATE TABLE IF NOT EXISTS invoices (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        sale_id      INTEGER REFERENCES sales(id) ON DELETE CASCADE,
        invoice_path TEXT,
        generated_at TEXT    NOT NULL DEFAULT (datetime('now','localtime'))
    );

    CREATE TABLE IF NOT EXISTS inventory_log (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id      INTEGER REFERENCES products(id) ON DELETE CASCADE,
        quantity_change INTEGER NOT NULL DEFAULT 0,
        reason          TEXT,
        updated_by      INTEGER REFERENCES users(id) ON DELETE SET NULL,
        updated_at      TEXT NOT NULL DEFAULT (datetime('now','localtime'))
    );

    CREATE TABLE IF NOT EXISTS settings (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        key        TEXT NOT NULL UNIQUE,
        value      TEXT,
        updated_at TEXT NOT NULL DEFAULT (datetime('now','localtime'))
    );

    CREATE TABLE IF NOT EXISTS activity_logs (
        id        INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id   INTEGER REFERENCES users(id) ON DELETE SET NULL,
        action    TEXT NOT NULL,
        details   TEXT,
        timestamp TEXT NOT NULL DEFAULT (datetime('now','localtime'))
    );
    """)

    conn.commit()

    _upgrade_existing_tables(conn)
    _seed_users(conn)
    _seed_settings(conn)
    _seed_brands(conn)

    conn.close()
    log.info("Database migrations complete.")


def _seed_users(conn):
    c = conn.cursor()
    default_users = [
        ("Khudada Khan", "khudada", "admin123", "Admin"),
        ("Hamza Ali",    "hamza",   "admin123", "Admin"),
        ("Waseem Ahmad", "waseem",  "admin123", "Admin"),
    ]
    for name, username, password, role in default_users:
        c.execute("SELECT id FROM users WHERE username = ?", (username,))
        if not c.fetchone():
            c.execute(
                "INSERT INTO users (name, username, password_hash, role) VALUES (?, ?, ?, ?)",
                (name, username, _hash_password(password), role)
            )
            log.info(f"Seeded user: {username}")
    conn.commit()


def _seed_settings(conn):
    c = conn.cursor()
    defaults = {
        "shop_name": "Jadeed Zarai Markaz",
        "shop_address": "Main Bazar, Pakistan",
        "shop_phone": "",
        "invoice_footer": "Thank you for your business!",
        "theme": "light",
        "auto_backup": "0",
        "low_stock_alert": "1",
    }
    for key, value in defaults.items():
        c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (key, value))
    conn.commit()


def _seed_brands(conn):
    c = conn.cursor()
    for brand in DEFAULT_BRANDS:
        c.execute("INSERT OR IGNORE INTO brands (name) VALUES (?)", (brand,))
    conn.commit()
