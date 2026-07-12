from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QTextEdit,
    QPushButton, QComboBox, QFileDialog, QFormLayout,
    QMessageBox, QSpinBox, QDoubleSpinBox, QHBoxLayout, QCheckBox
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

from models.product_model import insert_product
from models.supplier_model import get_all_suppliers
from models.brand_model import get_all_brands
from utils.config import PRODUCT_CATEGORIES, PRODUCT_SUBCATEGORIES, FORMULATIONS


class AddProductDialog(QDialog):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Add Product")
        self.resize(480, 560)
        self.image_path = ""

        main_layout = QVBoxLayout()
        title = QLabel("Add New Product")
        title.setStyleSheet("font-size:20px; font-weight:bold;")

        form = QFormLayout()
        form.setSpacing(10)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter product name")

        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("Enter product description")
        self.desc_input.setFixedHeight(70)

        self.brand_combo = QComboBox()
        self._load_brands()

        self.category_combo = QComboBox()
        self.category_combo.addItems(PRODUCT_CATEGORIES)
        self.category_combo.currentTextChanged.connect(self._load_subcategories)

        self.subcategory_combo = QComboBox()
        self._load_subcategories(self.category_combo.currentText())

        self.formulation_combo = QComboBox()
        self.formulation_combo.addItems(FORMULATIONS)

        self.supplier_combo = QComboBox()
        self.supplier_combo.addItem("— None —", None)
        for s in get_all_suppliers():
            self.supplier_combo.addItem(s["name"], s["id"])

        self.purchase_price = QDoubleSpinBox()
        self.purchase_price.setRange(0, 1000000)
        self.purchase_price.setPrefix("Rs ")
        self.purchase_price.setDecimals(2)

        self.sale_price = QDoubleSpinBox()
        self.sale_price.setRange(0, 1000000)
        self.sale_price.setPrefix("Rs ")
        self.sale_price.setDecimals(2)

        self.weight_input = QLineEdit()
        self.weight_input.setPlaceholderText("e.g. 500ml, 1kg")

        self.quantity_input = QSpinBox()
        self.quantity_input.setRange(0, 100000)

        self.low_stock_input = QSpinBox()
        self.low_stock_input.setRange(0, 10000)
        self.low_stock_input.setValue(5)

        self.secret_checkbox = QCheckBox("Mark as secret product")

        self.mfg_input = QLineEdit()
        self.mfg_input.setPlaceholderText("YYYY-MM-DD")

        self.expiry_input = QLineEdit()
        self.expiry_input.setPlaceholderText("YYYY-MM-DD")

        img_row = QHBoxLayout()
        self.image_btn = QPushButton("Upload Image")
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
        form.addRow("Sub-Category:", self.subcategory_combo)
        form.addRow("Formulation:", self.formulation_combo)
        form.addRow("Supplier:", self.supplier_combo)
        form.addRow("Purchase Price:", self.purchase_price)
        form.addRow("Sale Price:", self.sale_price)
        form.addRow("Weight/Unit:", self.weight_input)
        form.addRow("Quantity:", self.quantity_input)
        form.addRow("Low Stock At:", self.low_stock_input)
        form.addRow("", self.secret_checkbox)
        form.addRow("Mfg Date:", self.mfg_input)
        form.addRow("Expiry Date:", self.expiry_input)
        form.addRow("Image:", img_row)

        save_btn = QPushButton("Save Product")
        save_btn.setStyleSheet("""
            QPushButton { background:#2e7d32; color:white; padding:10px;
                border-radius:8px; font-size:14px; font-weight:bold; }
            QPushButton:hover { background:#1b5e20; }
        """)
        save_btn.clicked.connect(self._save)

        main_layout.addWidget(title)
        main_layout.addLayout(form)
        main_layout.addWidget(save_btn)
        self.setLayout(main_layout)

    def _select_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.jpg *.jpeg)")
        if path:
            self.image_path = path
            self.image_btn.setText("Image Selected ✓")
            pix = QPixmap(path).scaled(58, 58, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_preview.setPixmap(pix)

    def _load_brands(self):
        self.brand_combo.clear()
        brands = get_all_brands()
        if not brands:
            self.brand_combo.addItem("Other")
            return
        for brand in brands:
            self.brand_combo.addItem(brand["name"])

    def _load_subcategories(self, category: str):
        current = self.subcategory_combo.currentText() if hasattr(self, "subcategory_combo") else ""
        self.subcategory_combo.blockSignals(True)
        self.subcategory_combo.clear()
        self.subcategory_combo.addItems(PRODUCT_SUBCATEGORIES.get(category, ["Other"]))
        if current:
            idx = self.subcategory_combo.findText(current)
            if idx >= 0:
                self.subcategory_combo.setCurrentIndex(idx)
        self.subcategory_combo.blockSignals(False)

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
            "sub_category":        self.subcategory_combo.currentText(),
            "formulation":         self.formulation_combo.currentText(),
            "purchase_price":      self.purchase_price.value(),
            "sale_price":          self.sale_price.value(),
            "quantity":            self.quantity_input.value(),
            "unit_type":           "",
            "weight":              self.weight_input.text(),
            "supplier_id":         self.supplier_combo.currentData(),
            "manufacturing_date":  self.mfg_input.text().strip() or None,
            "expiry_date":         self.expiry_input.text().strip() or None,
            "low_stock_threshold": self.low_stock_input.value(),
            "secret_product":      1 if self.secret_checkbox.isChecked() else 0,
            "image":               self.image_path,
        }

        try:
            insert_product(data)
            QMessageBox.information(self, "Success", "Product added successfully.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Database Error", str(e))
