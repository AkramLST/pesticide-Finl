from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QTextEdit,
    QPushButton, QComboBox, QFileDialog, QFormLayout,
    QMessageBox, QSpinBox, QDoubleSpinBox, QHBoxLayout,
    QScrollArea, QWidget
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

from models.product_model import update_product
from models.supplier_model import get_all_suppliers
from utils.config import PRODUCT_CATEGORIES, PRODUCT_BRANDS, FORMULATIONS

_BTN = """
    QPushButton {{ background:{bg}; color:white; padding:10px;
        border-radius:8px; font-size:14px; font-weight:bold; border:none; }}
    QPushButton:hover {{ background:{hov}; }}
"""


class EditProductDialog(QDialog):

    def __init__(self, product: dict):
        super().__init__()
        self.product = product
        self.setWindowTitle("Edit Product")
        self.resize(500, 620)
        self.image_path = product.get("image", "") or ""
        self._build_ui()
        self._prefill()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        content = QWidget()
        main_layout = QVBoxLayout(content)
        main_layout.setContentsMargins(20, 16, 20, 16)
        main_layout.setSpacing(12)
        scroll.setWidget(content)
        outer.addWidget(scroll)

        heading = QLabel("✏  Edit Product")
        heading.setStyleSheet("font-size:20px; font-weight:bold; color:#0f172a;")
        main_layout.addWidget(heading)

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignRight)

        self.name_input = QLineEdit()
        self.desc_input = QTextEdit()
        self.desc_input.setFixedHeight(65)

        self.brand_combo = QComboBox()
        self.brand_combo.addItems(PRODUCT_BRANDS)

        self.category_combo = QComboBox()
        self.category_combo.addItems(PRODUCT_CATEGORIES)

        self.formulation_combo = QComboBox()
        self.formulation_combo.addItems(FORMULATIONS)

        self.supplier_combo = QComboBox()
        self.supplier_combo.addItem("— None —", None)
        for s in get_all_suppliers():
            self.supplier_combo.addItem(s["name"], s["id"])

        self.purchase_price = QDoubleSpinBox()
        self.purchase_price.setRange(0, 1_000_000)
        self.purchase_price.setPrefix("Rs ")
        self.purchase_price.setDecimals(2)

        self.sale_price = QDoubleSpinBox()
        self.sale_price.setRange(0, 1_000_000)
        self.sale_price.setPrefix("Rs ")
        self.sale_price.setDecimals(2)

        self.weight_input = QLineEdit()
        self.weight_input.setPlaceholderText("e.g. 500ml, 1kg")

        self.quantity_input = QSpinBox()
        self.quantity_input.setRange(0, 100_000)

        self.low_stock_input = QSpinBox()
        self.low_stock_input.setRange(0, 10_000)

        self.mfg_input = QLineEdit()
        self.mfg_input.setPlaceholderText("YYYY-MM-DD")

        self.expiry_input = QLineEdit()
        self.expiry_input.setPlaceholderText("YYYY-MM-DD")

        img_row = QHBoxLayout()
        self.image_btn = QPushButton("Change Image")
        self.image_btn.clicked.connect(self._select_image)
        self.image_preview = QLabel()
        self.image_preview.setFixedSize(60, 60)
        self.image_preview.setAlignment(Qt.AlignCenter)
        self.image_preview.setStyleSheet("border:1px solid #ccc; border-radius:4px;")
        img_row.addWidget(self.image_btn)
        img_row.addWidget(self.image_preview)

        form.addRow("Product Name *:", self.name_input)
        form.addRow("Description:", self.desc_input)
        form.addRow("Brand:", self.brand_combo)
        form.addRow("Category:", self.category_combo)
        form.addRow("Formulation:", self.formulation_combo)
        form.addRow("Supplier:", self.supplier_combo)
        form.addRow("Purchase Price:", self.purchase_price)
        form.addRow("Sale Price:", self.sale_price)
        form.addRow("Weight/Unit:", self.weight_input)
        form.addRow("Quantity:", self.quantity_input)
        form.addRow("Low Stock At:", self.low_stock_input)
        form.addRow("Mfg Date:", self.mfg_input)
        form.addRow("Expiry Date:", self.expiry_input)
        form.addRow("Image:", img_row)

        main_layout.addLayout(form)

        save_btn = QPushButton("Update Product")
        save_btn.setStyleSheet(_BTN.format(bg="#2e7d32", hov="#1b5e20"))
        save_btn.clicked.connect(self._save)
        main_layout.addWidget(save_btn)

    def _prefill(self):
        p = self.product
        self.name_input.setText(p.get("name", ""))
        self.desc_input.setPlainText(p.get("description", "") or "")
        self._set_combo(self.brand_combo,       p.get("brand", ""))
        self._set_combo(self.category_combo,    p.get("category", ""))
        self._set_combo(self.formulation_combo, p.get("formulation", ""))

        # Supplier
        sid = p.get("supplier_id")
        for i in range(self.supplier_combo.count()):
            if self.supplier_combo.itemData(i) == sid:
                self.supplier_combo.setCurrentIndex(i)
                break

        self.purchase_price.setValue(p.get("purchase_price", 0) or 0)
        self.sale_price.setValue(p.get("sale_price", 0) or 0)
        self.weight_input.setText(p.get("weight", "") or "")
        self.quantity_input.setValue(p.get("quantity", 0) or 0)
        self.low_stock_input.setValue(p.get("low_stock_threshold", 5) or 5)
        self.mfg_input.setText(p.get("manufacturing_date", "") or "")
        self.expiry_input.setText(p.get("expiry_date", "") or "")

        if self.image_path:
            pix = QPixmap(self.image_path)
            if not pix.isNull():
                self.image_preview.setPixmap(
                    pix.scaled(58, 58, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                )

    @staticmethod
    def _set_combo(combo: QComboBox, value: str):
        idx = combo.findText(value)
        if idx >= 0:
            combo.setCurrentIndex(idx)

    def _select_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.jpg *.jpeg)")
        if path:
            self.image_path = path
            self.image_btn.setText("Image Updated ✓")
            pix = QPixmap(path).scaled(58, 58, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_preview.setPixmap(pix)

    def _save(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Validation", "Product name is required.")
            return

        data = {
            "name":                name,
            "description":         self.desc_input.toPlainText(),
            "brand":               self.brand_combo.currentText(),
            "category":            self.category_combo.currentText(),
            "formulation":         self.formulation_combo.currentText(),
            "purchase_price":      self.purchase_price.value(),
            "sale_price":          self.sale_price.value(),
            "quantity":            self.quantity_input.value(),
            "unit_type":           self.product.get("unit_type", ""),
            "weight":              self.weight_input.text(),
            "supplier_id":         self.supplier_combo.currentData(),
            "manufacturing_date":  self.mfg_input.text().strip() or None,
            "expiry_date":         self.expiry_input.text().strip() or None,
            "low_stock_threshold": self.low_stock_input.value(),
            "image":               self.image_path,
        }

        try:
            update_product(self.product["id"], data)
            QMessageBox.information(self, "Success", "Product updated successfully.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Database Error", str(e))
