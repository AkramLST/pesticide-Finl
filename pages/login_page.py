from PySide6.QtWidgets import (
    QMainWindow, QWidget, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox, QCheckBox
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

from models.user_model import get_user_by_credentials, update_last_login
from utils.session import session
from utils.logger import get_logger

log = get_logger(__name__)


class LoginWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login — Jadeed Zarai Markaz")
        self.setWindowFlags(
            Qt.Window |
            Qt.WindowMinimizeButtonHint |
            Qt.WindowCloseButtonHint
        )
        self.showMaximized()

        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        background = QLabel()
        background.setPixmap(QPixmap("images/pesti.png"))
        background.setScaledContents(True)

        card = QWidget()
        card.setFixedWidth(380)
        card.setStyleSheet("""
        QWidget {
            background-color: rgba(255,255,255,0.97);
            border-radius: 16px;
        }
        QLabel#cardTitle {
            font-size: 22px;
            font-weight: bold;
            color: #1a202c;
        }
        QLabel#cardSub {
            font-size: 13px;
            color: #718096;
        }
        QLineEdit {
            padding: 11px 14px;
            border: 1.5px solid #e2e8f0;
            border-radius: 8px;
            font-size: 14px;
            background: #f7fafc;
        }
        QLineEdit:focus {
            border-color: #2e7d32;
            background: white;
        }
        QPushButton#loginBtn {
            background-color: #2e7d32;
            color: white;
            padding: 12px;
            border-radius: 8px;
            font-size: 15px;
            font-weight: bold;
            border: none;
        }
        QPushButton#loginBtn:hover {
            background-color: #1b5e20;
        }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(36, 36, 36, 36)
        layout.setSpacing(14)

        title = QLabel("Pesticide Inventory System")
        title.setObjectName("cardTitle")
        title.setAlignment(Qt.AlignCenter)

        sub = QLabel("Sign in to your account")
        sub.setObjectName("cardSub")
        sub.setAlignment(Qt.AlignCenter)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")

        pwd_row = QHBoxLayout()
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)

        self.toggle_btn = QPushButton("👁")
        self.toggle_btn.setFixedSize(38, 38)
        self.toggle_btn.setStyleSheet(
            "QPushButton { background: transparent; border: none; font-size:16px; }"
        )
        self.toggle_btn.clicked.connect(self._toggle_password)

        pwd_row.addWidget(self.password_input)
        pwd_row.addWidget(self.toggle_btn)

        login_btn = QPushButton("Login")
        login_btn.setObjectName("loginBtn")
        login_btn.clicked.connect(self.login)
        self.password_input.returnPressed.connect(self.login)

        layout.addWidget(title)
        layout.addWidget(sub)
        layout.addSpacing(8)
        layout.addWidget(QLabel("Username"))
        layout.addWidget(self.username_input)
        layout.addWidget(QLabel("Password"))
        layout.addLayout(pwd_row)
        layout.addSpacing(4)
        layout.addWidget(login_btn)

        card.setLayout(layout)

        main_layout = QVBoxLayout(main_widget)
        main_layout.addWidget(background)

        overlay = QVBoxLayout(background)
        overlay.addStretch()
        row = QHBoxLayout()
        row.addStretch()
        row.addWidget(card)
        row.addStretch()
        overlay.addLayout(row)
        overlay.addStretch()

    def _toggle_password(self):
        if self.password_input.echoMode() == QLineEdit.Password:
            self.password_input.setEchoMode(QLineEdit.Normal)
            self.toggle_btn.setText("🙈")
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            self.toggle_btn.setText("👁")

    def login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(self, "Error", "Please enter username and password.")
            return

        user = get_user_by_credentials(username, password)

        if user:
            session.login(user)
            update_last_login(user["id"])
            log.info(f"Login: {username}")

            from ui.main_window import MainWindow
            from PySide6.QtWidgets import QApplication
            # Store on QApplication so the window survives LoginWindow being closed
            app = QApplication.instance()
            app._main_window = MainWindow()
            app._main_window.show()
            self.close()
        else:
            log.warning(f"Failed login attempt: {username}")
            QMessageBox.warning(self, "Login Failed", "Invalid username or password.")
