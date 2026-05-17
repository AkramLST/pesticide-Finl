from PySide6.QtWidgets import (
    QWidget, QLabel, QHBoxLayout, QPushButton,
    QFrame, QVBoxLayout, QScrollArea, QSizePolicy, QApplication
)
from PySide6.QtGui import QPixmap, QCursor
from PySide6.QtCore import Qt, QTimer, QPoint

from utils.session import session


class TopBar(QWidget):

    def __init__(self):
        super().__init__()
        self.setFixedHeight(60)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(
            "background-color:white; border-bottom:1.5px solid #e2e8f0;")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(10)

        # Logo
        logo = QLabel()
        px = QPixmap("images/logo_2.png")
        if not px.isNull():
            logo.setPixmap(px.scaled(38, 38, Qt.KeepAspectRatio,
                                     Qt.SmoothTransformation))

        # Title
        title = QLabel("Jadeed Zarai Markaz")
        title.setStyleSheet(
            "font-size:17px;font-weight:700;color:#0f172a;")

        layout.addWidget(logo)
        layout.addWidget(title)
        layout.addStretch()

        # Bell button
        self.bell_btn = QPushButton("🔔")
        self.bell_btn.setFixedSize(38, 38)
        self.bell_btn.setStyleSheet(
            "QPushButton{background:#f1f5f9;border:1.5px solid #e2e8f0;"
            "border-radius:8px;font-size:17px;color:#475569;}"
            "QPushButton:hover{background:#e2e8f0;}")
        self.bell_btn.clicked.connect(self._toggle_panel)

        # Badge label over bell
        self._badge = QLabel("0", self.bell_btn)
        self._badge.setFixedSize(18, 18)
        self._badge.move(20, 0)
        self._badge.setAlignment(Qt.AlignCenter)
        self._badge.setStyleSheet(
            "background:#ef4444;color:white;border-radius:9px;"
            "font-size:10px;font-weight:700;")
        self._badge.hide()

        # Username label
        self.user_lbl = QLabel("—")
        self.user_lbl.setStyleSheet(
            "font-size:13px;color:#475569;font-weight:600;"
            "padding:6px 12px;background:#f8fafc;"
            "border:1.5px solid #e2e8f0;border-radius:8px;")

        layout.addWidget(self.bell_btn)
        layout.addWidget(self.user_lbl)

        # Notification dropdown panel (popup, parented to desktop)
        self._panel = _NotifPanel()
        self._panel.hide()

        # Refresh every 60 s
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.refresh)
        self._timer.start(60_000)
        self.refresh()

    # ─────────────────────────────────────────────────────
    def refresh(self):
        u = session.user
        self.user_lbl.setText(
            f"👤  {u.get('name', u.get('username',''))} "
            f"({u.get('role','')})" if u else "—")

        try:
            from utils.notifier import get_notifications
            notes = get_notifications()
        except Exception:
            notes = []

        count = len(notes)
        if count:
            self._badge.setText(str(min(count, 99)))
            self._badge.show()
        else:
            self._badge.hide()

        self._panel.set_notifications(notes)

    def _toggle_panel(self):
        if self._panel.isVisible():
            self._panel.hide()
            return
        btn_pos  = self.bell_btn.mapToGlobal(QPoint(0, self.bell_btn.height() + 4))
        self._panel.move(btn_pos.x() - 260, btn_pos.y())
        self._panel.show()
        self._panel.raise_()


# ─── Notification Dropdown Panel ─────────────────────────────────────────────
class _NotifPanel(QFrame):

    def __init__(self):
        super().__init__(None, Qt.Popup | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setFixedWidth(320)
        self.setStyleSheet(
            "QFrame{background:white;border:1.5px solid #e2e8f0;"
            "border-radius:10px;}")
        self.setWindowFlag(Qt.NoDropShadowWindowHint, False)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        hdr = QLabel("🔔  Notifications")
        hdr.setStyleSheet(
            "font-size:13px;font-weight:700;color:#0f172a;"
            "padding:10px 14px;border-bottom:1px solid #f1f5f9;")
        root.addWidget(hdr)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setFixedHeight(300)
        self._body = QWidget()
        self._body.setStyleSheet("background:white;")
        self._body_layout = QVBoxLayout(self._body)
        self._body_layout.setContentsMargins(0, 0, 0, 0)
        self._body_layout.setSpacing(0)
        scroll.setWidget(self._body)
        root.addWidget(scroll)

        self._empty_lbl = QLabel("✅  All clear — no alerts")
        self._empty_lbl.setStyleSheet(
            "color:#94a3b8;font-size:12px;padding:20px;")
        self._empty_lbl.setAlignment(Qt.AlignCenter)

    def set_notifications(self, notes: list):
        while self._body_layout.count():
            item = self._body_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not notes:
            self._body_layout.addWidget(self._empty_lbl)
            self.adjustSize()
            return

        _sev_colors = {
            "critical": ("#fef2f2", "#dc2626"),
            "warning":  ("#fffbeb", "#d97706"),
            "info":     ("#eff6ff", "#2563eb"),
        }
        for n in notes:
            bg, fg = _sev_colors.get(n["severity"], ("#f8fafc", "#475569"))
            row = QLabel(n["message"])
            row.setWordWrap(True)
            row.setStyleSheet(
                f"background:{bg};color:{fg};font-size:12px;"
                f"padding:8px 14px;border-bottom:1px solid #f1f5f9;")
            self._body_layout.addWidget(row)

        self._body_layout.addStretch()
        self.adjustSize()