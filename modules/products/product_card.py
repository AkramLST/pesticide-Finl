from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt


class ProductCard(QWidget):

    def __init__(self, product):
        super().__init__()

        self.setObjectName("productCard")
        self.setAttribute(Qt.WA_StyledBackground, True)  # IMPORTANT
        self.setFixedSize(340, 300) 
        layout = QVBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(6)

        # Product Image
        image_label = QLabel()
        image_label.setFixedHeight(150)
        image_label.setAlignment(Qt.AlignCenter)

        if product[7]:
            pixmap = QPixmap(product[7])
            image_label.setPixmap(
                pixmap.scaled(200, 140, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
        else:
            image_label.setText("No Image")

        # Product Name
        name = QLabel(product[1])
        name.setStyleSheet("font-size:16px; font-weight:bold;")

        brand = QLabel(f"Brand: {product[3]}")
        category = QLabel(f"Category: {product[4]}")
        formulation = QLabel(f"Formulation: {product[6]}")

        layout.addWidget(image_label)
        layout.addWidget(name)
        layout.addWidget(brand)
        layout.addWidget(category)
        layout.addWidget(formulation)

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
