from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QTextEdit,
    QPushButton, QComboBox, QFileDialog, QFormLayout,
    QMessageBox, QSpinBox, QDoubleSpinBox
)


from database.db import insert_product


class AddProductDialog(QDialog):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Add Product")
        self.resize(450, 500)

        self.image_path = ""

        main_layout = QVBoxLayout()

        title = QLabel("Add New Product")
        title.setStyleSheet("font-size:20px; font-weight:bold;")

        form_layout = QFormLayout()

        # Product Name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter product name")

        # Description (LIMITED SIZE)
        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("Enter product description")
        self.desc_input.setFixedHeight(70)  # 👈 makes it ~3 rows

        # Brand Dropdown
        self.brand_combo = QComboBox()
        self.brand_combo.addItems([
            "Bayer",
            "Syngenta",
            "FMC",
            "Corteva",
            "UPL",
            "Adama"
        ])

        # Category
        self.category_combo = QComboBox()
        self.category_combo.addItems([
            "Insecticide",
            "Herbicide",
            "Fungicide",
            "Rodenticide"
        ])

        # Formulation
        self.formulation_combo = QComboBox()
        self.formulation_combo.addItems([
            "Liquid",
            "Powder",
            "Granules",
            "Spray"
        ])

        # Price
        self.price_input = QDoubleSpinBox()
        self.price_input.setRange(0, 100000)
        self.price_input.setPrefix("Rs ")
        self.price_input.setDecimals(2)

        # Weight (single unit)
        self.weight_input = QLineEdit()
        self.weight_input.setPlaceholderText("e.g. 500ml, 1kg")

        # Quantity
        self.quantity_input = QSpinBox()
        self.quantity_input.setRange(0, 10000)

        # Image Upload
        self.image_btn = QPushButton("Upload Product Image")
        self.image_btn.clicked.connect(self.select_image)

        # Save Button
        save_btn = QPushButton("Save Product")
        save_btn.clicked.connect(self.save_product)

        # Add fields
        form_layout.addRow("Product Name:", self.name_input)
        form_layout.addRow("Description:", self.desc_input)
        form_layout.addRow("Brand:", self.brand_combo)
        form_layout.addRow("Category:", self.category_combo)
        form_layout.addRow("Formulation:", self.formulation_combo)
        form_layout.addRow("Price:", self.price_input)
        form_layout.addRow("Weight:", self.weight_input)
        form_layout.addRow("Quantity:", self.quantity_input)
        form_layout.addRow("Product Image:", self.image_btn)

        main_layout.addWidget(title)
        main_layout.addLayout(form_layout)
        main_layout.addWidget(save_btn)

        self.setLayout(main_layout)

    def select_image(self):

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Product Image",
            "",
            "Images (*.png *.jpg *.jpeg)"
        )

        if file_path:
            self.image_path = file_path
            self.image_btn.setText("Image Selected")

    def save_product(self):

        name = self.name_input.text()
        description = self.desc_input.toPlainText()
        brand = self.brand_combo.currentText()
        category = self.category_combo.currentText()
        formulation = self.formulation_combo.currentText()
        price = self.price_input.value()
        weight = self.weight_input.text()
        quantity = self.quantity_input.value()
        image = self.image_path

        if name == "":
            QMessageBox.warning(self, "Error", "Product Name is required")
            return

        data = (
            name, description, brand, category,
            formulation, price, weight, quantity, image
        )

        try:
            insert_product(data)
            QMessageBox.information(self, "Success", "Product Added Successfully")
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Database Error", str(e))


