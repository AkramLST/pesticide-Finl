from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class SuppliersPage(QWidget):

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        title = QLabel("Suppliers")
        title.setStyleSheet("font-size:24px; font-weight:bold;")
        layout.addWidget(title)
        layout.addStretch()
        self.setLayout(layout)
