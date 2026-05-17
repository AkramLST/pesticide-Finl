import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

APP_NAME = "Jadeed Zarai Markaz"
APP_VERSION = "1.0.0"

DB_PATH = os.path.join(BASE_DIR, "database", "pesticide.db")

ASSETS_DIR = os.path.join(BASE_DIR, "assets")
IMAGES_DIR = os.path.join(BASE_DIR, "images")
EXPORTS_DIR = os.path.join(BASE_DIR, "exports")
INVOICES_DIR = os.path.join(EXPORTS_DIR, "invoices")
BACKUPS_DIR = os.path.join(BASE_DIR, "backups")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

for _dir in (EXPORTS_DIR, INVOICES_DIR, BACKUPS_DIR, LOGS_DIR):
    os.makedirs(_dir, exist_ok=True)

COLORS = {
    "primary": "#2e7d32",
    "primary_dark": "#1b5e20",
    "primary_light": "#4caf50",
    "sidebar_bg": "#1f2933",
    "sidebar_hover": "#2d3748",
    "accent": "#3b82f6",
    "danger": "#e53e3e",
    "warning": "#f6ad55",
    "success": "#48bb78",
    "white": "#ffffff",
    "bg_light": "#f7fafc",
    "text_dark": "#1a202c",
    "text_muted": "#718096",
    "border": "#e2e8f0",
}

PAYMENT_METHODS = ["Cash", "Bank Transfer", "EasyPaisa", "JazzCash"]

PRODUCT_CATEGORIES = ["Insecticide", "Herbicide", "Fungicide", "Rodenticide", "Fertilizer", "Other"]

PRODUCT_BRANDS = ["Bayer", "Syngenta", "FMC", "Corteva", "UPL", "Adama", "Other"]

FORMULATIONS = ["Liquid", "Powder", "Granules", "Spray", "Tablet", "Other"]

USER_ROLES = ["Admin", "Manager", "Staff"]

ADMIN_USERS = ["khudada", "hamza", "waseem"]

PAGINATION_SIZE = 20
