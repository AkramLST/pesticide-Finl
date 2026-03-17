from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QHBoxLayout, QMessageBox
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

from database.db import delete_product


class ProductCard(QWidget):

    def __init__(self, product, refresh_callback=None):
        super().__init__()

        self.product = product
        self.refresh_callback = refresh_callback

        self.setObjectName("productCard")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setFixedSize(340, 340)

        layout = QVBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(6)

        # Image
        image_label = QLabel()
        image_label.setFixedHeight(150)
        image_label.setAlignment(Qt.AlignCenter)

        if product[9]:  # updated index
            pixmap = QPixmap(product[9])
            image_label.setPixmap(
                pixmap.scaled(200, 140, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
        else:
            image_label.setText("No Image")

        # Info
        name = QLabel(product[1])
        name.setStyleSheet("font-size:16px; font-weight:bold;")

        brand = QLabel(f"Brand: {product[3]}")
        category = QLabel(f"Category: {product[4]}")
        formulation = QLabel(f"Formulation: {product[5]}")
        price = QLabel(f"Price: Rs {product[6]}")

        # Buttons
        btn_layout = QHBoxLayout()

        edit_btn = QPushButton("Edit")
        edit_btn.setStyleSheet("background-color: #4CAF50; color: white;")

        delete_btn = QPushButton("Delete")
        delete_btn.setStyleSheet("background-color: red; color: white;")
        delete_btn.clicked.connect(self.delete_product)

        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(delete_btn)

        # Add to layout
        layout.addWidget(image_label)
        layout.addWidget(name)
        layout.addWidget(brand)
        layout.addWidget(category)
        layout.addWidget(formulation)
        layout.addWidget(price)
        layout.addStretch()
        layout.addLayout(btn_layout)

        self.setLayout(layout)

        self.setStyleSheet("""
        #productCard {
            background-color: white;
            border: 2px solid black;
            border-radius: 12px;
        }

        QLabel {
            background: transparent;
        }
        """)

    def delete_product(self):
        confirm = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete this product?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            try:
                delete_product(self.product[0])  # ID
                QMessageBox.information(self, "Deleted", "Product deleted successfully")

                if self.refresh_callback:
                    self.refresh_callback()

            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

