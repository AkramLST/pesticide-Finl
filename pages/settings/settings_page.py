from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class SettingsPage(QWidget):

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        title = QLabel("Settings")
        title.setStyleSheet("font-size:24px; font-weight:bold;")
        layout.addWidget(title)
        layout.addStretch()
        self.setLayout(layout)
