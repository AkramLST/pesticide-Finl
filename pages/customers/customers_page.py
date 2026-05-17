from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class CustomersPage(QWidget):

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        title = QLabel("Customers")
        title.setStyleSheet("font-size:24px; font-weight:bold;")
        layout.addWidget(title)
        layout.addStretch()
        self.setLayout(layout)
