from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt


class TopBar(QWidget):

    def __init__(self):
        super().__init__()

        self.setFixedHeight(60)

        # Important for stylesheet background
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.setStyleSheet("""
        background-color: white;
        border-bottom: 1px solid #08a680;
        """)

        layout = QHBoxLayout()
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(10)

        # -------- Logo --------
        logo = QLabel()
        pixmap = QPixmap("images/logo_2.png")
        logo.setPixmap(pixmap.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        # -------- Title --------
        title = QLabel("Jadeed Zarai Markaz")
        title.setStyleSheet("""
            font-size:18px;
            font-weight:bold;
        """)

        # -------- Username --------
        user = QLabel("Akram")
        user.setStyleSheet("""
        font-size:14px;
        color:black;
        """)

        layout.addWidget(logo)
        layout.addWidget(title)
        layout.addStretch()
        layout.addWidget(user)

        self.setLayout(layout)