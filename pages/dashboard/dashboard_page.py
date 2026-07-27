from datetime import datetime

from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame,
    QSizePolicy, QGraphicsDropShadowEffect, QScrollArea,
    QTableWidget, QTableWidgetItem, QHeaderView, QPushButton,
    QGridLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from database.connection import get_connection
from utils.helpers import format_currency, format_datetime


class DashboardPage(QWidget):

    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("background:#f1f5f9;")
        self._cards = []
        self._build_ui()
        self.refresh()

    def showEvent(self, event):
        super().showEvent(event)
        if hasattr(self, "_stats_ready"):
            self.refresh()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        header = QFrame()
        header.setFixedHeight(64)
        header.setAttribute(Qt.WA_StyledBackground, True)
        header.setStyleSheet("QFrame{background:white;border-bottom:1.5px solid #e2e8f0;}")
        hl = QHBoxLayout(header)
        hl.setContentsMargins(24, 0, 24, 0)

        title = QLabel("Dashboard")
        title.setStyleSheet("font-size:20px;font-weight:700;color:#0f172a;")

        refresh_btn = QPushButton("↻  Refresh")
        refresh_btn.setFixedSize(110, 36)
        refresh_btn.setStyleSheet(
            "QPushButton{background:#2e7d32;color:white;border-radius:8px;"
            "font-size:13px;font-weight:600;border:none;}"
            "QPushButton:hover{background:#1b5e20;}"
        )
        refresh_btn.clicked.connect(self.refresh)

        hl.addWidget(title)
        hl.addStretch()
        hl.addWidget(refresh_btn)
        outer.addWidget(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background:#f1f5f9;border:none;")

        self.content = QWidget()
        self.content.setStyleSheet("background:#f1f5f9;")
        self.root = QVBoxLayout(self.content)
        self.root.setContentsMargins(20, 16, 20, 20)
        self.root.setSpacing(16)

        self._low_stock_banner = self._make_banner()
        self.root.addWidget(self._low_stock_banner)

        self.cards_grid = QGridLayout()
        self.cards_grid.setSpacing(12)
        self.root.addLayout(self.cards_grid)

        self.overview_card, self.overview_layout = self._make_section("Business Overview")
        self.root.addWidget(self.overview_card)

        self.category_card, self.category_layout = self._make_section("Category-wise Statistics")
        self.root.addWidget(self.category_card)

        charts_row = QHBoxLayout()
        charts_row.setSpacing(14)
        self.inventory_card, self.inventory_layout = self._make_section("Inventory Snapshot")
        self.recent_card, self.recent_layout = self._make_section("Recent Sales")
        charts_row.addWidget(self.inventory_card, stretch=2)
        charts_row.addWidget(self.recent_card, stretch=3)
        self.root.addLayout(charts_row)

        bottom = QHBoxLayout()
        bottom.setSpacing(14)
        self.customers_card, self.customers_layout = self._make_section("Customer Balances")
        self.suppliers_card, self.suppliers_layout = self._make_section("Supplier Balances")
        bottom.addWidget(self.customers_card, stretch=1)
        bottom.addWidget(self.suppliers_card, stretch=1)
        self.root.addLayout(bottom)

        self.root.addStretch()
        scroll.setWidget(self.content)
        outer.addWidget(scroll)

        self._stats_ready = True

    def _make_banner(self):
        banner = QFrame()
        banner.setAttribute(Qt.WA_StyledBackground, True)
        banner.setStyleSheet(
            "QFrame{background:#fffbeb;border:1.5px solid #f59e0b;border-radius:10px;}"
        )
        layout = QHBoxLayout(banner)
        layout.setContentsMargins(14, 8, 14, 8)
        self.banner_label = QLabel("Low stock items will appear here.")
        self.banner_label.setStyleSheet("font-size:13px;color:#92400e;")
        layout.addWidget(self.banner_label)
        layout.addStretch()
        return banner

    def _make_section(self, title: str):
        card = QFrame()
        card.setAttribute(Qt.WA_StyledBackground, True)
        card.setStyleSheet("QFrame{background:white;border-radius:14px;border:1px solid #e2e8f0;}")
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(16)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 22))
        card.setGraphicsEffect(shadow)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(10)

        heading = QLabel(title)
        heading.setStyleSheet("font-size:15px;font-weight:700;color:#0f172a;")
        layout.addWidget(heading)
        return card, layout

    def _make_card(self, title: str, value: str, accent: str, bg1: str, bg2: str):
        card = QFrame()
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        card.setFixedHeight(98)
        card.setAttribute(Qt.WA_StyledBackground, True)
        card.setStyleSheet(
            f"QFrame{{background:qlineargradient(x1:0,y1:0,x2:1,y2:1,"
            f"stop:0 {bg1}, stop:1 {bg2});border-radius:14px;border:1.5px solid {accent}33;}}"
        )

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(16)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 28))
        card.setGraphicsEffect(shadow)

        layout = QHBoxLayout(card)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(14)

        icon_lbl = QLabel("●")
        icon_lbl.setFixedSize(48, 48)
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setStyleSheet(f"background:{accent}22;border-radius:12px;color:{accent};font-size:22px;")

        text_col = QVBoxLayout()
        text_col.setSpacing(2)
        val_lbl = QLabel(value)
        val_lbl.setStyleSheet(f"font-size:24px;font-weight:800;color:{accent};")
        ttl_lbl = QLabel(title)
        ttl_lbl.setStyleSheet("font-size:12px;color:#64748b;font-weight:500;")
        text_col.addWidget(val_lbl)
        text_col.addWidget(ttl_lbl)

        layout.addWidget(icon_lbl)
        layout.addLayout(text_col)
        layout.addStretch()
        self._cards.append((val_lbl, title))
        return card

    def _query_one(self, sql: str, params=()):
        conn = get_connection()
        try:
            row = conn.execute(sql, params).fetchone()
            return dict(row) if row else {}
        finally:
            conn.close()

    def _query_all(self, sql: str, params=()):
        conn = get_connection()
        try:
            rows = conn.execute(sql, params).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def refresh(self):
        stats = self._load_stats()
        self._render_banner(stats["low_stock"])
        self._render_cards(stats)
        self._render_overview(stats)
        self._render_categories(stats["categories"])
        self._render_inventory(stats)
        self._render_recent_sales(stats["recent_sales"])
        self._render_customer_balances(stats["customers_due"])
        self._render_supplier_balances(stats["suppliers_due"])

    def _render_banner(self, low_stock):
        if low_stock:
            names = ", ".join(item["name"] for item in low_stock[:5])
            suffix = "..." if len(low_stock) > 5 else ""
            self.banner_label.setText(
                f"<b>{len(low_stock)} product(s)</b> are low on stock: {names}{suffix}"
            )
        else:
            self.banner_label.setText("No low-stock alerts right now.")

    def _load_stats(self):
        inventory = self._query_one(
            """
            SELECT
                COALESCE(COUNT(*), 0) AS product_count,
                COALESCE(SUM(CASE WHEN quantity > 0 THEN 1 ELSE 0 END), 0) AS in_stock_products,
                COALESCE(SUM(quantity), 0) AS total_quantity,
                COALESCE(SUM(quantity * purchase_price), 0) AS inventory_value,
                COALESCE(SUM(CASE WHEN quantity > 0 AND quantity <= low_stock_threshold THEN 1 ELSE 0 END), 0) AS low_stock
            FROM products
            WHERE is_active = 1
            """
        )
        sales_items = self._query_one(
            """
            SELECT
                COALESCE(SUM(si.quantity), 0) AS total_sold_qty,
                COALESCE(SUM(si.subtotal), 0) AS total_sold_value,
                COALESCE(SUM(si.subtotal - (COALESCE(p.purchase_price, 0) * si.quantity)), 0) AS total_profit
            FROM sale_items si
            JOIN sales s ON s.id = si.sale_id
            LEFT JOIN products p ON p.id = si.product_id
            WHERE s.is_deleted = 0
            """
        )
        sales_totals = self._query_one(
            """
            SELECT
                COALESCE(SUM(total_amount), 0) AS total_revenue,
                COALESCE(SUM(remaining_amount), 0) AS total_pending
            FROM sales
            WHERE is_deleted = 0
            """
        )
        payments = self._query_one(
            """
            SELECT
                COALESCE(SUM(CASE WHEN sale_id IS NOT NULL THEN amount_paid ELSE 0 END), 0) AS customer_received,
                COALESCE(SUM(CASE WHEN sale_id IS NULL THEN amount_paid ELSE 0 END), 0) AS opening_received
            FROM payments
            """
        )
        customers_due = self._query_all(
            """
            SELECT
                c.id,
                c.name,
                COALESCE(c.opening_balance, 0) AS opening_balance,
                COALESCE((SELECT SUM(amount_paid) FROM payments p WHERE p.customer_id = c.id), 0) AS total_paid,
                COALESCE((SELECT SUM(amount_paid) FROM payments p WHERE p.customer_id = c.id AND p.sale_id IS NULL), 0) AS opening_paid,
                COALESCE((SELECT SUM(remaining_amount) FROM sales s WHERE s.customer_id = c.id AND s.is_deleted = 0), 0) AS sales_pending
            FROM customers c
            WHERE c.is_active = 1
            ORDER BY (opening_balance + sales_pending) DESC, c.name
            """
        )
        suppliers_due = self._query_all(
            """
            SELECT
                s.id,
                s.name,
                COALESCE(s.opening_balance, 0) AS opening_balance,
                COALESCE((SELECT SUM(total_amount) FROM supplier_purchases sp WHERE sp.supplier_id = s.id), 0) AS purchase_total,
                COALESCE((SELECT SUM(amount_paid) FROM supplier_purchases sp WHERE sp.supplier_id = s.id), 0) AS paid_at_purchase,
                COALESCE((SELECT SUM(amount_paid) FROM supplier_payments sp WHERE sp.supplier_id = s.id), 0) AS total_paid
            FROM suppliers s
            WHERE s.is_active = 1
            ORDER BY (opening_balance + purchase_total - paid_at_purchase - total_paid) DESC, s.name
            """
        )
        categories = self._query_all(
            """
            SELECT
                COALESCE(p.category, 'Uncategorized') AS category,
                COUNT(DISTINCT p.id) AS product_count,
                COALESCE(SUM(p.quantity), 0) AS stock_units,
                COALESCE(SUM(p.quantity * p.purchase_price), 0) AS stock_value,
                COALESCE((SELECT SUM(si.quantity)
                          FROM sale_items si JOIN sales s ON s.id=si.sale_id
                          JOIN products sold_p ON sold_p.id=si.product_id
                          WHERE s.is_deleted=0 AND COALESCE(sold_p.category, 'Uncategorized')=COALESCE(p.category, 'Uncategorized')), 0) AS units_sold,
                COALESCE((SELECT SUM(si.subtotal)
                          FROM sale_items si JOIN sales s ON s.id=si.sale_id
                          JOIN products sold_p ON sold_p.id=si.product_id
                          WHERE s.is_deleted=0 AND COALESCE(sold_p.category, 'Uncategorized')=COALESCE(p.category, 'Uncategorized')), 0) AS sales_value
            FROM products p
            WHERE p.is_active=1
            GROUP BY COALESCE(p.category, 'Uncategorized')
            ORDER BY category
            """
        )
        recent_sales = self._query_all(
            """
            SELECT s.id, s.invoice_number, COALESCE(c.name, 'Walk-in') AS customer_name,
                   s.total_amount, s.paid_amount, s.remaining_amount, s.sale_date,
                   COALESCE(u.name, u.username, 'Unknown') AS seller_name
            FROM sales s
            LEFT JOIN customers c ON c.id = s.customer_id
            LEFT JOIN users u ON u.id = s.sold_by
            WHERE s.is_deleted = 0
            ORDER BY datetime(s.sale_date) DESC, s.id DESC
            LIMIT 8
            """
        )
        low_stock = self._query_all(
            """
            SELECT id, name, quantity, low_stock_threshold, purchase_price
            FROM products
            WHERE is_active = 1 AND quantity <= low_stock_threshold
            ORDER BY quantity ASC, name ASC
            LIMIT 10
            """
        )
        return {
            "inventory": inventory,
            "sales": {**sales_items, **sales_totals},
            "payments": payments,
            "customers_due": customers_due,
            "suppliers_due": suppliers_due,
            "categories": categories,
            "recent_sales": recent_sales,
            "low_stock": low_stock,
        }

    def _render_cards(self, stats):
        while self.cards_grid.count():
            item = self.cards_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._cards = []
        cards = [
            ("Products In Stock", str(stats["inventory"].get("in_stock_products", 0)), "#2563eb", "#eff6ff", "#dbeafe"),
            ("Units Available", str(stats["inventory"].get("total_quantity", 0)), "#10b981", "#f0fdf4", "#d1fae5"),
            ("Inventory Value", format_currency(stats["inventory"].get("inventory_value", 0)), "#f59e0b", "#fffbeb", "#fef3c7"),
            ("Products Sold", str(stats["sales"].get("total_sold_qty", 0)), "#8b5cf6", "#f5f3ff", "#ede9fe"),
            ("Total Profit", format_currency(stats["sales"].get("total_profit", 0)), "#2e7d32", "#f0fdf4", "#d1fae5"),
            ("Customer Received", format_currency(stats["payments"].get("customer_received", 0) + stats["payments"].get("opening_received", 0)), "#14b8a6", "#f0fdfa", "#ccfbf1"),
            ("Customer Pending", format_currency(stats["sales"].get("total_pending", 0)), "#ef4444", "#fef2f2", "#fee2e2"),
            ("Supplier Pending", format_currency(self._supplier_pending_total(stats["suppliers_due"])), "#dc2626", "#fef2f2", "#fee2e2"),
        ]
        for idx, (title, value, accent, bg1, bg2) in enumerate(cards):
            self.cards_grid.addWidget(self._make_card(title, value, accent, bg1, bg2), idx // 3, idx % 3)

    def _supplier_pending_total(self, suppliers_due):
        total = 0.0
        for supplier in suppliers_due:
            opening = float(supplier.get("opening_balance", 0) or 0)
            purchases = float(supplier.get("purchase_total", 0) or 0)
            paid = (float(supplier.get("paid_at_purchase", 0) or 0)
                    + float(supplier.get("total_paid", 0) or 0))
            total += max(0.0, opening + purchases - paid)
        return total

    def _render_categories(self, categories):
        while self.category_layout.count() > 1:
            item = self.category_layout.takeAt(1)
            if item.widget():
                item.widget().deleteLater()

        table = QTableWidget()
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels([
            "Category", "Products", "Stock Units", "Stock Value", "Units Sold", "Sales Value"
        ])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setAlternatingRowColors(True)
        table.setShowGrid(False)
        table.setRowCount(len(categories))
        table.setFixedHeight(max(150, min(280, 46 + len(categories) * 38)))
        table.setStyleSheet(
            "QTableWidget{border:none;font-size:13px;background:white;alternate-background-color:#f8fafc;}"
            "QHeaderView::section{background:#f1f5f9;color:#475569;font-weight:700;font-size:12px;padding:8px;border:none;}"
            "QTableWidget::item{padding:8px;color:#1e293b;}"
        )
        for row, category in enumerate(categories):
            values = [
                category.get("category", "Uncategorized"),
                str(category.get("product_count", 0) or 0),
                str(category.get("stock_units", 0) or 0),
                format_currency(category.get("stock_value", 0) or 0),
                str(category.get("units_sold", 0) or 0),
                format_currency(category.get("sales_value", 0) or 0),
            ]
            for col, value in enumerate(values):
                table.setItem(row, col, QTableWidgetItem(value))
        self.category_layout.addWidget(table)

    def _render_overview(self, stats):
        while self.overview_layout.count() > 1:
            item = self.overview_layout.takeAt(1)
            if item.widget():
                item.widget().deleteLater()

        summary = QLabel(
            f"Inventory value {format_currency(stats['inventory'].get('inventory_value', 0))} "
            f"across {stats['inventory'].get('product_count', 0)} active products. "
            f"Total Profit earned is {format_currency(stats['sales'].get('total_profit', 0))}. "
            f"Customer pending is {format_currency(stats['sales'].get('total_pending', 0))} "
            f"and supplier pending is {format_currency(self._supplier_pending_total(stats['suppliers_due']))}."
        )
        summary.setStyleSheet("font-size:13px;color:#334155;line-height:1.6;")
        summary.setWordWrap(True)
        self.overview_layout.addWidget(summary)

        low_stock = stats["low_stock"]
        if low_stock:
            low_summary = QLabel(
                "<b>Low stock watch:</b> "
                + ", ".join(item["name"] for item in low_stock[:5])
                + ("..." if len(low_stock) > 5 else "")
            )
            low_summary.setStyleSheet("font-size:13px;color:#92400e;")
            low_summary.setWordWrap(True)
            self.overview_layout.addWidget(low_summary)
        else:
            ok = QLabel("All tracked products are comfortably above their low-stock threshold.")
            ok.setStyleSheet("font-size:13px;color:#15803d;")
            self.overview_layout.addWidget(ok)

    def _render_inventory(self, stats):
        while self.inventory_layout.count() > 1:
            item = self.inventory_layout.takeAt(1)
            if item.widget():
                item.widget().deleteLater()

        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Product", "Qty", "Threshold", "Value"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setShowGrid(False)
        table.setAlternatingRowColors(True)
        table.setRowCount(len(stats["low_stock"]))
        table.setFixedHeight(240)
        table.setStyleSheet(
            "QTableWidget{border:none;font-size:13px;background:white;alternate-background-color:#f8fafc;}"
            "QHeaderView::section{background:#f1f5f9;color:#475569;font-weight:700;font-size:12px;padding:8px;border:none;}"
            "QTableWidget::item{padding:8px;color:#1e293b;}"
        )
        for row, item_data in enumerate(stats["low_stock"]):
            values = [
                item_data.get("name", ""),
                str(item_data.get("quantity", 0) or 0),
                str(item_data.get("low_stock_threshold", 0) or 0),
                format_currency((item_data.get("quantity", 0) or 0) * (item_data.get("purchase_price", 0) or 0)),
            ]
            for col, value in enumerate(values):
                table.setItem(row, col, QTableWidgetItem(value))
        if not stats["low_stock"]:
            note = QLabel("No low-stock alerts right now.")
            note.setStyleSheet("font-size:13px;color:#15803d;padding:8px 0;")
            self.inventory_layout.addWidget(note)
        self.inventory_layout.addWidget(table)

    def _render_recent_sales(self, recent_sales):
        while self.recent_layout.count() > 1:
            item = self.recent_layout.takeAt(1)
            if item.widget():
                item.widget().deleteLater()

        table = QTableWidget()
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels(["Invoice", "Customer", "Revenue", "Paid", "Remaining", "Date"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setShowGrid(False)
        table.setAlternatingRowColors(True)
        table.setRowCount(len(recent_sales))
        table.setFixedHeight(240)
        table.setStyleSheet(
            "QTableWidget{border:none;font-size:13px;background:white;alternate-background-color:#f8fafc;}"
            "QHeaderView::section{background:#f1f5f9;color:#475569;font-weight:700;font-size:12px;padding:8px;border:none;}"
            "QTableWidget::item{padding:8px;color:#1e293b;}"
        )
        for row, sale in enumerate(recent_sales):
            cells = [
                sale.get("invoice_number", ""),
                sale.get("customer_name", ""),
                format_currency(sale.get("total_amount", 0) or 0),
                format_currency(sale.get("paid_amount", 0) or 0),
                format_currency(sale.get("remaining_amount", 0) or 0),
                format_datetime(sale.get("sale_date", "")),
            ]
            for col, text in enumerate(cells):
                table.setItem(row, col, QTableWidgetItem(text))
        if not recent_sales:
            note = QLabel("No recent sales yet.")
            note.setStyleSheet("font-size:13px;color:#64748b;padding:8px 0;")
            self.recent_layout.addWidget(note)
        self.recent_layout.addWidget(table)

    def _render_customer_balances(self, customers_due):
        while self.customers_layout.count() > 1:
            item = self.customers_layout.takeAt(1)
            if item.widget():
                item.widget().deleteLater()

        table = QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["Customer", "Opening", "Outstanding"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setShowGrid(False)
        table.setAlternatingRowColors(True)
        rows = []
        for customer in customers_due:
            opening_balance = float(customer.get("opening_balance", 0) or 0)
            opening_paid = float(customer.get("opening_paid", 0) or 0)
            sales_pending = float(customer.get("sales_pending", 0) or 0)
            outstanding = max(0.0, opening_balance - opening_paid) + sales_pending
            if outstanding > 0:
                rows.append((customer.get("name", ""), opening_balance, outstanding))
        table.setRowCount(len(rows))
        table.setFixedHeight(240)
        table.setStyleSheet(
            "QTableWidget{border:none;font-size:13px;background:white;alternate-background-color:#f8fafc;}"
            "QHeaderView::section{background:#f1f5f9;color:#475569;font-weight:700;font-size:12px;padding:8px;border:none;}"
            "QTableWidget::item{padding:8px;color:#1e293b;}"
        )
        for row, (name, opening, outstanding) in enumerate(rows):
            table.setItem(row, 0, QTableWidgetItem(name))
            table.setItem(row, 1, QTableWidgetItem(format_currency(opening)))
            outstanding_item = QTableWidgetItem(format_currency(outstanding))
            outstanding_item.setForeground(QColor("#dc2626"))
            table.setItem(row, 2, outstanding_item)
        if not rows:
            note = QLabel("No customer balances are pending.")
            note.setStyleSheet("font-size:13px;color:#15803d;padding:8px 0;")
            self.customers_layout.addWidget(note)
        self.customers_layout.addWidget(table)

    def _render_supplier_balances(self, suppliers_due):
        while self.suppliers_layout.count() > 1:
            item = self.suppliers_layout.takeAt(1)
            if item.widget():
                item.widget().deleteLater()

        table = QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["Supplier", "Total Payable", "Outstanding"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setShowGrid(False)
        table.setAlternatingRowColors(True)
        rows = []
        for supplier in suppliers_due:
            opening = float(supplier.get("opening_balance", 0) or 0)
            purchases = float(supplier.get("purchase_total", 0) or 0)
            paid = (float(supplier.get("paid_at_purchase", 0) or 0)
                    + float(supplier.get("total_paid", 0) or 0))
            outstanding = max(0.0, opening + purchases - paid)
            if outstanding > 0:
                rows.append((supplier.get("name", ""), opening + purchases, outstanding))
        table.setRowCount(len(rows))
        table.setFixedHeight(240)
        table.setStyleSheet(
            "QTableWidget{border:none;font-size:13px;background:white;alternate-background-color:#f8fafc;}"
            "QHeaderView::section{background:#f1f5f9;color:#475569;font-weight:700;font-size:12px;padding:8px;border:none;}"
            "QTableWidget::item{padding:8px;color:#1e293b;}"
        )
        for row, (name, opening, outstanding) in enumerate(rows):
            table.setItem(row, 0, QTableWidgetItem(name))
            table.setItem(row, 1, QTableWidgetItem(format_currency(opening)))
            outstanding_item = QTableWidgetItem(format_currency(outstanding))
            outstanding_item.setForeground(QColor("#dc2626"))
            table.setItem(row, 2, outstanding_item)
        if not rows:
            note = QLabel("No supplier balances are pending.")
            note.setStyleSheet("font-size:13px;color:#15803d;padding:8px 0;")
            self.suppliers_layout.addWidget(note)
        self.suppliers_layout.addWidget(table)
