from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QGridLayout, QScrollArea
)

from modules.products.add_product import AddProductDialog
from modules.products.product_card import ProductCard
from database.db import get_products


class ProductPage(QWidget):

    def __init__(self):
        super().__init__()

        # Set object name for stylesheet
        self.setObjectName("productPage")

        # Background image
        self.setStyleSheet("""
        #productPage {
            background-image: url(images/dss.jpg);
            background-position: center;
            background-repeat: no-repeat;
        }
        """)

        main_layout = QVBoxLayout()

        title = QLabel("Products")
        title.setStyleSheet("font-size:24px; font-weight:bold;")

        add_btn = QPushButton("Add Product")
        add_btn.clicked.connect(self.open_add_product)

        # Scroll Area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)

        # Make scroll area transparent
        self.scroll.setStyleSheet("""
        QScrollArea {
            background: transparent;
            border: none;
        }
        QScrollArea > QWidget > QWidget {
            background: transparent;
        }
        """)

        # Container widget
        self.container = QWidget()
        self.container.setStyleSheet("background: transparent;")

        # Grid layout for product cards
        self.grid = QGridLayout()
        self.grid.setSpacing(15)

        self.container.setLayout(self.grid)
        self.scroll.setWidget(self.container)

        main_layout.addWidget(title)
        main_layout.addWidget(add_btn)
        main_layout.addWidget(self.scroll)

        self.setLayout(main_layout)

        self.load_products()

    def load_products(self):
        products = get_products()

        # Clear previous cards
        for i in reversed(range(self.grid.count())):
            widget = self.grid.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        row = 0
        col = 0

        for product in products:
            card = ProductCard(product)
            self.grid.addWidget(card, row, col)

            col += 1
            if col == 3:
                col = 0
                row += 1

    def open_add_product(self):
        dialog = AddProductDialog()

        if dialog.exec():
            self.load_products()



