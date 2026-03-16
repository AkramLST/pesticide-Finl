from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class ProductPage(QWidget):

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        title = QLabel("Products Page")
        title.setStyleSheet("font-size:24px;")

        layout.addWidget(title)

        self.setLayout(layout)