from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QFrame, QSizePolicy, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QColor


class DashboardPage(QWidget):
    def __init__(self):
        super().__init__()

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ======================
        # Background Frame
        # ======================
        bg_frame = QFrame()
        bg_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        bg_layout = QVBoxLayout()
        bg_layout.setContentsMargins(0, 0, 0, 0)
        bg_frame.setLayout(bg_layout)

        # Background image
        bg_label = QLabel()
        bg_pixmap = QPixmap("images/dss.jpg")
        bg_label.setPixmap(bg_pixmap)
        bg_label.setScaledContents(True)

        # 🌑 Dark overlay for readability
        bg_label.setStyleSheet("""
            QLabel {
                background-color: rgba(0, 0, 0, 80);
            }
        """)

        # Overlay widget (cards container)
        overlay_widget = QWidget(bg_label)
        overlay_layout = QVBoxLayout()
        overlay_layout.setContentsMargins(30, 30, 30, 40)
        overlay_layout.setSpacing(20)
        overlay_layout.setAlignment(Qt.AlignTop)
        overlay_widget.setLayout(overlay_layout)

# Row 1
        row1 = QHBoxLayout()
        row1.setSpacing(25)
        row1.setAlignment(Qt.AlignLeft)

        row1.addWidget(self.create_card("Total Items", "43", "#00c6ff"))
        row1.addWidget(self.create_card("Total Sold Items", "23", "#00ffb3"))
        row1.addWidget(self.create_card("Total Sales", "34,445 PKR", "#b388ff"))

# Row 2
        row2 = QHBoxLayout()
        row2.setSpacing(25)
        row2.setAlignment(Qt.AlignLeft)

        row2.addWidget(self.create_card("Pending Items", "78", "#ff7675"))
        row2.addWidget(self.create_card("Total Sales This Week", "22,445 PKR", "#74b9ff"))
        row2.addWidget(self.create_card("Most Sold Item", "Product A", "#55efc4"))

# Add rows to main overlay
        overlay_layout.addLayout(row1)
        overlay_layout.addLayout(row2)
        bg_layout.addWidget(bg_label)
        main_layout.addWidget(bg_frame)

        self.setLayout(main_layout)

    # ======================
    # Card Component
    # ======================
    def create_card(self, title, value, color):
        card = QFrame()
        card.setFixedSize(240, 130)

        # Glass effect
        card.setStyleSheet(f"""
            QFrame {{
                background: rgba(20, 25, 30, 0.75);
                border-radius: 16px;
                border: 1px solid rgba(255, 255, 255, 0.15);
            }}
        """)

        # Shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(18)
        shadow.setXOffset(0)
        shadow.setYOffset(6)
        shadow.setColor(QColor(0, 0, 0, 150))
        card.setGraphicsEffect(shadow)

        layout = QVBoxLayout()
        layout.setContentsMargins(18, 15, 18, 15)
        layout.setSpacing(6)

        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            font-size: 14px;
            font-weight: 600;
            color: {color};
        """)

        # Value
        value_label = QLabel(value)
        value_label.setStyleSheet("""
            font-size: 26px;
            font-weight: bold;
            color: #ecf0f1;
        """)

        layout.addWidget(title_label)
        layout.addWidget(value_label)
        layout.addStretch()

        card.setLayout(layout)

        return card
