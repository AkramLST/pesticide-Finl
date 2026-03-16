from PySide6.QtWidgets import (
    QMainWindow, QWidget, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
from ui.dashboard_window import DashboardWindow


USERNAME = "dmin"
PASSWORD = "234"


class LoginWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Login")

        self.setWindowFlags(
            Qt.Window |
            Qt.WindowMinimizeButtonHint |
            Qt.WindowCloseButtonHint
        )

        self.showMaximized()

        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # Background
        background = QLabel()
        background.setPixmap(QPixmap("images/pesti.png"))
        background.setScaledContents(True)

        # Login Card
        card = QWidget()
        card.setFixedWidth(350)

        card.setStyleSheet("""
        QWidget{
            background-color: rgba(255,255,255,0.95);
            border-radius:15px;
        }

        QLineEdit{
            padding:10px;
            border:1px solid #ccc;
            border-radius:6px;
        }

        QPushButton{
            background-color:#2e7d32;
            color:white;
            padding:10px;
            border-radius:6px;
            font-weight:bold;
        }
        """)

        layout = QVBoxLayout()

        title = QLabel("Pesticide Inventory System")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size:22px;font-weight:bold")

        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")

        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.Password)

        login_btn = QPushButton("Login")
        login_btn.clicked.connect(self.login)

        layout.addWidget(title)
        layout.addSpacing(20)
        layout.addWidget(self.username)
        layout.addWidget(self.password)
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

    def login(self):

        if self.username.text() == USERNAME and self.password.text() == PASSWORD:

            self.dashboard = DashboardWindow()
            self.dashboard.show()

            self.close()

        else:
            QMessageBox.warning(self, "Error", "Invalid credentials")
