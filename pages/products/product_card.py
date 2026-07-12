from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QPushButton,
    QHBoxLayout, QMessageBox, QFrame, QGraphicsDropShadowEffect
)
from PySide6.QtGui import QPixmap, QColor
from PySide6.QtCore import Qt

from models.product_model import delete_product
from utils.helpers import format_currency, is_expired, is_expiring_soon
from pages.products.edit_product_dialog import EditProductDialog
from pages.products.sell_product_dialog import SellProductDialog


class ProductCard(QWidget):

    def __init__(self, product: dict, refresh_callback=None):
        super().__init__()
        self.product = product
        self.refresh_callback = refresh_callback
        self.setFixedSize(270, 340)
        self._build()

    def _build(self):
        p = self.product
        qty       = p.get("quantity", 0)
        threshold = p.get("low_stock_threshold", 5)
        expiry    = p.get("expiry_date", "")

        if qty == 0:
            badge_text, badge_color, badge_bg = "Out of Stock", "#991b1b", "#fee2e2"
        elif qty <= threshold:
            badge_text, badge_color, badge_bg = "Low Stock",    "#92400e", "#fef3c7"
        else:
            badge_text, badge_color, badge_bg = "In Stock",     "#065f46", "#d1fae5"
        secret = bool(p.get("secret_product", 0))

        # ── Card frame
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("""
            QWidget {
                background: white;
                border-radius: 14px;
            }
            QLabel { background: transparent; }
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(18)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 30))
        self.setGraphicsEffect(shadow)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Image section
        img_frame = QFrame()
        img_frame.setFixedHeight(140)
        img_frame.setAttribute(Qt.WA_StyledBackground, True)
        img_frame.setStyleSheet("background:#f8fafc; border-radius:14px 14px 0 0;")

        img_lbl = QLabel(img_frame)
        img_lbl.setFixedSize(270, 140)
        img_lbl.setAlignment(Qt.AlignCenter)

        img_path = p.get("image", "")
        if img_path:
            pix = QPixmap(img_path)
            if not pix.isNull():
                img_lbl.setPixmap(pix.scaled(250, 130, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            else:
                img_lbl.setText("📷")
                img_lbl.setStyleSheet("font-size:36px; color:#cbd5e0;")
        else:
            img_lbl.setText("📷")
            img_lbl.setStyleSheet("font-size:36px; color:#cbd5e0;")

        # Badge overlay on image
        badge = QLabel(badge_text, img_frame)
        badge.setStyleSheet(f"""
            background:{badge_bg}; color:{badge_color};
            border-radius:6px; padding:2px 8px;
            font-size:10px; font-weight:700;
        """)
        badge.adjustSize()
        badge.move(10, 10)

        if secret:
            secret_badge = QLabel("Secret", img_frame)
            secret_badge.setStyleSheet(
                "background:#111827;color:white;border-radius:6px;padding:2px 8px;"
                "font-size:10px;font-weight:700;"
            )
            secret_badge.adjustSize()
            secret_badge.move(190, 10)

        root.addWidget(img_frame)

        # ── Info section
        info = QVBoxLayout()
        info.setContentsMargins(14, 10, 14, 4)
        info.setSpacing(3)

        name_lbl = QLabel(p.get("name", ""))
        name_lbl.setStyleSheet("font-size:14px; font-weight:700; color:#0f172a;")
        name_lbl.setWordWrap(True)

        brand_cat = QLabel(f"{p.get('brand','')}  ·  {p.get('category','')}")
        brand_cat.setStyleSheet("font-size:11px; color:#64748b;")
        sub_cat = QLabel(p.get("sub_category", "") or "")
        sub_cat.setStyleSheet("font-size:10px; color:#94a3b8;")

        price_lbl = QLabel(format_currency(p.get("sale_price", 0)))
        price_lbl.setStyleSheet("font-size:16px; font-weight:800; color:#2e7d32;")

        qty_lbl = QLabel(f"Qty: {qty}")
        qty_lbl.setStyleSheet(f"font-size:12px; color:{badge_color}; font-weight:600;")

        if expiry:
            if is_expired(expiry):
                exp_lbl = QLabel(f"⚠ Expired: {expiry}")
                exp_lbl.setStyleSheet("font-size:11px; color:#ef4444;")
            elif is_expiring_soon(expiry):
                exp_lbl = QLabel(f"⏳ Expires: {expiry}")
                exp_lbl.setStyleSheet("font-size:11px; color:#f59e0b;")
            else:
                exp_lbl = QLabel(f"📅 Exp: {expiry}")
                exp_lbl.setStyleSheet("font-size:11px; color:#94a3b8;")
            info.addWidget(exp_lbl)

        info.addWidget(name_lbl)
        info.addWidget(brand_cat)
        if p.get("sub_category"):
            info.addWidget(sub_cat)
        info.addWidget(price_lbl)
        info.addWidget(qty_lbl)
        info.addStretch()

        root.addLayout(info)

        # ── Action buttons
        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(10, 0, 10, 12)
        btn_row.setSpacing(6)

        sell_btn = QPushButton("🛒 Sell")
        sell_btn.setFixedHeight(30)
        sell_btn.setStyleSheet("""
            QPushButton { background:#d1fae5; color:#065f46; border:1px solid #6ee7b7;
                          border-radius:7px; font-size:11px; font-weight:700; }
            QPushButton:hover { background:#a7f3d0; }
        """)
        sell_btn.clicked.connect(self._sell)

        edit_btn = QPushButton("✏ Edit")
        edit_btn.setFixedHeight(30)
        edit_btn.setStyleSheet("""
            QPushButton { background:#eff6ff; color:#1d4ed8; border:1px solid #bfdbfe;
                          border-radius:7px; font-size:11px; font-weight:600; }
            QPushButton:hover { background:#dbeafe; }
        """)
        edit_btn.clicked.connect(self._edit)

        del_btn = QPushButton("🗑")
        del_btn.setFixedSize(30, 30)
        del_btn.setStyleSheet("""
            QPushButton { background:#fef2f2; color:#dc2626; border:1px solid #fecaca;
                          border-radius:7px; font-size:13px; }
            QPushButton:hover { background:#fee2e2; }
        """)
        del_btn.clicked.connect(self._delete)

        btn_row.addWidget(sell_btn)
        btn_row.addWidget(edit_btn)
        btn_row.addWidget(del_btn)
        root.addLayout(btn_row)

    def _sell(self):
        dialog = SellProductDialog(self.product)
        dialog.sale_completed.connect(self.refresh_callback or (lambda: None))
        dialog.exec()

    def _edit(self):
        dialog = EditProductDialog(self.product)
        if dialog.exec():
            if self.refresh_callback:
                self.refresh_callback()

    def _delete(self):
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Delete product '{self.product.get('name')}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                delete_product(self.product["id"])
                if self.refresh_callback:
                    self.refresh_callback()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))
