from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QStackedWidget
)

from ui.sidebar import Sidebar
from ui.topbar import TopBar

from modules.dashboard.dashboard_page import DashboardPage
from modules.products.product_page import ProductPage
from modules.sales.sales_page import SalesPage
from modules.inventory.stock_page import StockPage
from modules.suppliers.supplier_page import SupplierPage


class DashboardWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Product Of Bht")
        self.showMaximized()

        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0,0,0,0)

        # topbar
        self.topbar = TopBar()
        main_layout.addWidget(self.topbar)

        # main area
        main_area = QHBoxLayout()
        main_area.setContentsMargins(0,0,0,0)
        self.sidebar = Sidebar()
        main_area.addWidget(self.sidebar)

        # stacked pages
        self.pages = QStackedWidget()

        self.dashboard_page = DashboardPage()
        self.products_page = ProductPage()
        self.inventory_page = StockPage()
        self.sales_page = SalesPage()
        self.suppliers_page = SupplierPage()

        self.pages.addWidget(self.dashboard_page)
        self.pages.addWidget(self.products_page)
        self.pages.addWidget(self.inventory_page)
        self.pages.addWidget(self.sales_page)
        self.pages.addWidget(self.suppliers_page)

        main_area.addWidget(self.pages)

        main_layout.addLayout(main_area)

        main_widget.setLayout(main_layout)

        # sidebar signal
        self.sidebar.page_changed.connect(self.change_page)

        # default page
        self.pages.setCurrentIndex(0)

    def change_page(self, page):

        pages = {
            "dashboard":0,
            "products":1,
            "inventory":2,
            "sales":3,
            "suppliers":4
        }

        self.pages.setCurrentIndex(pages[page])
