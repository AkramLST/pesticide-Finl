import sys
from PySide6.QtWidgets import QApplication
from database.migrations import run_migrations
from pages.login_page import LoginWindow
from utils.theme import load_saved_theme

run_migrations()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    load_saved_theme()

    window = LoginWindow()
    window.show()

    sys.exit(app.exec())

