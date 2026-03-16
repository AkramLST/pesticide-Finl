from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PySide6.QtCore import Signal, Qt


class Sidebar(QWidget):

    page_changed = Signal(str)

    def __init__(self):
        super().__init__()

        self.setObjectName("Sidebar")
        self.setFixedWidth(220)

        self.setAttribute(Qt.WA_StyledBackground, True)

        self.setStyleSheet("""
#Sidebar {
    background-color: #1f2933;
}

#Sidebar QPushButton {
    color: #e5e7eb;
    background: transparent;
    border: none;
    padding: 16px 20px;
    text-align: left;
    font-size: 15px;
    font-weight: 500;
}

#Sidebar QPushButton:hover {
    background-color: #2d3748;
    color: #22c55e;
}
""")

        layout = QVBoxLayout()

        dashboard_btn = QPushButton("Dashboard")
        products_btn = QPushButton("Products")
        inventory_btn = QPushButton("Inventory")
        sales_btn = QPushButton("Sales")
        suppliers_btn = QPushButton("Suppliers")

        dashboard_btn.clicked.connect(lambda: self.page_changed.emit("dashboard"))
        products_btn.clicked.connect(lambda: self.page_changed.emit("products"))
        inventory_btn.clicked.connect(lambda: self.page_changed.emit("inventory"))
        sales_btn.clicked.connect(lambda: self.page_changed.emit("sales"))
        suppliers_btn.clicked.connect(lambda: self.page_changed.emit("suppliers"))

        layout.addWidget(dashboard_btn)
        layout.addWidget(products_btn)
        layout.addWidget(inventory_btn)
        layout.addWidget(sales_btn)
        layout.addWidget(suppliers_btn)

        layout.addStretch()

        self.setLayout(layout)