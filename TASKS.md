# Pesticide Management System — Task List

> **Project:** Jadeed Zarai Markaz — Desktop ERP  
> **Stack:** Python 3.12 · PySide6 · SQLite · reportlab (PDF)  
> **Status legend:** `[ ]` pending · `[~]` in progress · `[x]` done

---

## 0. Current State (Already Exists)

- [x] `main.py` — entry point, calls `create_tables()`, launches `LoginWindow`
- [x] `ui/login_window.py` — basic login (hardcoded `dmin` / `234`)
- [x] `ui/dashboard_window.py` — main shell with sidebar + stacked pages
- [x] `ui/sidebar.py` — 5 buttons (dashboard, products, inventory, sales, suppliers)
- [x] `ui/topbar.py` — logo, title, username
- [x] `database/db.py` — SQLite connection, `products` table only
- [x] `modules/dashboard/dashboard_page.py` — static cards (hardcoded values)
- [x] `modules/products/product_page.py` — grid of product cards
- [x] `modules/products/add_product.py` — add product dialog
- [x] `modules/products/product_card.py` — individual card widget
- [x] `modules/inventory/stock_page.py` — basic stock/inventory page
- [x] `modules/sales/sales_page.py` — basic sales page
- [x] `modules/suppliers/supplier_page.py` — basic suppliers page

---

## 1. Project Restructure & Architecture

### 1.1 Folder Structure
- [ ] Create folders: `assets/`, `pages/`, `widgets/`, `dialogs/`, `controllers/`, `models/`, `services/`, `utils/`, `reports/`, `exports/`, `backups/`
- [ ] Move existing UI files into correct folders:
  - `ui/login_window.py` → `pages/login_page.py`
  - `ui/dashboard_window.py` → `ui/main_window.py`
  - `ui/sidebar.py` → `widgets/sidebar.py`
  - `ui/topbar.py` → `widgets/topbar.py`
  - `modules/*/` → `pages/*/`
- [ ] Add `__init__.py` where needed
- [ ] Update all imports after restructure

### 1.2 Config / Constants
- [ ] Create `utils/config.py` — app name, version, DB path, color palette, default credentials
- [ ] Create `utils/logger.py` — file + console logging using Python `logging` module
- [ ] Create `utils/helpers.py` — shared utility functions (date formatting, currency formatting, etc.)

### 1.3 DB Abstraction Layer
- [ ] Refactor `database/db.py` into `database/connection.py` (pure connection, path-configurable)
- [ ] Create `models/` files, one per table — each model wraps CRUD queries for its table
- [ ] Ensure all queries use parameterized statements (no string interpolation)
- [ ] Add `database/migrations.py` — version-aware schema migration runner

---

## 2. Database Design

### 2.1 Schema — Create All Tables
- [ ] `users` table
  ```sql
  id, name, username, password_hash, role, phone, email, profile_image, last_login, is_active, created_at, updated_at
  ```
- [ ] `products` table (extend existing)
  ```sql
  id, name, description, brand, category, formulation, purchase_price, sale_price,
  quantity, unit_type, weight, supplier_id(FK), manufacturing_date, expiry_date,
  low_stock_threshold, image, barcode, is_active, created_at, updated_at
  ```
- [ ] `inventory` table
  ```sql
  id, product_id(FK), quantity_change, reason, updated_by(FK users), updated_at
  ```
- [ ] `customers` table
  ```sql
  id, name, phone, address, notes, total_purchases, total_paid, total_pending,
  last_purchase_date, is_active, created_at, updated_at
  ```
- [ ] `suppliers` table
  ```sql
  id, name, phone, email, address, notes, total_transactions, is_active, created_at, updated_at
  ```
- [ ] `sales` table
  ```sql
  id, invoice_number, customer_id(FK), sold_by(FK users), sale_date,
  total_amount, discount, paid_amount, remaining_amount, payment_method,
  notes, created_at
  ```
- [ ] `sale_items` table
  ```sql
  id, sale_id(FK), product_id(FK), quantity, unit_price, discount, subtotal
  ```
- [ ] `payments` table
  ```sql
  id, sale_id(FK), customer_id(FK), amount_paid, payment_method, payment_date, notes
  ```
- [ ] `invoices` table
  ```sql
  id, sale_id(FK), invoice_path, generated_at
  ```
- [ ] `settings` table
  ```sql
  id, key, value, updated_at
  ```
- [ ] `activity_logs` table
  ```sql
  id, user_id(FK), action, details, timestamp
  ```

### 2.2 Seed Data
- [ ] Seed 3 default users: `khudada`, `hamza`, `waseem` (role: admin)
- [ ] Seed default settings (shop name, address, invoice footer)

---

## 3. Authentication

### 3.1 Login Page Improvements
- [ ] Replace hardcoded credentials with DB lookup (`users` table)
- [ ] Hash passwords with `bcrypt` or `hashlib` (SHA-256 + salt)
- [ ] Add password visibility toggle button (eye icon)
- [ ] Add "Remember me" checkbox (save username in settings)
- [ ] Improve error messages (distinguish wrong username vs wrong password)
- [ ] Add login attempt limit / lockout after 5 failed attempts
- [ ] Store logged-in user in a session object (`utils/session.py`)

### 3.2 Session Management
- [ ] Create `utils/session.py` — singleton holding current user info
- [ ] Pass session to all pages that need user context (e.g., sales page "sold by")
- [ ] Show current user name + role in TopBar
- [ ] Add logout button in TopBar → clears session, returns to login

---

## 4. Sidebar & Navigation

### 4.1 Updated Menu Items (8 items)
- [ ] Add: **Customers** (index 4)
- [ ] Add: **Users** (index 6)
- [ ] Add: **Settings** (index 7)
- [ ] Update `dashboard_window.py` `pages` dict to map all 8 pages

### 4.2 Sidebar Enhancements
- [ ] Add icon (SVG/PNG) for each menu item
- [ ] Active page highlighting (different background + color)
- [ ] Hover animation (smooth color transition via QPropertyAnimation)
- [ ] Collapsible sidebar toggle button (show icons only when collapsed)
- [ ] Store collapse state preference

### 4.3 Page Transitions
- [ ] Add smooth fade/slide animation when switching pages using `QPropertyAnimation`

---

## 5. Dashboard Page

### 5.1 Live Stats Cards (replace hardcoded)
- [ ] Total Products — query `products` table
- [ ] Total Inventory Items — query `inventory`
- [ ] Total Sales Amount — query `sales`
- [ ] Total Sold Items — sum `sale_items.quantity`
- [ ] Pending Payments — sum `sales.remaining_amount > 0`
- [ ] Sales This Week — filter `sales.sale_date >= monday`
- [ ] Most Sold Product — GROUP BY product_id ORDER BY COUNT DESC LIMIT 1
- [ ] Total Customers — query `customers`
- [ ] Total Suppliers — query `suppliers`
- [ ] Low Stock Alerts — products where `quantity <= low_stock_threshold`

### 5.2 Charts
- [ ] Install `matplotlib` — add to requirements
- [ ] Weekly sales bar chart (last 7 days)
- [ ] Monthly revenue line chart (last 12 months)
- [ ] Top 5 selling products horizontal bar chart
- [ ] Inventory status pie chart (in stock / low stock / out of stock)
- [ ] Embed charts in dashboard using `FigureCanvasQTAgg`

### 5.3 Dashboard Tables
- [ ] Recent 5 sales table (invoice #, customer, amount, date)
- [ ] Recent 5 added products table
- [ ] Pending payments table (customer, amount due)

### 5.4 Low Stock Alert Banner
- [ ] Show red alert banner at top if any product is below threshold

---

## 6. Products Page

### 6.1 Top Bar
- [ ] Search bar (real-time filter on product name/brand/category)
- [ ] "Add Product" button
- [ ] "Export Products" button (CSV/Excel)
- [ ] "Refresh" button
- [ ] Category filter dropdown
- [ ] Supplier filter dropdown

### 6.2 Product Card Improvements
- [ ] Show: image, name, brand, category, quantity, sale price, supplier, expiry date, stock status badge
- [ ] Stock status badge: **In Stock** (green) / **Low Stock** (orange) / **Out of Stock** (red)
- [ ] Card actions: **Edit**, **Delete**, **Sell** buttons
- [ ] Image placeholder if no image set

### 6.3 Add Product Dialog
- [ ] Image upload with preview
- [ ] All fields: name, brand, category, supplier (dropdown), purchase price, sale price, quantity, unit type, manufacturing date, expiry date, description, low stock threshold
- [ ] Auto-generate product ID
- [ ] Duplicate product name prevention
- [ ] Input validation (required fields, numeric checks, date logic)
- [ ] QDateEdit for date fields

### 6.4 Edit Product Dialog
- [ ] Pre-fill all fields from existing product
- [ ] Same validation as Add
- [ ] Update DB on save

### 6.5 Sell Product Dialog
- [ ] Open from product card "Sell" button
- [ ] **Product info section:** name, available qty, unit price (read-only)
- [ ] **Sale fields:** qty to sell, discount %, total amount (auto-calculated), amount paid, remaining (auto-calculated), payment method (Cash / Bank Transfer / EasyPaisa / JazzCash)
- [ ] **Customer section — two tabs/options:**
  - Existing Customer: searchable dropdown, auto-load details
  - New Customer: name, phone, address, notes (auto-save to customers table)
- [ ] On confirm:
  1. Validate stock >= qty requested
  2. Deduct from `products.quantity` + insert `inventory` log row
  3. Insert `sales` record
  4. Insert `sale_items` record
  5. Insert/update `customers` record
  6. If remaining > 0, insert `payments` pending record
  7. Generate PDF invoice
  8. Open print dialog
  9. Save PDF to `exports/invoices/`
- [ ] Show success message with invoice number

### 6.6 PDF Invoice
- [ ] Use `reportlab` library
- [ ] Invoice layout: shop logo, shop name, invoice #, date/time, customer details, product table (name, qty, unit price, discount, subtotal), totals section (subtotal, discount, grand total, paid, remaining), payment method, seller name, footer text
- [ ] Save to `exports/invoices/INV-{number}.pdf`

---

## 7. Inventory Page

### 7.1 Table Columns
- [ ] Product ID, image thumbnail, name, category, supplier, quantity, purchase price, sale price, expiry date, stock status, last updated

### 7.2 Filters
- [ ] Search by product name
- [ ] Filter by category
- [ ] Filter by supplier
- [ ] Filter by expiry status (expired / expiring soon / valid)
- [ ] Low stock only toggle
- [ ] Date range (last updated)

### 7.3 Features
- [ ] Sortable column headers (click to sort ASC/DESC)
- [ ] Pagination (e.g., 20 rows per page, prev/next buttons)
- [ ] Row color coding: red for expired, orange for low stock
- [ ] Export to Excel (`openpyxl`) and PDF (`reportlab`)
- [ ] Bulk quantity update dialog (select multiple rows → set new qty)

---

## 8. Sales Page

### 8.1 Sales Table Columns
- [ ] Invoice ID, customer name, product name, quantity, unit price, discount, total, paid, remaining, payment method, sale date, sold by

### 8.2 Features
- [ ] Search by invoice # or customer name
- [ ] Date range filter
- [ ] Filter by payment method
- [ ] Filter by sold by (khudada / hamza / waseem)
- [ ] Export to PDF / Excel
- [ ] View invoice button → open PDF
- [ ] Reprint invoice button
- [ ] Edit sale record dialog
- [ ] Delete sale record (confirm dialog, soft delete)

---

## 9. Customers Page

### 9.1 Customer Table Columns
- [ ] Customer ID, name, phone, address, total items purchased, total amount, total paid, total pending, last purchase date

### 9.2 Features
- [ ] Add customer dialog (name, phone, address, notes)
- [ ] Edit customer dialog
- [ ] Delete customer (soft delete)
- [ ] Search/filter by name or phone
- [ ] View purchase history (popup table of all sales for this customer)
- [ ] Customer statement PDF (all transactions, totals, dues)
- [ ] Add partial payment dialog
- [ ] Mark payment as fully paid

---

## 10. Suppliers Page

### 10.1 Supplier Table Columns
- [ ] Supplier ID, name, phone, email, address, products supplied count, total transactions

### 10.2 Features
- [ ] Add supplier dialog (name, phone, email, address, notes)
- [ ] Edit supplier dialog
- [ ] Delete supplier (soft delete, prevent if linked products exist)
- [ ] View products supplied by this supplier
- [ ] View purchase history from this supplier
- [ ] Pending supplier payments section

---

## 11. Users Page

### 11.1 User Table Columns
- [ ] User image, name, username, role, phone, email, last login, account status (active/inactive)

### 11.2 Features
- [ ] Add user dialog (image upload, name, username, password, role, phone, email)
- [ ] Edit user dialog
- [ ] Delete user (cannot delete logged-in user)
- [ ] Reset password dialog
- [ ] Toggle account active/inactive
- [ ] Role selection: Admin / Manager / Staff

---

## 12. Settings Page

### 12.1 Profile Settings
- [ ] Upload/change profile image
- [ ] Change name
- [ ] Change username (validate uniqueness)
- [ ] Change password (require current password confirmation)
- [ ] Update phone number
- [ ] Update email

### 12.2 Shop Settings
- [ ] Shop logo upload (used in invoices)
- [ ] Shop name
- [ ] Address
- [ ] Contact number
- [ ] Invoice footer text

### 12.3 Application Settings
- [ ] Theme toggle: Light / Dark mode (apply QSS globally)
- [ ] Language placeholder (English only for now, structure for i18n later)
- [ ] Manual DB backup — copy `pesticide.db` to `backups/` with timestamp
- [ ] Restore DB — browse for backup file and replace current DB
- [ ] Auto backup toggle + interval (daily/weekly)
- [ ] Notification preferences (low stock alert, pending payments alert)

---

## 13. Notifications System

- [ ] Create `utils/notifier.py` — notification queue
- [ ] Show notification toast (top-right overlay) for:
  - Low stock products
  - Expired / expiring-soon products
  - Pending customer payments
  - Successful sale
- [ ] Notification bell icon in TopBar with unread count badge
- [ ] Notification dropdown panel listing unread alerts

---

## 14. Reporting Module

- [ ] Daily sales report (PDF) — all sales for a selected date
- [ ] Monthly sales report (PDF) — by month, grouped by product
- [ ] Profit/loss report — (sale price - purchase price) × qty sold
- [ ] Inventory report — current stock levels, low stock items
- [ ] Customer dues report — all customers with pending > 0
- [ ] Reports page in UI with date pickers and "Generate" buttons

---

## 15. Activity Logs

- [ ] Log every: login, logout, product add/edit/delete, sale create/edit/delete, payment, user change
- [ ] Store in `activity_logs` table
- [ ] Activity log viewer in Settings or Users page (filterable by user, action type, date)

---

## 16. Backup System

- [ ] Manual backup button in Settings → saves `database/pesticide.db` → `backups/backup_YYYYMMDD_HHMMSS.db`
- [ ] Auto backup via `QTimer` on app start (if auto backup enabled in settings)
- [ ] Restore: file picker → confirm dialog → replace DB → restart prompt

---

## 17. UI / UX Polish

### 17.1 Global Stylesheet (QSS)
- [ ] Create `assets/styles/light.qss` and `assets/styles/dark.qss`
- [ ] Apply globally from `main.py` based on settings
- [ ] Colors: green `#2e7d32`, dark gray `#1f2933`, white `#ffffff`, accent blue `#3b82f6`

### 17.2 Reusable Widgets
- [ ] `widgets/stat_card.py` — dashboard stat tile
- [ ] `widgets/data_table.py` — sortable, paginated QTableWidget wrapper
- [ ] `widgets/search_bar.py` — styled search input with clear button
- [ ] `widgets/confirm_dialog.py` — reusable yes/no confirmation popup
- [ ] `widgets/toast_notification.py` — animated overlay notification
- [ ] `widgets/image_picker.py` — click-to-upload image widget with preview

### 17.3 Animations
- [ ] Sidebar collapse/expand via `QPropertyAnimation` on `maximumWidth`
- [ ] Page fade transition via `QGraphicsOpacityEffect` + `QPropertyAnimation`
- [ ] Button hover press effect

---

## 18. Code Quality

- [ ] Add docstrings to all classes and public methods
- [ ] Consistent naming: `snake_case` for variables/functions, `PascalCase` for classes
- [ ] No hardcoded strings — use constants from `utils/config.py`
- [ ] Remove all placeholder/dummy data from pages
- [ ] Add `requirements.txt`:
  ```
  PySide6>=6.6.0
  reportlab>=4.0.0
  openpyxl>=3.1.0
  matplotlib>=3.8.0
  bcrypt>=4.0.0
  ```
- [ ] Add `README.md` with setup and run instructions

---

## 19. Build & Distribution

- [ ] Add `build.spec` for PyInstaller
- [ ] Test frozen executable on Windows
- [ ] Bundle assets (images, QSS) into executable
- [ ] Create installer with NSIS or Inno Setup (optional)

---

## Priority Build Order

| Phase | Tasks | Goal |
|-------|-------|------|
| **Phase 1** | Tasks 1, 2, 3 | Clean architecture + full DB schema + real auth |
| **Phase 2** | Tasks 4, 5 | Sidebar with all 8 pages + live dashboard |
| **Phase 3** | Tasks 6 | Full products page with sell + PDF invoice |
| **Phase 4** | Tasks 7, 8 | Inventory + Sales pages with export |
| **Phase 5** | Tasks 9, 10 | Customers + Suppliers pages |
| **Phase 6** | Tasks 11, 12 | Users + Settings pages |
| **Phase 7** | Tasks 13–16 | Notifications, reports, logs, backup |
| **Phase 8** | Tasks 17, 18 | UI polish + code quality |
| **Phase 9** | Task 19 | Build & distribute |
