from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame,
    QSizePolicy, QGraphicsDropShadowEffect, QScrollArea,
    QTableWidget, QTableWidgetItem, QHeaderView, QPushButton
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont

from models.product_model import get_all_products, get_low_stock_products
from models.sale_model import get_sales_summary, get_all_sales
from models.customer_model import get_all_customers
from models.supplier_model import get_all_suppliers
from utils.helpers import format_currency, format_datetime

# ── Stat card definitions: (title, icon, accent_color, bg_gradient)
_CARDS = [
    ("Total Products",    "📦", "#3b82f6", "#eff6ff", "#dbeafe"),
    ("Total Customers",   "👥", "#10b981", "#f0fdf4", "#d1fae5"),
    ("Total Suppliers",   "🚚", "#8b5cf6", "#f5f3ff", "#ede9fe"),
    ("Total Revenue",     "💰", "#f59e0b", "#fffbeb", "#fef3c7"),
    ("Pending Payments",  "⏳", "#ef4444", "#fef2f2", "#fee2e2"),
    ("Low Stock Items",   "⚠",  "#f97316", "#fff7ed", "#ffedd5"),
]


class DashboardPage(QWidget):

    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("background-color: #f1f5f9;")
        self._build_ui()

    # ──────────────────────────────────────────────────────
    def _build_ui(self):
        stats = self._load_stats()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: #f1f5f9; border:none;")

        content = QWidget()
        content.setStyleSheet("background: #f1f5f9;")
        root = QVBoxLayout(content)
        root.setContentsMargins(28, 24, 28, 28)
        root.setSpacing(24)

        # ── Header
        header = QHBoxLayout()
        page_title = QLabel("Dashboard")
        page_title.setStyleSheet("font-size:26px; font-weight:700; color:#0f172a;")
        refresh_btn = QPushButton("↻  Refresh")
        refresh_btn.setFixedSize(110, 36)
        refresh_btn.setStyleSheet("""
            QPushButton { background:#2e7d32; color:white; border-radius:8px;
                          font-size:13px; font-weight:600; border:none; }
            QPushButton:hover { background:#1b5e20; }
        """)
        refresh_btn.clicked.connect(self._refresh)
        header.addWidget(page_title)
        header.addStretch()
        header.addWidget(refresh_btn)
        root.addLayout(header)

        # ── Low-stock banner
        low_stock_items = get_low_stock_products()
        if low_stock_items:
            banner = QFrame()
            banner.setStyleSheet("""
                QFrame { background:#fef3c7; border:1.5px solid #f59e0b;
                         border-radius:10px; padding:4px; }
            """)
            b_layout = QHBoxLayout(banner)
            b_layout.setContentsMargins(14, 8, 14, 8)
            icon = QLabel("⚠")
            icon.setStyleSheet("font-size:18px;")
            msg = QLabel(
                f"<b>{len(low_stock_items)} product(s)</b> are low on stock: "
                + ", ".join(p["name"] for p in low_stock_items[:5])
                + ("…" if len(low_stock_items) > 5 else "")
            )
            msg.setStyleSheet("font-size:13px; color:#92400e;")
            b_layout.addWidget(icon)
            b_layout.addWidget(msg)
            b_layout.addStretch()
            root.addWidget(banner)

        # ── Stat Cards row
        self._card_widgets = {}
        cards_row = QHBoxLayout()
        cards_row.setSpacing(16)
        values = [
            str(stats["products"]),
            str(stats["customers"]),
            str(stats["suppliers"]),
            stats["revenue"],
            stats["pending"],
            str(stats["low_stock"]),
        ]
        for (title, icon, accent, bg1, bg2), value in zip(_CARDS, values):
            cards_row.addWidget(self._make_stat_card(title, icon, value, accent, bg1, bg2))
        root.addLayout(cards_row)

        # ── Bottom section: Recent Sales + Low Stock table
        bottom = QHBoxLayout()
        bottom.setSpacing(20)
        bottom.addWidget(self._make_recent_sales_panel(), stretch=3)
        bottom.addWidget(self._make_low_stock_panel(low_stock_items), stretch=2)
        root.addLayout(bottom)

        root.addStretch()
        scroll.setWidget(content)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    # ──────────────────────────────────────────────────────
    def _make_stat_card(self, title, icon, value, accent, bg1, bg2) -> QFrame:
        card = QFrame()
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        card.setFixedHeight(110)
        card.setAttribute(Qt.WA_StyledBackground, True)
        card.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 {bg1}, stop:1 {bg2});
                border-radius: 14px;
                border: 1.5px solid {accent}33;
            }}
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(16)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 35))
        card.setGraphicsEffect(shadow)

        layout = QHBoxLayout(card)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(14)

        icon_lbl = QLabel(icon)
        icon_lbl.setFixedSize(48, 48)
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setStyleSheet(f"""
            background:{accent}22; border-radius:12px;
            font-size:22px;
        """)

        text_col = QVBoxLayout()
        text_col.setSpacing(2)
        val_lbl = QLabel(value)
        val_lbl.setStyleSheet(f"font-size:24px; font-weight:800; color:{accent};")
        ttl_lbl = QLabel(title)
        ttl_lbl.setStyleSheet("font-size:12px; color:#64748b; font-weight:500;")
        text_col.addWidget(val_lbl)
        text_col.addWidget(ttl_lbl)

        layout.addWidget(icon_lbl)
        layout.addLayout(text_col)
        layout.addStretch()
        return card

    # ──────────────────────────────────────────────────────
    def _make_recent_sales_panel(self) -> QFrame:
        panel = QFrame()
        panel.setAttribute(Qt.WA_StyledBackground, True)
        panel.setStyleSheet("""
            QFrame { background:white; border-radius:14px;
                     border:1px solid #e2e8f0; }
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(16)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 25))
        panel.setGraphicsEffect(shadow)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(12)

        hdr = QHBoxLayout()
        title = QLabel("🛒  Recent Sales")
        title.setStyleSheet("font-size:15px; font-weight:700; color:#0f172a;")
        hdr.addWidget(title)
        hdr.addStretch()
        layout.addLayout(hdr)

        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["Invoice", "Customer", "Amount", "Paid", "Date"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setAlternatingRowColors(True)
        table.setShowGrid(False)
        table.setStyleSheet("""
            QTableWidget { border:none; font-size:13px; background:white;
                           alternate-background-color:#f8fafc; }
            QHeaderView::section { background:#f1f5f9; color:#475569;
                font-weight:600; padding:8px; border:none; font-size:12px; }
            QTableWidget::item { padding:8px; color:#1e293b; }
            QTableWidget::item:selected { background:#dbeafe; color:#1e40af; }
        """)

        sales = get_all_sales()[:8]
        table.setRowCount(len(sales))
        for r, s in enumerate(sales):
            table.setItem(r, 0, QTableWidgetItem(s.get("invoice_number", "")))
            table.setItem(r, 1, QTableWidgetItem(s.get("customer_name") or "Walk-in"))
            table.setItem(r, 2, QTableWidgetItem(format_currency(s.get("total_amount", 0))))
            table.setItem(r, 3, QTableWidgetItem(format_currency(s.get("paid_amount", 0))))
            table.setItem(r, 4, QTableWidgetItem(format_datetime(s.get("sale_date", ""))))

        layout.addWidget(table)
        return panel

    # ──────────────────────────────────────────────────────
    def _make_low_stock_panel(self, items: list) -> QFrame:
        panel = QFrame()
        panel.setAttribute(Qt.WA_StyledBackground, True)
        panel.setStyleSheet("""
            QFrame { background:white; border-radius:14px;
                     border:1px solid #e2e8f0; }
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(16)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 25))
        panel.setGraphicsEffect(shadow)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(12)

        title = QLabel("⚠  Low Stock Alerts")
        title.setStyleSheet("font-size:15px; font-weight:700; color:#0f172a;")
        layout.addWidget(title)

        if not items:
            ok = QLabel("✅  All products are well stocked!")
            ok.setStyleSheet("color:#10b981; font-size:13px; padding:12px 0;")
            ok.setAlignment(Qt.AlignCenter)
            layout.addWidget(ok)
        else:
            table = QTableWidget()
            table.setColumnCount(3)
            table.setHorizontalHeaderLabels(["Product", "Qty", "Min"])
            table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            table.verticalHeader().setVisible(False)
            table.setEditTriggers(QTableWidget.NoEditTriggers)
            table.setShowGrid(False)
            table.setAlternatingRowColors(True)
            table.setStyleSheet("""
                QTableWidget { border:none; font-size:13px; background:white;
                               alternate-background-color:#fff7ed; }
                QHeaderView::section { background:#fff7ed; color:#92400e;
                    font-weight:600; padding:8px; border:none; font-size:12px; }
                QTableWidget::item { padding:8px; color:#1e293b; }
            """)
            table.setRowCount(len(items))
            for r, p in enumerate(items):
                qty = p.get("quantity", 0)
                threshold = p.get("low_stock_threshold", 5)
                name_item = QTableWidgetItem(p.get("name", ""))
                qty_item  = QTableWidgetItem(str(qty))
                min_item  = QTableWidgetItem(str(threshold))
                if qty == 0:
                    qty_item.setForeground(QColor("#ef4444"))
                else:
                    qty_item.setForeground(QColor("#f97316"))
                table.setItem(r, 0, name_item)
                table.setItem(r, 1, qty_item)
                table.setItem(r, 2, min_item)
            layout.addWidget(table)

        layout.addStretch()
        return panel

    # ──────────────────────────────────────────────────────
    def _load_stats(self) -> dict:
        try:
            products  = get_all_products()
            customers = get_all_customers()
            suppliers = get_all_suppliers()
            low_stock = get_low_stock_products()
            summary   = get_sales_summary()
        except Exception:
            return {"products": 0, "customers": 0, "suppliers": 0,
                    "revenue": "Rs 0", "pending": "Rs 0", "low_stock": 0}
        return {
            "products":  len(products),
            "customers": len(customers),
            "suppliers": len(suppliers),
            "revenue":   format_currency(summary.get("total_revenue", 0)),
            "pending":   format_currency(summary.get("total_pending", 0)),
            "low_stock": len(low_stock),
        }

    def _refresh(self):
        layout = self.layout()
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._build_ui()
