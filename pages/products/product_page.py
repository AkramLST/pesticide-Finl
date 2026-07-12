from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QGridLayout, QScrollArea, QHBoxLayout, QLineEdit,
    QFrame, QComboBox, QCheckBox, QMessageBox
)
from PySide6.QtCore import Qt

from pages.products.add_product_dialog import AddProductDialog
from pages.products.product_card import ProductCard
from models.product_model import get_all_products, get_low_stock_products
from models.user_model import get_user_by_credentials
from utils.session import session
from utils.config import PRODUCT_CATEGORIES


class ProductPage(QWidget):

    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("background:#f1f5f9;")
        self._all_products = []
        self._show_secret_products = False
        self._build_ui()
        self.load_products()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ── Top Header Bar
        header_frame = QFrame()
        header_frame.setFixedHeight(64)
        header_frame.setAttribute(Qt.WA_StyledBackground, True)
        header_frame.setStyleSheet("""
            QFrame { background:white; border-bottom:1.5px solid #e2e8f0; }
        """)
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(24, 0, 24, 0)
        header_layout.setSpacing(12)

        title = QLabel("📦  Products")
        title.setStyleSheet("font-size:20px; font-weight:700; color:#0f172a;")

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍  Search by name, brand or category…")
        self.search_input.setFixedWidth(320)
        self.search_input.setStyleSheet("""
            QLineEdit { border:1.5px solid #e2e8f0; border-radius:8px;
                        padding:8px 14px; font-size:13px; background:white; }
            QLineEdit:focus { border-color:#2e7d32; }
        """)
        self.search_input.textChanged.connect(self._filter_products)

        self.cat_filter = QComboBox()
        self.cat_filter.setFixedWidth(160)
        self.cat_filter.addItem("All Categories")
        self.cat_filter.addItems(PRODUCT_CATEGORIES)
        self.cat_filter.setStyleSheet("""
            QComboBox { border:1.5px solid #e2e8f0; border-radius:8px;
                        padding:7px 12px; font-size:13px; background:white; }
            QComboBox:focus { border-color:#2e7d32; }
            QComboBox::drop-down { border:none; }
        """)
        self.cat_filter.currentTextChanged.connect(self._filter_products)

        self.secret_toggle = QCheckBox("Show Secret Products")
        self.secret_toggle.setStyleSheet("font-size:12px; color:#334155;")
        self.secret_toggle.stateChanged.connect(self._toggle_secret_products)

        add_btn = QPushButton("＋  Add Product")
        add_btn.setFixedHeight(38)
        add_btn.setStyleSheet("""
            QPushButton { background:#2e7d32; color:white; border-radius:8px;
                          padding:0 18px; font-size:13px; font-weight:600; border:none; }
            QPushButton:hover { background:#1b5e20; }
        """)
        add_btn.clicked.connect(self.open_add_product)

        refresh_btn = QPushButton("↻")
        refresh_btn.setFixedSize(38, 38)
        refresh_btn.setStyleSheet("""
            QPushButton { background:#f1f5f9; border:1.5px solid #e2e8f0;
                          border-radius:8px; font-size:16px; color:#475569; }
            QPushButton:hover { background:#e2e8f0; }
        """)
        refresh_btn.clicked.connect(self.load_products)

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.search_input)
        header_layout.addWidget(self.cat_filter)
        header_layout.addWidget(self.secret_toggle)
        header_layout.addWidget(add_btn)
        header_layout.addWidget(refresh_btn)

        main_layout.addWidget(header_frame)

        # ── Stats strip
        self.stats_frame = QFrame()
        self.stats_frame.setFixedHeight(52)
        self.stats_frame.setAttribute(Qt.WA_StyledBackground, True)
        self.stats_frame.setStyleSheet("background:#f8fafc; border-bottom:1px solid #e2e8f0;")
        self._stats_layout = QHBoxLayout(self.stats_frame)
        self._stats_layout.setContentsMargins(24, 0, 24, 0)
        self._stats_layout.setSpacing(30)
        main_layout.addWidget(self.stats_frame)

        # ── Scrollable card grid
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setStyleSheet("background:#f1f5f9; border:none;")

        self.container = QWidget()
        self.container.setStyleSheet("background:#f1f5f9;")
        self.grid = QGridLayout(self.container)
        self.grid.setContentsMargins(24, 20, 24, 24)
        self.grid.setSpacing(18)
        self.grid.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        self.scroll.setWidget(self.container)
        main_layout.addWidget(self.scroll)

    # ──────────────────────────────────────────────────────
    def _update_stats_strip(self, products):
        while self._stats_layout.count():
            item = self._stats_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        low = sum(1 for p in products
                  if 0 < p.get("quantity", 0) <= p.get("low_stock_threshold", 5))
        out = sum(1 for p in products if p.get("quantity", 0) == 0)

        stats = [
            (f"Showing  <b>{len(products)}</b>  products", "#475569"),
            (f"🟢  In Stock: <b>{len(products) - low - out}</b>", "#10b981"),
            (f"🟠  Low Stock: <b>{low}</b>", "#f59e0b"),
            (f"🔴  Out of Stock: <b>{out}</b>", "#ef4444"),
        ]
        for text, color in stats:
            lbl = QLabel(text)
            lbl.setStyleSheet(f"font-size:13px; color:{color};")
            self._stats_layout.addWidget(lbl)
        self._stats_layout.addStretch()

    # ──────────────────────────────────────────────────────
    def load_products(self):
        self._all_products = get_all_products(include_secret=self._show_secret_products)
        self._filter_products()

    def _filter_products(self):
        query = self.search_input.text().lower().strip()
        cat   = self.cat_filter.currentText()

        filtered = [
            p for p in self._all_products
            if (query in p.get("name", "").lower()
                or query in p.get("brand", "").lower()
                or query in p.get("category", "").lower()
                or query in (p.get("sub_category", "") or "").lower())
            and (cat == "All Categories" or p.get("category", "") == cat)
        ]

        for i in reversed(range(self.grid.count())):
            w = self.grid.itemAt(i).widget()
            if w:
                w.setParent(None)

        self._update_stats_strip(filtered)

        if not filtered:
            empty = QLabel("No products found.")
            empty.setAlignment(Qt.AlignCenter)
            empty.setStyleSheet("color:#94a3b8; font-size:16px; padding:40px;")
            self.grid.addWidget(empty, 0, 0, 1, 4)
            return

        row = col = 0
        for product in filtered:
            card = ProductCard(product, self.load_products)
            self.grid.addWidget(card, row, col)
            col += 1
            if col == 4:
                col = 0
                row += 1

    def open_add_product(self):
        dialog = AddProductDialog()
        if dialog.exec():
            self.load_products()

    def _toggle_secret_products(self, state: int):
        if state != Qt.Checked:
            self._show_secret_products = False
            self.load_products()
            return
        if self._confirm_admin_password():
            self._show_secret_products = True
            self.load_products()
            return
        self.secret_toggle.blockSignals(True)
        self.secret_toggle.setChecked(False)
        self.secret_toggle.blockSignals(False)

    def _confirm_admin_password(self) -> bool:
        from PySide6.QtWidgets import QInputDialog

        if not session.user:
            QMessageBox.warning(self, "Access Denied", "Please log in again.")
            return False
        pwd, ok = QInputDialog.getText(
            self,
            "Administrator Password",
            "Enter administrator password:",
            QLineEdit.Password,
        )
        if not ok or not pwd:
            return False
        user = get_user_by_credentials(session.user.get("username", ""), pwd)
        if not user or user.get("role") != "Admin":
            QMessageBox.warning(self, "Access Denied", "Invalid administrator password.")
            return False
        return True
