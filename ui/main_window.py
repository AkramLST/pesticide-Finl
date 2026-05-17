from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QStackedWidget, QMessageBox, QApplication, QGraphicsOpacityEffect
)
from PySide6.QtCore import QPropertyAnimation, QEasingCurve

from widgets.sidebar import Sidebar
from widgets.topbar import TopBar

from pages.dashboard.dashboard_page import DashboardPage
from pages.products.product_page import ProductPage
from pages.inventory.inventory_page import InventoryPage
from pages.sales.sales_page import SalesPage
from pages.customers.customers_page import CustomersPage
from pages.suppliers.suppliers_page import SuppliersPage
from pages.users.users_page import UsersPage
from pages.settings.settings_page import SettingsPage

from utils.session import session

PAGE_INDEX = {
    "dashboard": 0,
    "products":  1,
    "inventory": 2,
    "sales":     3,
    "customers": 4,
    "suppliers": 5,
    "users":     6,
    "settings":  7,
}


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Jadeed Zarai Markaz — Pesticide Management")
        self.showMaximized()

        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.topbar = TopBar()
        self.topbar.logout_requested.connect(self._logout)
        main_layout.addWidget(self.topbar)

        main_area = QHBoxLayout()
        main_area.setContentsMargins(0, 0, 0, 0)
        main_area.setSpacing(0)

        self.sidebar = Sidebar()
        self.sidebar.page_changed.connect(self._change_page)
        main_area.addWidget(self.sidebar)

        self.pages = QStackedWidget()
        self.pages.addWidget(DashboardPage())
        self.pages.addWidget(ProductPage())
        self.pages.addWidget(InventoryPage())
        self.pages.addWidget(SalesPage())
        self.pages.addWidget(CustomersPage())
        self.pages.addWidget(SuppliersPage())
        self.pages.addWidget(UsersPage())
        self.pages.addWidget(SettingsPage())

        # Attach fade effect to the stacked widget content area
        self._opacity_effect = QGraphicsOpacityEffect(self.pages)
        self.pages.setGraphicsEffect(self._opacity_effect)
        self._fade_anim = QPropertyAnimation(self._opacity_effect, b"opacity")
        self._fade_anim.setDuration(180)
        self._fade_anim.setEasingCurve(QEasingCurve.InOutQuad)
        self._fade_connected = False

        main_area.addWidget(self.pages)
        main_layout.addLayout(main_area)
        main_widget.setLayout(main_layout)

        self.pages.setCurrentIndex(0)

    def _change_page(self, key: str):
        idx = PAGE_INDEX.get(key, 0)
        if idx == self.pages.currentIndex():
            return
        # Fade out → switch → fade in
        self._fade_anim.stop()
        if self._fade_connected:
            try:
                self._fade_anim.finished.disconnect()
            except RuntimeError:
                pass
            self._fade_connected = False
        self._fade_anim.setStartValue(1.0)
        self._fade_anim.setEndValue(0.0)
        self._fade_anim.finished.connect(lambda: self._finish_switch(idx))
        self._fade_connected = True
        self._fade_anim.start()

    def _finish_switch(self, idx: int):
        self.pages.setCurrentIndex(idx)
        try:
            self._fade_anim.finished.disconnect()
        except RuntimeError:
            pass
        self._fade_connected = False
        self._fade_anim.setStartValue(0.0)
        self._fade_anim.setEndValue(1.0)
        self._fade_anim.start()

    def _logout(self):
        reply = QMessageBox.question(
            self, "Logout", "Are you sure you want to logout?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            session.logout()
            from pages.login_page import LoginWindow
            # Store on QApplication so LoginWindow survives MainWindow closing
            app = QApplication.instance()
            app._login_window = LoginWindow()
            app._login_window.show()
            self.close()
