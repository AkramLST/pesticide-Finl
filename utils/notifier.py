"""
Notification queue and helpers.
Collects alerts (low stock, expiring, pending payments) and
exposes them to the TopBar bell widget.
"""
from database.connection import get_connection
from utils.helpers import is_expired, is_expiring_soon


def get_notifications() -> list[dict]:
    """Return list of {type, message, severity} dicts."""
    notes = []

    conn = get_connection()

    # Low stock / out of stock
    rows = conn.execute(
        "SELECT name, quantity, low_stock_threshold FROM products "
        "WHERE is_active=1 AND quantity <= low_stock_threshold"
    ).fetchall()
    for r in rows:
        if r["quantity"] == 0:
            notes.append({
                "type": "stock",
                "message": f"Out of stock: {r['name']}",
                "severity": "critical",
            })
        else:
            notes.append({
                "type": "stock",
                "message": f"Low stock: {r['name']} ({r['quantity']} left)",
                "severity": "warning",
            })

    # Expired / expiring soon
    rows = conn.execute(
        "SELECT name, expiry_date FROM products WHERE is_active=1 AND expiry_date IS NOT NULL"
    ).fetchall()
    for r in rows:
        exp = r["expiry_date"]
        if is_expired(exp):
            notes.append({
                "type": "expiry",
                "message": f"Expired: {r['name']} (exp. {exp})",
                "severity": "critical",
            })
        elif is_expiring_soon(exp):
            notes.append({
                "type": "expiry",
                "message": f"Expiring soon: {r['name']} (exp. {exp})",
                "severity": "warning",
            })

    # Pending customer payments
    rows = conn.execute(
        "SELECT name, total_pending FROM customers "
        "WHERE is_active=1 AND total_pending > 0"
    ).fetchall()
    for r in rows:
        from utils.helpers import format_currency
        notes.append({
            "type": "payment",
            "message": f"Pending: {r['name']} owes {format_currency(r['total_pending'])}",
            "severity": "info",
        })

    conn.close()
    return notes


def log_activity(user_id: int, action: str, details: str = ""):
    """Write a record to activity_logs."""
    conn = get_connection()
    conn.execute(
        "INSERT INTO activity_logs (user_id, action, details) VALUES (?, ?, ?)",
        (user_id, action, details)
    )
    conn.commit()
    conn.close()
