import sys
from PySide6.QtWidgets import QApplication
from database.migrations import run_migrations
from pages.login_page import LoginWindow

run_migrations()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = LoginWindow()
    window.show()

    sys.exit(app.exec())

