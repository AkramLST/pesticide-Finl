from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QPushButton
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, Signal

from utils.session import session
from utils.config import APP_NAME


class TopBar(QWidget):

    logout_requested = Signal()

    def __init__(self):
        super().__init__()
        self.setFixedHeight(60)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("""
            background-color: white;
            border-bottom: 2px solid #2e7d32;
        """)

        layout = QHBoxLayout()
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(10)

        logo = QLabel()
        pixmap = QPixmap("images/logo_2.png")
        if not pixmap.isNull():
            logo.setPixmap(pixmap.scaled(38, 38, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        title = QLabel(APP_NAME)
        title.setStyleSheet("font-size:18px; font-weight:bold; color:#1a202c;")

        self.user_label = QLabel()
        self.user_label.setStyleSheet("font-size:13px; color:#2e7d32; font-weight:600;")
        self.refresh_user()

        logout_btn = QPushButton("Logout")
        logout_btn.setStyleSheet("""
            QPushButton {
                background: #e53e3e;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 6px 14px;
                font-size: 13px;
            }
            QPushButton:hover { background: #c53030; }
        """)
        logout_btn.clicked.connect(self.logout_requested.emit)

        layout.addWidget(logo)
        layout.addWidget(title)
        layout.addStretch()
        layout.addWidget(self.user_label)
        layout.addWidget(logout_btn)
        self.setLayout(layout)

    def refresh_user(self):
        if session.is_logged_in:
            self.user_label.setText(f"👤 {session.name}  [{session.role}]")
        else:
            self.user_label.setText("")
