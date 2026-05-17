from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QLineEdit, QComboBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from models.product_model import get_all_products
from utils.helpers import format_currency, is_expired, is_expiring_soon
from utils.config import PRODUCT_CATEGORIES

# Column indices
COL_ID   = 0
COL_NAME = 1
COL_CAT  = 2
COL_SUP  = 3
COL_QTY  = 4
COL_BUY  = 5
COL_SELL = 6
COL_EXP  = 7
COL_STAT = 8
COL_UPD  = 9


class InventoryPage(QWidget):

    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("background:#f1f5f9;")
        self._all_products = []
        self._build_ui()
        self.load_data()

    # ──────────────────────────────────────────────────────
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Header bar
        header = QFrame()
        header.setFixedHeight(64)
        header.setAttribute(Qt.WA_StyledBackground, True)
        header.setStyleSheet("QFrame{ background:white; border-bottom:1.5px solid #e2e8f0; }")
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(24, 0, 24, 0)
        h_layout.setSpacing(12)

        title = QLabel("🗃  Inventory")
        title.setStyleSheet("font-size:20px; font-weight:700; color:#0f172a;")

        self.search = QLineEdit()
        self.search.setPlaceholderText("🔍  Search product…")
        self.search.setFixedWidth(260)
        self.search.setStyleSheet("""
            QLineEdit { border:1.5px solid #e2e8f0; border-radius:8px;
                        padding:8px 14px; font-size:13px; background:white; }
            QLineEdit:focus { border-color:#2e7d32; }
        """)
        self.search.textChanged.connect(self._filter)

        self.cat_cb = QComboBox()
        self.cat_cb.setFixedWidth(150)
        self.cat_cb.addItem("All Categories")
        self.cat_cb.addItems(PRODUCT_CATEGORIES)
        self.cat_cb.setStyleSheet("""
            QComboBox { border:1.5px solid #e2e8f0; border-radius:8px;
                        padding:7px 12px; font-size:13px; background:white; }
            QComboBox::drop-down { border:none; }
        """)
        self.cat_cb.currentTextChanged.connect(self._filter)

        self.stock_cb = QComboBox()
        self.stock_cb.setFixedWidth(140)
        self.stock_cb.addItems(["All Stock", "In Stock", "Low Stock", "Out of Stock"])
        self.stock_cb.setStyleSheet(self.cat_cb.styleSheet())
        self.stock_cb.currentTextChanged.connect(self._filter)

        self.exp_cb = QComboBox()
        self.exp_cb.setFixedWidth(140)
        self.exp_cb.addItems(["All Expiry", "Valid", "Expiring Soon", "Expired"])
        self.exp_cb.setStyleSheet(self.cat_cb.styleSheet())
        self.exp_cb.currentTextChanged.connect(self._filter)

        refresh_btn = QPushButton("↻")
        refresh_btn.setFixedSize(38, 38)
        refresh_btn.setStyleSheet("""
            QPushButton { background:#f1f5f9; border:1.5px solid #e2e8f0;
                          border-radius:8px; font-size:16px; color:#475569; }
            QPushButton:hover { background:#e2e8f0; }
        """)
        refresh_btn.clicked.connect(self.load_data)

        h_layout.addWidget(title)
        h_layout.addStretch()
        h_layout.addWidget(self.search)
        h_layout.addWidget(self.cat_cb)
        h_layout.addWidget(self.stock_cb)
        h_layout.addWidget(self.exp_cb)
        h_layout.addWidget(refresh_btn)
        root.addWidget(header)

        # ── Stats strip
        self.stats_bar = QFrame()
        self.stats_bar.setFixedHeight(44)
        self.stats_bar.setAttribute(Qt.WA_StyledBackground, True)
        self.stats_bar.setStyleSheet("background:#f8fafc; border-bottom:1px solid #e2e8f0;")
        self._sbar_layout = QHBoxLayout(self.stats_bar)
        self._sbar_layout.setContentsMargins(24, 0, 24, 0)
        self._sbar_layout.setSpacing(28)
        root.addWidget(self.stats_bar)

        # ── Table
        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            "ID", "Product Name", "Category", "Supplier",
            "Qty", "Buy Price", "Sale Price",
            "Expiry Date", "Status", "Last Updated"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setDefaultSectionSize(120)
        self.table.setColumnWidth(COL_ID,   50)
        self.table.setColumnWidth(COL_NAME, 200)
        self.table.setColumnWidth(COL_CAT,  120)
        self.table.setColumnWidth(COL_SUP,  130)
        self.table.setColumnWidth(COL_QTY,  60)
        self.table.setColumnWidth(COL_BUY,  110)
        self.table.setColumnWidth(COL_SELL, 110)
        self.table.setColumnWidth(COL_EXP,  110)
        self.table.setColumnWidth(COL_STAT, 110)

        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.setSortingEnabled(True)
        self.table.setStyleSheet("""
            QTableWidget {
                border: none;
                font-size: 13px;
                background: white;
                alternate-background-color: #f8fafc;
                gridline-color: #f1f5f9;
            }
            QHeaderView::section {
                background: #f1f5f9;
                color: #475569;
                font-weight: 700;
                font-size: 12px;
                padding: 10px 8px;
                border: none;
                border-right: 1px solid #e2e8f0;
            }
            QTableWidget::item {
                padding: 10px 8px;
                color: #1e293b;
                border-bottom: 1px solid #f1f5f9;
            }
            QTableWidget::item:selected {
                background: #dbeafe;
                color: #1e40af;
            }
        """)

        # Wrap table in a white padded frame
        table_wrap = QFrame()
        table_wrap.setAttribute(Qt.WA_StyledBackground, True)
        table_wrap.setStyleSheet("background:white; border:none;")
        tw_layout = QVBoxLayout(table_wrap)
        tw_layout.setContentsMargins(16, 16, 16, 16)
        tw_layout.setSpacing(0)
        tw_layout.addWidget(self.table)
        root.addWidget(table_wrap)

    # ──────────────────────────────────────────────────────
    def _update_stats(self, products):
        while self._sbar_layout.count():
            item = self._sbar_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        in_stock  = sum(1 for p in products if p.get("quantity", 0) > p.get("low_stock_threshold", 5))
        low       = sum(1 for p in products if 0 < p.get("quantity", 0) <= p.get("low_stock_threshold", 5))
        out       = sum(1 for p in products if p.get("quantity", 0) == 0)
        expired   = sum(1 for p in products if is_expired(p.get("expiry_date", "")))

        for text, color in [
            (f"Total: <b>{len(products)}</b>", "#475569"),
            (f"🟢 In Stock: <b>{in_stock}</b>", "#10b981"),
            (f"🟠 Low Stock: <b>{low}</b>", "#f59e0b"),
            (f"🔴 Out of Stock: <b>{out}</b>", "#ef4444"),
            (f"💀 Expired: <b>{expired}</b>", "#7c3aed"),
        ]:
            lbl = QLabel(text)
            lbl.setStyleSheet(f"font-size:13px; color:{color};")
            self._sbar_layout.addWidget(lbl)
        self._sbar_layout.addStretch()

    # ──────────────────────────────────────────────────────
    def load_data(self):
        self._all_products = get_all_products()
        self._filter()

    def _filter(self):
        query     = self.search.text().lower().strip()
        cat       = self.cat_cb.currentText()
        stock_f   = self.stock_cb.currentText()
        exp_f     = self.exp_cb.currentText()

        result = []
        for p in self._all_products:
            qty       = p.get("quantity", 0)
            threshold = p.get("low_stock_threshold", 5)
            expiry    = p.get("expiry_date", "")

            if query and query not in p.get("name", "").lower():
                continue
            if cat != "All Categories" and p.get("category", "") != cat:
                continue
            if stock_f == "In Stock"      and not (qty > threshold): continue
            if stock_f == "Low Stock"     and not (0 < qty <= threshold): continue
            if stock_f == "Out of Stock"  and qty != 0: continue
            if exp_f == "Expired"         and not is_expired(expiry): continue
            if exp_f == "Expiring Soon"   and not is_expiring_soon(expiry): continue
            if exp_f == "Valid"           and (is_expired(expiry) or is_expiring_soon(expiry)): continue

            result.append(p)

        self._populate_table(result)
        self._update_stats(result)

    def _populate_table(self, products):
        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(products))

        for row, p in enumerate(products):
            qty       = p.get("quantity", 0)
            threshold = p.get("low_stock_threshold", 5)
            expiry    = p.get("expiry_date", "") or ""

            # Status
            if qty == 0:
                status_text, row_color = "Out of Stock", QColor("#fff5f5")
                status_color = QColor("#dc2626")
            elif qty <= threshold:
                status_text, row_color = "Low Stock", QColor("#fffbeb")
                status_color = QColor("#d97706")
            else:
                status_text, row_color = "In Stock", None
                status_color = QColor("#059669")

            # Expiry override
            if is_expired(expiry):
                row_color    = QColor("#fdf4ff")
                status_text  = "Expired"
                status_color = QColor("#7c3aed")
            elif is_expiring_soon(expiry):
                row_color = QColor("#fffbeb")

            cells = [
                str(p.get("id", "")),
                p.get("name", ""),
                p.get("category", ""),
                p.get("supplier_name") or "—",
                str(qty),
                format_currency(p.get("purchase_price", 0)),
                format_currency(p.get("sale_price", 0)),
                expiry or "—",
                status_text,
                p.get("updated_at") or "—",
            ]

            for col, text in enumerate(cells):
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
                if row_color:
                    item.setBackground(row_color)
                if col == COL_STAT:
                    item.setForeground(status_color)
                    item.setTextAlignment(Qt.AlignCenter)
                if col == COL_QTY:
                    item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, col, item)

            self.table.setRowHeight(row, 42)

        self.table.setSortingEnabled(True)
