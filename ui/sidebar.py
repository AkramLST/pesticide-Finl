from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PySide6.QtCore import Signal, Qt


class Sidebar(QWidget):

    page_changed = Signal(str)

    def __init__(self):
        super().__init__()

        self.setObjectName("Sidebar")
        self.setFixedWidth(220)

        # IMPORTANT: allows stylesheet background to render
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.setStyleSheet("""
#Sidebar {
    background-color: #8bbfb3;
    border: 2px solid #08a680;
}

#Sidebar QPushButton {
    color:#0d47a1;
    background:transparent;
    border:none;
    padding:18px;
    text-align:left;
    font-size:16px;
    font-weight:bold;
}

#Sidebar QPushButton:hover {
    background-color:#1b5e20;
    color:white;
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