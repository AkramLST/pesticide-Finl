from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class SupplierPage(QWidget):

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        title = QLabel("Suppliers Page")
        title.setStyleSheet("font-size:24px;")

        layout.addWidget(title)

        self.setLayout(layout)