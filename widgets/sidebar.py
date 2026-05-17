from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout
from PySide6.QtCore import Signal, Qt, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QCursor

EXPANDED_WIDTH  = 220
COLLAPSED_WIDTH = 58

MENU_ITEMS = [
    ("dashboard", "🏠", "Dashboard"),
    ("products",  "📦", "Products"),
    ("inventory", "🗃", "Inventory"),
    ("sales",     "🛒", "Sales"),
    ("customers", "👥", "Customers"),
    ("suppliers", "🚚", "Suppliers"),
    ("users",     "👤", "Users"),
    ("settings",  "⚙",  "Settings"),
]

_STYLE = """
#Sidebar {
    background-color: #1f2933;
}
#sidebarLogo {
    color: #22c55e;
    font-size: 15px;
    font-weight: bold;
    padding: 16px 14px 8px 14px;
}
#toggleBtn {
    background: #2d3748;
    border: none;
    color: #94a3b8;
    font-size: 16px;
    padding: 8px;
    border-radius: 6px;
    margin: 0 10px 8px 10px;
}
#toggleBtn:hover { color: #22c55e; background:#374151; }
#Sidebar QPushButton[role="nav"] {
    color: #cbd5e0;
    background: transparent;
    border: none;
    border-left: 3px solid transparent;
    padding: 13px 14px;
    text-align: left;
    font-size: 14px;
    font-weight: 500;
}
#Sidebar QPushButton[role="nav"]:hover {
    background-color: #2d3748;
    color: #22c55e;
    border-left: 3px solid #22c55e;
}
#Sidebar QPushButton[role="nav"][active="true"] {
    background-color: #2d3748;
    color: #22c55e;
    border-left: 3px solid #22c55e;
    font-weight: 700;
}
"""


class Sidebar(QWidget):

    page_changed = Signal(str)

    def __init__(self):
        super().__init__()
        self.setObjectName("Sidebar")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(_STYLE)
        self.setMinimumWidth(0)
        self.setMaximumWidth(EXPANDED_WIDTH)
        self._expanded = True

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Logo row + toggle button
        top_row = QHBoxLayout()
        top_row.setContentsMargins(0, 0, 0, 0)
        top_row.setSpacing(0)

        self._logo = QLabel("🌿 Zarai Markaz")
        self._logo.setObjectName("sidebarLogo")

        self._toggle_btn = QPushButton("◀")
        self._toggle_btn.setObjectName("toggleBtn")
        self._toggle_btn.setFixedSize(32, 32)
        self._toggle_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self._toggle_btn.clicked.connect(self.toggle)

        top_row.addWidget(self._logo)
        top_row.addStretch()
        top_row.addWidget(self._toggle_btn)

        layout.addLayout(top_row)

        # ── Nav buttons
        self._buttons: dict[str, QPushButton] = {}
        self._labels:  dict[str, str]          = {}

        for key, icon, label in MENU_ITEMS:
            btn = QPushButton(f"{icon}  {label}")
            btn.setProperty("role", "nav")
            btn.setProperty("active", "false")
            btn.setCursor(QCursor(Qt.PointingHandCursor))
            btn.clicked.connect(lambda checked=False, k=key: self._on_click(k))
            layout.addWidget(btn)
            self._buttons[key]  = btn
            self._labels[key]   = (icon, label)

        layout.addStretch()
        self.setLayout(layout)
        self._set_active("dashboard")

        # ── Collapse animation
        self._anim = QPropertyAnimation(self, b"maximumWidth")
        self._anim.setDuration(220)
        self._anim.setEasingCurve(QEasingCurve.InOutCubic)

    # ──────────────────────────────────────────────────────
    def toggle(self):
        if self._expanded:
            self._anim.setStartValue(EXPANDED_WIDTH)
            self._anim.setEndValue(COLLAPSED_WIDTH)
            self._toggle_btn.setText("▶")
            self._logo.setVisible(False)
            for key, btn in self._buttons.items():
                icon, _ = self._labels[key]
                btn.setText(icon)
        else:
            self._anim.setStartValue(COLLAPSED_WIDTH)
            self._anim.setEndValue(EXPANDED_WIDTH)
            self._toggle_btn.setText("◀")
            self._logo.setVisible(True)
            for key, btn in self._buttons.items():
                icon, label = self._labels[key]
                btn.setText(f"{icon}  {label}")

        self._expanded = not self._expanded
        self._anim.start()

    def _on_click(self, key: str):
        self._set_active(key)
        self.page_changed.emit(key)

    def _set_active(self, key: str):
        for k, btn in self._buttons.items():
            btn.setProperty("active", "true" if k == key else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)
