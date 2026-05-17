from datetime import datetime, date


def format_currency(amount: float) -> str:
    """Format a float as Pakistani Rupee string."""
    return f"Rs {amount:,.2f}"


def format_date(d) -> str:
    """Convert date/datetime/string to display format DD-MM-YYYY."""
    if d is None:
        return ""
    if isinstance(d, (datetime, date)):
        return d.strftime("%d-%m-%Y")
    try:
        return datetime.strptime(str(d), "%Y-%m-%d").strftime("%d-%m-%Y")
    except ValueError:
        return str(d)


def format_datetime(dt) -> str:
    """Convert datetime/string to display format DD-MM-YYYY HH:MM."""
    if dt is None:
        return ""
    if isinstance(dt, datetime):
        return dt.strftime("%d-%m-%Y %H:%M")
    try:
        return datetime.strptime(str(dt), "%Y-%m-%d %H:%M:%S").strftime("%d-%m-%Y %H:%M")
    except ValueError:
        return str(dt)


def generate_invoice_number() -> str:
    """Generate a time-based invoice number: INV-YYYYMMDD-HHMMSS."""
    return f"INV-{datetime.now().strftime('%Y%m%d-%H%M%S')}"


def is_expiring_soon(expiry_date_str: str, days: int = 30) -> bool:
    """Return True if product expires within `days` days."""
    if not expiry_date_str:
        return False
    try:
        exp = datetime.strptime(str(expiry_date_str), "%Y-%m-%d").date()
        return 0 <= (exp - date.today()).days <= days
    except ValueError:
        return False


def is_expired(expiry_date_str: str) -> bool:
    """Return True if product has already expired."""
    if not expiry_date_str:
        return False
    try:
        exp = datetime.strptime(str(expiry_date_str), "%Y-%m-%d").date()
        return exp < date.today()
    except ValueError:
        return False


def truncate_text(text: str, max_len: int = 40) -> str:
    """Truncate text and add ellipsis if too long."""
    return text if len(text) <= max_len else text[:max_len - 3] + "..."
