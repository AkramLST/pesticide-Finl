import os
from pathlib import Path

# =========================
# Application Information
# =========================

APP_NAME = "Jadeed Zarai Markaz"
APP_VERSION = "1.0.0"

# =========================
# Application Data Folder
# =========================

APP_DATA_DIR = Path.home() / "JadeedZaraiMarkaz"

APP_DATA_DIR.mkdir(parents=True, exist_ok=True)

# =========================
# Database
# =========================

DB_PATH = str(APP_DATA_DIR / "pesticide.db")

# =========================
# Directories
# =========================

ASSETS_DIR = str(APP_DATA_DIR / "assets")
IMAGES_DIR = str(APP_DATA_DIR / "images")
EXPORTS_DIR = str(APP_DATA_DIR / "exports")
INVOICES_DIR = str(Path(EXPORTS_DIR) / "invoices")
BACKUPS_DIR = str(APP_DATA_DIR / "backups")
LOGS_DIR = str(APP_DATA_DIR / "logs")

for directory in (
    ASSETS_DIR,
    IMAGES_DIR,
    EXPORTS_DIR,
    INVOICES_DIR,
    BACKUPS_DIR,
    LOGS_DIR,
):
    os.makedirs(directory, exist_ok=True)

# =========================
# Theme Colors
# =========================

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

# =========================
# Payment Methods
# =========================

PAYMENT_METHODS = [
    "Cash",
    "Bank Transfer",
    "EasyPaisa",
    "JazzCash",
    "Cheque",
    "Other",
]

# =========================
# Product Data
# =========================

PRODUCT_MAIN_CATEGORIES = ["Seeds", "Fertilizers", "Pesticides"]

PRODUCT_SUBCATEGORIES = {
    "Seeds": [
        "Wheat", "Corn", "Rice", "Cotton", "Sunflower", "Mustard",
        "Vegetable Seeds", "Fruit Seeds", "Bajra", "Mung Bean", "Sesame",
        "Barley", "Canola", "Fodder Seeds", "Hybrid Seeds", "Other",
    ],
    "Fertilizers": [
        "Urea", "DAP", "NPK", "SOP", "MOP", "Ammonium Sulphate",
        "Zinc Fertilizer", "Micronutrients", "Compost", "Borax",
        "Gypsum", "Calcium Nitrate", "Other",
    ],
    "Pesticides": [
        "Insecticide", "Herbicide", "Fungicide", "Rodenticide",
        "Termiticide", "Plant Growth Regulator", "Bio Pesticide",
        "Acaricide", "Nematicide", "Molluscicide", "Other",
    ],
}

PRODUCT_CATEGORIES = PRODUCT_MAIN_CATEGORIES

DEFAULT_BRANDS = [
    "Bayer", "Syngenta", "FMC", "Corteva", "UPL", "Adama",
    "Nufarm", "Arysta", "Sygenta", "BASF", "Other",
]

PRODUCT_BRANDS = DEFAULT_BRANDS

FORMULATIONS = [
    "Liquid",
    "Powder",
    "Granules",
    "Spray",
    "Tablet",
    "Other",
]

# =========================
# Users & Roles
# =========================

USER_ROLES = [
    "Admin",
    "Manager",
    "Staff",
]

ADMIN_USERS = [
    "khudada",
    "hamza",
    "waseem",
]

# =========================
# Pagination
# =========================

PAGINATION_SIZE = 20
