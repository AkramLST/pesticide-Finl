from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Signal, Qt


MENU_ITEMS = [
    ("dashboard",  "🏠  Dashboard"),
    ("products",   "📦  Products"),
    ("inventory",  "🗃  Inventory"),
    ("sales",      "🛒  Sales"),
    ("customers",  "👥  Customers"),
    ("suppliers",  "🚚  Suppliers"),
    ("users",      "👤  Users"),
    ("settings",   "⚙  Settings"),
]


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
        #sidebarLogo {
            color: #22c55e;
            font-size: 16px;
            font-weight: bold;
            padding: 18px 20px 10px 20px;
        }
        #Sidebar QPushButton {
            color: #cbd5e0;
            background: transparent;
            border: none;
            border-left: 3px solid transparent;
            padding: 14px 20px;
            text-align: left;
            font-size: 14px;
            font-weight: 500;
        }
        #Sidebar QPushButton:hover {
            background-color: #2d3748;
            color: #22c55e;
            border-left: 3px solid #22c55e;
        }
        #Sidebar QPushButton[active="true"] {
            background-color: #2d3748;
            color: #22c55e;
            border-left: 3px solid #22c55e;
            font-weight: 700;
        }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        logo = QLabel("🌿 Zarai Markaz")
        logo.setObjectName("sidebarLogo")
        layout.addWidget(logo)

        self._buttons: dict[str, QPushButton] = {}

        for key, label in MENU_ITEMS:
            btn = QPushButton(label)
            btn.setProperty("active", "false")
            btn.clicked.connect(lambda checked=False, k=key: self._on_click(k))
            layout.addWidget(btn)
            self._buttons[key] = btn

        layout.addStretch()
        self.setLayout(layout)

        self._set_active("dashboard")

    def _on_click(self, key: str):
        self._set_active(key)
        self.page_changed.emit(key)

    def _set_active(self, key: str):
        for k, btn in self._buttons.items():
            btn.setProperty("active", "true" if k == key else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)
