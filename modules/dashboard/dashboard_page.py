from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame, QSizePolicy
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap


class DashboardPage(QWidget):
    def __init__(self):
        super().__init__()

        # Main vertical layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ======================
        # Background Image Frame
        # ======================
        bg_frame = QFrame()
        bg_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        bg_layout = QVBoxLayout()
        bg_layout.setContentsMargins(0, 0, 0, 0)
        bg_layout.setSpacing(0)
        bg_frame.setLayout(bg_layout)

        # Background image
        bg_label = QLabel()
        bg_pixmap = QPixmap("images/dss.jpg")  # Path to your image
        bg_label.setPixmap(bg_pixmap)
        bg_label.setScaledContents(True)
        bg_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Overlay container for cards
        overlay_widget = QWidget(bg_label)  # parent is bg_label
        overlay_layout = QHBoxLayout()
        overlay_layout.setContentsMargins(20, 20, 20, 20)
        overlay_layout.setSpacing(20)
        overlay_layout.setAlignment(Qt.AlignBottom)  # Cards aligned at bottom
        overlay_widget.setLayout(overlay_layout)

        # Add cards
        overlay_layout.addWidget(self.create_card("Total Items", "43", "#3498db"))
        overlay_layout.addWidget(self.create_card("Total Sold Items", "23", "#1abc9c"))
        overlay_layout.addWidget(self.create_card("Total Sales", "34,445 PKR", "#9b59b6"))

        # Add background image to frame
        bg_layout.addWidget(bg_label)
        main_layout.addWidget(bg_frame)

        self.setLayout(main_layout)

    def create_card(self, title, value, color):
        card = QFrame()
        card.setFixedSize(200, 120)
        card.setStyleSheet(f"""
            QFrame {{
                background: white;
                border-radius: 12px;
                border: 1px solid #dce3e8;
            }}
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(5)

        title_label = QLabel(title)
        title_label.setStyleSheet(f"font-size:16px; font-weight:600; color:{color};")
        value_label = QLabel(value)
        value_label.setStyleSheet("font-size:26px; font-weight:bold; color:#2c3e50;")

        layout.addWidget(title_label)
        layout.addWidget(value_label)
        layout.addStretch()
        card.setLayout(layout)

        return card