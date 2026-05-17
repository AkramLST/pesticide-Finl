"""
Global theme manager.
Call apply_theme('light' | 'dark') to switch QSS on the running QApplication.
Persists the choice to the settings DB.
"""
import os
from PySide6.QtWidgets import QApplication

BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_QSS_DIR   = os.path.join(BASE_DIR, "assets", "styles")
_LIGHT_QSS = os.path.join(_QSS_DIR, "light.qss")
_DARK_QSS  = os.path.join(_QSS_DIR, "dark.qss")

_current_theme = "light"


def current_theme() -> str:
    return _current_theme


def apply_theme(theme: str, save: bool = True):
    """Apply 'light' or 'dark' QSS globally and optionally persist."""
    global _current_theme
    theme = theme if theme in ("light", "dark") else "light"
    _current_theme = theme

    qss_path = _DARK_QSS if theme == "dark" else _LIGHT_QSS
    try:
        with open(qss_path, "r", encoding="utf-8") as f:
            qss = f.read()
        app = QApplication.instance()
        if app:
            app.setStyleSheet(qss)
    except FileNotFoundError:
        pass

    if save:
        try:
            from models.settings_model import set_setting
            set_setting("theme", theme)
        except Exception:
            pass


def load_saved_theme():
    """Read saved theme from DB and apply it (called at startup)."""
    try:
        from models.settings_model import get_setting
        theme = get_setting("theme") or "light"
    except Exception:
        theme = "light"
    apply_theme(theme, save=False)
