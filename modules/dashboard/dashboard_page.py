from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame
from PySide6.QtCore import Qt


class DashboardPage(QWidget):

    def __init__(self):
        super().__init__()

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(25)

        title = QLabel("Dashboard")
        title.setStyleSheet("font-size:28px; font-weight:bold;")
        main_layout.addWidget(title)

        # Cards layout
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(20)

        cards_layout.addWidget(self.create_card("Total Items", "43"))
        cards_layout.addWidget(self.create_card("Total Sold Items", "23"))
        cards_layout.addWidget(self.create_card("Total Sales", "34,445 PKR"))

        main_layout.addLayout(cards_layout)

        main_layout.addStretch()

        self.setLayout(main_layout)

    def create_card(self, title, value):

        card = QFrame()
        card.setFixedHeight(120)

        card.setStyleSheet("""
        QFrame{
            background:white;
            border-radius:8px;
            border:1px solid #dcdcdc;
        }
        """)

        layout = QVBoxLayout()

        title_label = QLabel(title)
        title_label.setStyleSheet("font-size:16px; color:gray;")

        value_label = QLabel(value)
        value_label.setStyleSheet("font-size:26px; font-weight:bold;")

        layout.addWidget(title_label)
        layout.addWidget(value_label)
        layout.addStretch()

        card.setLayout(layout)

        return card