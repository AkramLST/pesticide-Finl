from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QTextEdit,
    QPushButton, QComboBox, QFileDialog, QFormLayout, QMessageBox
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

        # Description
        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("Enter product description")

        # Brand
        self.brand_input = QLineEdit()
        self.brand_input.setPlaceholderText("e.g. Bayer AG, Syngenta")

        # Category
        self.category_combo = QComboBox()
        self.category_combo.addItems([
            "Insecticide",
            "Herbicide",
            "Fungicide",
            "Rodenticide"
        ])

        # Active Ingredient
        self.active_input = QLineEdit()
        self.active_input.setPlaceholderText("Active Ingredient")

        # Formulation
        self.formulation_combo = QComboBox()
        self.formulation_combo.addItems([
            "Liquid",
            "Powder",
            "Granules",
            "Spray"
        ])

        # Image Upload Button
        self.image_btn = QPushButton("Upload Product Image")
        self.image_btn.clicked.connect(self.select_image)

        # Save Button
        save_btn = QPushButton("Save Product")
        save_btn.clicked.connect(self.save_product)

        # Form Fields
        form_layout.addRow("Product Name:", self.name_input)
        form_layout.addRow("Description:", self.desc_input)
        form_layout.addRow("Brand:", self.brand_input)
        form_layout.addRow("Category:", self.category_combo)
        form_layout.addRow("Active Ingredient:", self.active_input)
        form_layout.addRow("Formulation:", self.formulation_combo)
        form_layout.addRow("Product Image:", self.image_btn)

        main_layout.addWidget(title)
        main_layout.addLayout(form_layout)
        main_layout.addWidget(save_btn)

        self.setLayout(main_layout)

    # Image selection
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

    # Save product
    def save_product(self):

        name = self.name_input.text()
        description = self.desc_input.toPlainText()
        brand = self.brand_input.text()
        category = self.category_combo.currentText()
        active = self.active_input.text()
        formulation = self.formulation_combo.currentText()
        image = self.image_path

        if name == "":
            QMessageBox.warning(self, "Error", "Product Name is required")
            return

        data = (
            name,
            description,
            brand,
            category,
            active,
            formulation,
            image
        )

        try:

            insert_product(data)

            QMessageBox.information(self, "Success", "Product Added Successfully")

            self.accept()

        except Exception as e:

            QMessageBox.critical(self, "Database Error", str(e))

