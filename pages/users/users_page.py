from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QLineEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QMessageBox, QDialog,
    QFormLayout, QComboBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from models.user_model import (
    get_all_users, insert_user, update_user,
    update_password, toggle_user_status
)
from utils.config import USER_ROLES
from utils.helpers import format_datetime
from utils.session import session

_TABLE_STYLE = """
    QTableWidget { border:none; font-size:13px; background:white;
                   alternate-background-color:#f8fafc; }
    QHeaderView::section { background:#f1f5f9; color:#475569; font-weight:700;
        font-size:12px; padding:10px 8px; border:none;
        border-right:1px solid #e2e8f0; }
    QTableWidget::item { padding:9px 8px; color:#1e293b;
        border-bottom:1px solid #f1f5f9; }
    QTableWidget::item:selected { background:#dbeafe; color:#1e40af; }
"""
_FS = ("QLineEdit,QComboBox{border:1.5px solid #e2e8f0;border-radius:7px;"
       "padding:8px;font-size:13px;background:white;}"
       "QLineEdit:focus,QComboBox:focus{border-color:#2e7d32;}")
_GREEN = ("QPushButton{background:#2e7d32;color:white;border-radius:8px;"
          "padding:8px 16px;font-size:13px;font-weight:700;border:none;}"
          "QPushButton:hover{background:#1b5e20;}")
_GRAY  = ("QPushButton{background:#f1f5f9;color:#475569;border-radius:8px;"
          "padding:8px 14px;font-size:13px;border:1.5px solid #e2e8f0;}"
          "QPushButton:hover{background:#e2e8f0;}")
_RED   = ("QPushButton{background:#fef2f2;color:#dc2626;border:1px solid #fecaca;"
          "border-radius:8px;font-size:13px;font-weight:600;padding:8px 14px;}"
          "QPushButton:hover{background:#fee2e2;}")
_AMBER = ("QPushButton{background:#fffbeb;color:#92400e;border:1px solid #fde68a;"
          "border-radius:8px;font-size:13px;font-weight:600;padding:8px 14px;}"
          "QPushButton:hover{background:#fef3c7;}")

COL_ID     = 0
COL_NAME   = 1
COL_USER   = 2
COL_ROLE   = 3
COL_PHONE  = 4
COL_EMAIL  = 5
COL_STATUS = 6
COL_LAST   = 7


class UsersPage(QWidget):

    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("background:#f1f5f9;")
        self._all = []
        self._build_ui()
        self.load_data()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Header
        header = QFrame()
        header.setFixedHeight(64)
        header.setAttribute(Qt.WA_StyledBackground, True)
        header.setStyleSheet("QFrame{background:white;border-bottom:1.5px solid #e2e8f0;}")
        hl = QHBoxLayout(header)
        hl.setContentsMargins(24, 0, 24, 0)
        hl.setSpacing(12)

        title = QLabel("👤  Users")
        title.setStyleSheet("font-size:20px;font-weight:700;color:#0f172a;")

        self.search = QLineEdit()
        self.search.setPlaceholderText("🔍  Search name or username…")
        self.search.setFixedWidth(240)
        self.search.setStyleSheet(
            "QLineEdit{border:1.5px solid #e2e8f0;border-radius:8px;"
            "padding:8px 14px;font-size:13px;background:white;}"
            "QLineEdit:focus{border-color:#2e7d32;}")
        self.search.textChanged.connect(self._filter)

        add_btn = QPushButton("➕  Add User")
        add_btn.setFixedHeight(38)
        add_btn.setStyleSheet(_GREEN)
        add_btn.clicked.connect(self._add)

        refresh_btn = QPushButton("↻")
        refresh_btn.setFixedSize(38, 38)
        refresh_btn.setStyleSheet(
            "QPushButton{background:#f1f5f9;border:1.5px solid #e2e8f0;"
            "border-radius:8px;font-size:16px;color:#475569;}"
            "QPushButton:hover{background:#e2e8f0;}")
        refresh_btn.clicked.connect(self.load_data)

        hl.addWidget(title)
        hl.addStretch()
        hl.addWidget(self.search)
        hl.addWidget(add_btn)
        hl.addWidget(refresh_btn)
        root.addWidget(header)

        # Stats strip
        self.stats_bar = QFrame()
        self.stats_bar.setFixedHeight(44)
        self.stats_bar.setAttribute(Qt.WA_StyledBackground, True)
        self.stats_bar.setStyleSheet("background:#f8fafc;border-bottom:1px solid #e2e8f0;")
        self._sbar = QHBoxLayout(self.stats_bar)
        self._sbar.setContentsMargins(24, 0, 24, 0)
        self._sbar.setSpacing(30)
        root.addWidget(self.stats_bar)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ID", "Full Name", "Username", "Role",
            "Phone", "Email", "Status", "Last Login"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setColumnWidth(COL_ID,     45)
        self.table.setColumnWidth(COL_NAME,   160)
        self.table.setColumnWidth(COL_USER,   120)
        self.table.setColumnWidth(COL_ROLE,   90)
        self.table.setColumnWidth(COL_PHONE,  120)
        self.table.setColumnWidth(COL_EMAIL,  180)
        self.table.setColumnWidth(COL_STATUS, 80)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.setSortingEnabled(True)
        self.table.setStyleSheet(_TABLE_STYLE)

        wrap = QFrame()
        wrap.setAttribute(Qt.WA_StyledBackground, True)
        wrap.setStyleSheet("background:white;border:none;")
        wl = QVBoxLayout(wrap)
        wl.setContentsMargins(16, 12, 16, 10)
        wl.setSpacing(8)

        act_row = QHBoxLayout()
        for label, style, slot in [
            ("✏  Edit",           _GRAY,  self._edit),
            ("🔑  Reset Password", _AMBER, self._reset_password),
            ("⏸  Toggle Active",  _RED,   self._toggle_status),
        ]:
            b = QPushButton(label)
            b.setFixedHeight(36)
            b.setStyleSheet(style)
            b.clicked.connect(slot)
            act_row.addWidget(b)
        act_row.addStretch()

        wl.addWidget(self.table)
        wl.addLayout(act_row)
        root.addWidget(wrap)

    # ─────────────────────────────────────────────────────
    def _update_stats(self, users):
        while self._sbar.count():
            item = self._sbar.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        active   = sum(1 for u in users if u.get("is_active", 1))
        inactive = len(users) - active
        for text, color in [
            (f"Total: <b>{len(users)}</b>", "#475569"),
            (f"✅ Active: <b>{active}</b>",   "#10b981"),
            (f"🚫 Inactive: <b>{inactive}</b>", "#ef4444"),
        ]:
            lbl = QLabel(text)
            lbl.setStyleSheet(f"font-size:13px;color:{color};")
            self._sbar.addWidget(lbl)
        self._sbar.addStretch()

    def load_data(self):
        self._all = get_all_users()
        self._filter()

    def _filter(self):
        q = self.search.text().lower().strip()
        result = [u for u in self._all
                  if not q
                  or q in (u.get("name","") or "").lower()
                  or q in (u.get("username","") or "").lower()]
        self._populate(result)
        self._update_stats(result)

    def _populate(self, users):
        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(users))
        for row, u in enumerate(users):
            active = u.get("is_active", 1)
            status_text  = "Active" if active else "Inactive"
            status_color = QColor("#16a34a") if active else QColor("#dc2626")

            cells = [
                str(u.get("id","")),
                u.get("name",""),
                u.get("username",""),
                u.get("role",""),
                u.get("phone","") or "—",
                u.get("email","") or "—",
                status_text,
                format_datetime(u.get("last_login","") or ""),
            ]
            for col, text in enumerate(cells):
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
                if col == COL_STATUS:
                    item.setForeground(status_color)
                    item.setTextAlignment(Qt.AlignCenter)
                if not active:
                    item.setForeground(QColor("#94a3b8"))
                    if col == COL_STATUS:
                        item.setForeground(status_color)
                self.table.setItem(row, col, item)
            self.table.setRowHeight(row, 42)
        self.table.setSortingEnabled(True)

    def _selected(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(self, "Select Row", "Please select a user first.")
            return None
        uid = int(self.table.item(row, COL_ID).text())
        return next((u for u in self._all if u["id"] == uid), None)

    def _add(self):
        if UserDialog().exec():
            self.load_data()

    def _edit(self):
        u = self._selected()
        if u and UserDialog(u).exec():
            self.load_data()

    def _reset_password(self):
        u = self._selected()
        if not u:
            return
        dlg = ResetPasswordDialog(u)
        if dlg.exec():
            self.load_data()

    def _toggle_status(self):
        u = self._selected()
        if not u:
            return
        current_user = session.user
        if current_user and current_user.get("id") == u["id"]:
            QMessageBox.warning(self, "Not Allowed", "You cannot deactivate your own account.")
            return
        new_status = 0 if u.get("is_active", 1) else 1
        action = "deactivate" if new_status == 0 else "activate"
        if QMessageBox.question(self, "Confirm",
                                f"{action.capitalize()} user '{u['username']}'?",
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            toggle_user_status(u["id"], new_status)
            self.load_data()


# ─── User Add/Edit Dialog ────────────────────────────────────────────────────
class UserDialog(QDialog):

    def __init__(self, user: dict = None):
        super().__init__()
        self.user = user
        self.setWindowTitle("Edit User" if user else "Add User")
        self.resize(440, 380)
        self._build()
        if user:
            self._prefill()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 18, 20, 18)
        root.setSpacing(12)

        heading = QLabel("✏  Edit User" if self.user else "➕  Add New User")
        heading.setStyleSheet("font-size:18px;font-weight:700;color:#0f172a;")
        root.addWidget(heading)

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignRight)

        self.name_i     = QLineEdit(); self.name_i.setStyleSheet(_FS)
        self.username_i = QLineEdit(); self.username_i.setStyleSheet(_FS)
        self.phone_i    = QLineEdit(); self.phone_i.setStyleSheet(_FS)
        self.email_i    = QLineEdit(); self.email_i.setStyleSheet(_FS)

        self.role_cb = QComboBox()
        self.role_cb.addItems(USER_ROLES)
        self.role_cb.setStyleSheet(_FS)

        form.addRow("Full Name *:", self.name_i)
        form.addRow("Username *:",  self.username_i)
        form.addRow("Role:",        self.role_cb)
        form.addRow("Phone:",       self.phone_i)
        form.addRow("Email:",       self.email_i)

        if not self.user:
            self.pass_i    = QLineEdit(); self.pass_i.setEchoMode(QLineEdit.Password)
            self.pass_i.setStyleSheet(_FS)
            self.confirm_i = QLineEdit(); self.confirm_i.setEchoMode(QLineEdit.Password)
            self.confirm_i.setStyleSheet(_FS)
            form.addRow("Password *:",        self.pass_i)
            form.addRow("Confirm Password *:", self.confirm_i)

        root.addLayout(form)

        btn_row = QHBoxLayout()
        cancel = QPushButton("Cancel"); cancel.setStyleSheet(_GRAY)
        cancel.clicked.connect(self.reject)
        save = QPushButton("Save"); save.setStyleSheet(_GREEN)
        save.clicked.connect(self._save)
        btn_row.addWidget(cancel); btn_row.addStretch(); btn_row.addWidget(save)
        root.addLayout(btn_row)

    def _prefill(self):
        u = self.user
        self.name_i.setText(u.get("name",""))
        self.username_i.setText(u.get("username",""))
        self.phone_i.setText(u.get("phone","") or "")
        self.email_i.setText(u.get("email","") or "")
        idx = self.role_cb.findText(u.get("role",""))
        if idx >= 0:
            self.role_cb.setCurrentIndex(idx)

    def _save(self):
        name     = self.name_i.text().strip()
        username = self.username_i.text().strip()
        if not name or not username:
            QMessageBox.warning(self, "Validation", "Name and username are required.")
            return

        data = {
            "name":          name,
            "username":      username,
            "role":          self.role_cb.currentText(),
            "phone":         self.phone_i.text().strip(),
            "email":         self.email_i.text().strip(),
            "profile_image": self.user.get("profile_image","") if self.user else "",
        }

        try:
            if self.user:
                update_user(self.user["id"], data)
            else:
                pwd  = self.pass_i.text()
                cpwd = self.confirm_i.text()
                if not pwd:
                    QMessageBox.warning(self, "Validation", "Password is required.")
                    return
                if pwd != cpwd:
                    QMessageBox.warning(self, "Validation", "Passwords do not match.")
                    return
                insert_user({**data, "password": pwd})
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


# ─── Reset Password Dialog ────────────────────────────────────────────────────
class ResetPasswordDialog(QDialog):

    def __init__(self, user: dict):
        super().__init__()
        self.user = user
        self.setWindowTitle(f"Reset Password — {user['username']}")
        self.resize(380, 220)
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 18, 20, 18)
        root.setSpacing(12)

        root.addWidget(QLabel(
            f"<b>Reset password for:</b>  {self.user.get('name','')}  "
            f"<span style='color:#64748b'>(@{self.user.get('username','')})</span>"
        ))

        form = QFormLayout()
        self.new_pass    = QLineEdit(); self.new_pass.setEchoMode(QLineEdit.Password)
        self.confirm_pass = QLineEdit(); self.confirm_pass.setEchoMode(QLineEdit.Password)
        for w in (self.new_pass, self.confirm_pass):
            w.setStyleSheet(_FS)
        form.addRow("New Password:",     self.new_pass)
        form.addRow("Confirm Password:", self.confirm_pass)
        root.addLayout(form)

        btn_row = QHBoxLayout()
        cancel = QPushButton("Cancel"); cancel.setStyleSheet(_GRAY)
        cancel.clicked.connect(self.reject)
        ok = QPushButton("🔑  Reset"); ok.setStyleSheet(_AMBER)
        ok.clicked.connect(self._reset)
        btn_row.addWidget(cancel); btn_row.addStretch(); btn_row.addWidget(ok)
        root.addLayout(btn_row)

    def _reset(self):
        pwd  = self.new_pass.text()
        cpwd = self.confirm_pass.text()
        if not pwd:
            QMessageBox.warning(self, "Validation", "Password cannot be empty.")
            return
        if pwd != cpwd:
            QMessageBox.warning(self, "Validation", "Passwords do not match.")
            return
        update_password(self.user["id"], pwd)
        QMessageBox.information(self, "Success",
            f"Password for '{self.user['username']}' has been reset.")
        self.accept()
