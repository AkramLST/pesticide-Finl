# Jadeed Zarai Markaz — Pesticide ERP Desktop App

A fully-featured desktop ERP application for pesticide retail management, built with Python 3.12 + PySide6.

---

## Features

| Module | Features |
|---|---|
| **Dashboard** | Live stats, revenue chart, low-stock alerts, recent sales |
| **Products** | Card grid, add/edit/delete, sell dialog, PDF invoice on sale |
| **Inventory** | Filterable table (category/supplier/stock/expiry), pagination, bulk qty update, Export Excel/PDF |
| **Sales** | Full sales history, payment recording, invoice PDF view/reprint, Export Excel/PDF |
| **Customers** | CRUD, purchase history popup, partial payment dialog, customer statement PDF |
| **Suppliers** | CRUD, view products by supplier |
| **Users** | Add/edit/reset-password/toggle-active, role management (Admin/Manager/Staff) |
| **Reports** | Sales report, Profit/Loss by product, Customer Dues, Inventory snapshot — all with Export PDF/Excel |
| **Settings** | Shop info, invoice settings, profile edit, theme toggle (light/dark), DB backup/restore, notification prefs, activity log viewer |

---

## Setup

### 1. Clone / unzip the project

```
cd pesticide-Finl
```

### 2. Create a virtual environment

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run

```bash
python main.py
```

### Default login credentials

| Username | Password | Role |
|---|---|---|
| `khudada` | `admin123` | Admin |
| `hamza` | `admin123` | Admin |
| `waseem` | `admin123` | Admin |

---

## Project Structure

```
pesticide-Finl/
├── main.py                  # Entry point
├── requirements.txt
├── assets/
│   └── styles/
│       ├── light.qss        # Light theme stylesheet
│       └── dark.qss         # Dark theme stylesheet
├── database/
│   ├── connection.py
│   ├── migrations.py        # Schema creation + seeding
│   └── pesticide.db         # SQLite database (auto-created)
├── models/                  # DB access layer
├── services/
│   ├── invoice_service.py   # PDF invoice generation
│   └── export_service.py    # Excel/PDF export for all pages
├── pages/
│   ├── dashboard/
│   ├── products/
│   ├── inventory/
│   ├── sales/
│   ├── customers/
│   ├── suppliers/
│   ├── users/
│   ├── reports/
│   └── settings/
├── ui/
│   ├── main_window.py
│   ├── topbar.py            # Notification bell + user chip
│   └── login_window.py
├── widgets/
│   └── sidebar.py
├── utils/
│   ├── config.py            # Paths, constants
│   ├── helpers.py           # Format helpers
│   ├── session.py           # Singleton login session
│   ├── notifier.py          # Notification queries
│   └── theme.py             # Light/dark QSS switcher
├── exports/                 # Generated Excel, PDF exports
├── backups/                 # Manual DB backups
└── logs/
```

---

## Build (Windows Executable)

```bash
pip install pyinstaller
pyinstaller build.spec
```

Output will be in `dist/JadeedZaraiMarkaz/`.

---

## Tech Stack

- **Python** 3.12
- **PySide6** 6.11.1 — UI framework
- **SQLite** — embedded database
- **reportlab** — PDF generation
- **openpyxl** — Excel export
- **matplotlib** — Dashboard charts
