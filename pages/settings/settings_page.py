import os, shutil
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QLineEdit, QTextEdit, QFormLayout,
    QScrollArea, QMessageBox, QSizePolicy, QCheckBox, QFileDialog
)
from PySide6.QtCore import Qt

from models.settings_model import get_all_settings, set_setting
from models.user_model import update_password, update_user
from utils.session import session
from utils.config import DB_PATH, BACKUPS_DIR
from utils.theme import apply_theme, current_theme

_FS = ("QLineEdit,QTextEdit{border:1.5px solid #e2e8f0;border-radius:7px;"
       "padding:8px 10px;font-size:13px;background:white;min-height:34px;}"
       "QLineEdit:focus,QTextEdit:focus{border-color:#2e7d32;}")
_GREEN = ("QPushButton{background:#2e7d32;color:white;border-radius:8px;"
          "padding:9px 22px;font-size:13px;font-weight:700;border:none;}"
          "QPushButton:hover{background:#1b5e20;}")
_GRAY  = ("QPushButton{background:#f1f5f9;color:#475569;border-radius:8px;"
          "padding:9px 18px;font-size:13px;border:1.5px solid #e2e8f0;}"
          "QPushButton:hover{background:#e2e8f0;}")


def _section_header(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setStyleSheet(
        "font-size:15px;font-weight:700;color:#0f172a;"
        "padding-bottom:4px;border-bottom:2px solid #2e7d32;")
    return lbl


def _divider() -> QFrame:
    line = QFrame()
    line.setFrameShape(QFrame.HLine)
    line.setStyleSheet("color:#e2e8f0;")
    return line


class SettingsPage(QWidget):

    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("background:#f1f5f9;")
        self._build_ui()
        self._load()

    # ─────────────────────────────────────────────────────
    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # Page header bar
        header = QFrame()
        header.setFixedHeight(64)
        header.setAttribute(Qt.WA_StyledBackground, True)
        header.setStyleSheet("QFrame{background:white;border-bottom:1.5px solid #e2e8f0;}")
        hl = QHBoxLayout(header)
        hl.setContentsMargins(24, 0, 24, 0)
        title = QLabel("⚙️  Settings")
        title.setStyleSheet("font-size:20px;font-weight:700;color:#0f172a;")
        hl.addWidget(title)
        hl.addStretch()
        outer.addWidget(header)

        # Scrollable body
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea{background:#f1f5f9;}")
        body = QWidget()
        body.setStyleSheet("background:#f1f5f9;")
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(32, 24, 32, 32)
        body_layout.setSpacing(24)
        scroll.setWidget(body)
        outer.addWidget(scroll)

        # ── Shop Information card
        shop_card = self._card()
        sc_layout = QVBoxLayout(shop_card)
        sc_layout.setSpacing(14)
        sc_layout.addWidget(_section_header("🏪  Shop Information"))

        shop_form = QFormLayout()
        shop_form.setSpacing(10)
        shop_form.setLabelAlignment(Qt.AlignRight)

        self.shop_name_i    = QLineEdit()
        self.shop_address_i = QLineEdit()
        self.shop_phone_i   = QLineEdit()
        self.shop_email_i   = QLineEdit()
        for w in (self.shop_name_i, self.shop_address_i,
                  self.shop_phone_i, self.shop_email_i):
            w.setStyleSheet(_FS)

        shop_form.addRow("Shop Name:",    self.shop_name_i)
        shop_form.addRow("Address:",      self.shop_address_i)
        shop_form.addRow("Phone:",        self.shop_phone_i)
        shop_form.addRow("Email:",        self.shop_email_i)
        sc_layout.addLayout(shop_form)

        shop_save = QPushButton("💾  Save Shop Info")
        shop_save.setFixedWidth(200)
        shop_save.setStyleSheet(_GREEN)
        shop_save.clicked.connect(self._save_shop)
        sc_layout.addWidget(shop_save, alignment=Qt.AlignLeft)
        body_layout.addWidget(shop_card)

        # ── Invoice Settings card
        inv_card = self._card()
        iv_layout = QVBoxLayout(inv_card)
        iv_layout.setSpacing(14)
        iv_layout.addWidget(_section_header("🧾  Invoice Settings"))

        inv_form = QFormLayout()
        inv_form.setSpacing(10)
        inv_form.setLabelAlignment(Qt.AlignRight)

        self.inv_footer_i = QTextEdit()
        self.inv_footer_i.setFixedHeight(70)
        self.inv_footer_i.setStyleSheet(_FS)
        self.inv_prefix_i = QLineEdit()
        self.inv_prefix_i.setPlaceholderText("e.g. INV")
        self.inv_prefix_i.setStyleSheet(_FS)

        inv_form.addRow("Invoice Prefix:", self.inv_prefix_i)
        inv_form.addRow("Footer Text:",    self.inv_footer_i)
        iv_layout.addLayout(inv_form)

        inv_save = QPushButton("💾  Save Invoice Settings")
        inv_save.setFixedWidth(230)
        inv_save.setStyleSheet(_GREEN)
        inv_save.clicked.connect(self._save_invoice)
        iv_layout.addWidget(inv_save, alignment=Qt.AlignLeft)
        body_layout.addWidget(inv_card)

        # ── Change Password card
        pw_card = self._card()
        pw_layout = QVBoxLayout(pw_card)
        pw_layout.setSpacing(14)
        pw_layout.addWidget(_section_header("🔑  Change My Password"))

        pw_form = QFormLayout()
        pw_form.setSpacing(10)
        pw_form.setLabelAlignment(Qt.AlignRight)

        self.cur_pass_i  = QLineEdit(); self.cur_pass_i.setEchoMode(QLineEdit.Password)
        self.new_pass_i  = QLineEdit(); self.new_pass_i.setEchoMode(QLineEdit.Password)
        self.conf_pass_i = QLineEdit(); self.conf_pass_i.setEchoMode(QLineEdit.Password)
        for w in (self.cur_pass_i, self.new_pass_i, self.conf_pass_i):
            w.setStyleSheet(_FS)

        pw_form.addRow("Current Password:", self.cur_pass_i)
        pw_form.addRow("New Password:",      self.new_pass_i)
        pw_form.addRow("Confirm Password:",  self.conf_pass_i)
        pw_layout.addLayout(pw_form)

        pw_save = QPushButton("🔒  Update Password")
        pw_save.setFixedWidth(200)
        pw_save.setStyleSheet(_GREEN)
        pw_save.clicked.connect(self._change_password)
        pw_layout.addWidget(pw_save, alignment=Qt.AlignLeft)
        body_layout.addWidget(pw_card)

        # ── Profile card
        prof_card = self._card()
        pf_layout = QVBoxLayout(prof_card)
        pf_layout.setSpacing(14)
        pf_layout.addWidget(_section_header("👤  My Profile"))

        prof_form = QFormLayout()
        prof_form.setSpacing(10)
        prof_form.setLabelAlignment(Qt.AlignRight)
        self.prof_name_i     = QLineEdit(); self.prof_name_i.setStyleSheet(_FS)
        self.prof_username_i = QLineEdit(); self.prof_username_i.setStyleSheet(_FS)
        self.prof_phone_i    = QLineEdit(); self.prof_phone_i.setStyleSheet(_FS)
        self.prof_email_i    = QLineEdit(); self.prof_email_i.setStyleSheet(_FS)
        prof_form.addRow("Full Name:",  self.prof_name_i)
        prof_form.addRow("Username:",   self.prof_username_i)
        prof_form.addRow("Phone:",       self.prof_phone_i)
        prof_form.addRow("Email:",       self.prof_email_i)
        pf_layout.addLayout(prof_form)
        prof_save = QPushButton("💾  Save Profile")
        prof_save.setFixedWidth(180)
        prof_save.setStyleSheet(_GREEN)
        prof_save.clicked.connect(self._save_profile)
        pf_layout.addWidget(prof_save, alignment=Qt.AlignLeft)
        body_layout.addWidget(prof_card)

        # ── Database Backup card
        bk_card = self._card()
        bk_layout = QVBoxLayout(bk_card)
        bk_layout.setSpacing(14)
        bk_layout.addWidget(_section_header("🗄️  Database Backup & Restore"))
        bk_row = QHBoxLayout()
        bk_btn = QPushButton("💾  Backup Now")
        bk_btn.setFixedHeight(36)
        bk_btn.setStyleSheet(_GREEN)
        bk_btn.clicked.connect(self._backup_db)
        restore_btn = QPushButton("📂  Restore from Backup")
        restore_btn.setFixedHeight(36)
        restore_btn.setStyleSheet(_GRAY)
        restore_btn.clicked.connect(self._restore_db)
        bk_row.addWidget(bk_btn)
        bk_row.addWidget(restore_btn)
        bk_row.addStretch()
        bk_layout.addLayout(bk_row)
        body_layout.addWidget(bk_card)

        # ── Theme toggle card
        th_card = self._card()
        th_layout = QVBoxLayout(th_card)
        th_layout.setSpacing(14)
        th_layout.addWidget(_section_header("🎨  Appearance"))
        th_row = QHBoxLayout()
        self.light_btn = QPushButton("☀️  Light Mode")
        self.dark_btn  = QPushButton("🌙  Dark Mode")
        for btn in (self.light_btn, self.dark_btn):
            btn.setFixedHeight(38)
            btn.setFixedWidth(160)
        self.light_btn.clicked.connect(lambda: self._set_theme("light"))
        self.dark_btn.clicked.connect(lambda: self._set_theme("dark"))
        th_row.addWidget(self.light_btn)
        th_row.addWidget(self.dark_btn)
        th_row.addStretch()
        th_layout.addLayout(th_row)
        body_layout.addWidget(th_card)

        # ── Notification preferences card
        np_card = self._card()
        np_layout = QVBoxLayout(np_card)
        np_layout.setSpacing(10)
        np_layout.addWidget(_section_header("🔔  Notification Preferences"))
        _cb_style = "QCheckBox{font-size:13px;color:#1e293b;}"
        self.notif_stock_cb   = QCheckBox("Low stock alerts")
        self.notif_expiry_cb  = QCheckBox("Expired / expiring soon alerts")
        self.notif_payment_cb = QCheckBox("Pending customer payment alerts")
        for cb in (self.notif_stock_cb, self.notif_expiry_cb, self.notif_payment_cb):
            cb.setStyleSheet(_cb_style)
            np_layout.addWidget(cb)
        np_save = QPushButton("💾  Save Preferences")
        np_save.setFixedWidth(200)
        np_save.setStyleSheet(_GREEN)
        np_save.clicked.connect(self._save_notif_prefs)
        np_layout.addWidget(np_save, alignment=Qt.AlignLeft)
        body_layout.addWidget(np_card)

        # ── Activity Log card
        log_card = self._card()
        log_layout = QVBoxLayout(log_card)
        log_layout.setSpacing(10)
        log_layout.addWidget(_section_header("📋  Activity Log"))

        log_filter_row = QHBoxLayout()
        self.log_search = QLineEdit()
        self.log_search.setPlaceholderText("🔍  Filter by action or user…")
        self.log_search.setFixedWidth(260)
        self.log_search.setStyleSheet(_FS)
        self.log_search.textChanged.connect(self._load_log)
        log_refresh = QPushButton("↻  Refresh")
        log_refresh.setStyleSheet(_GRAY)
        log_refresh.setFixedHeight(34)
        log_refresh.clicked.connect(self._load_log)
        log_filter_row.addWidget(self.log_search)
        log_filter_row.addWidget(log_refresh)
        log_filter_row.addStretch()
        log_layout.addLayout(log_filter_row)

        from PySide6.QtWidgets import QTableWidget, QHeaderView, QAbstractItemView
        self.log_table = QTableWidget()
        self.log_table.setColumnCount(4)
        self.log_table.setHorizontalHeaderLabels(["Time", "User", "Action", "Details"])
        self.log_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.log_table.verticalHeader().setVisible(False)
        self.log_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.log_table.setAlternatingRowColors(True)
        self.log_table.setShowGrid(False)
        self.log_table.setFixedHeight(260)
        self.log_table.setStyleSheet(
            "QTableWidget{border:none;font-size:12px;background:white;"
            "alternate-background-color:#f8fafc;}"
            "QHeaderView::section{background:#f1f5f9;color:#475569;"
            "font-weight:700;font-size:11px;padding:6px;border:none;}"
            "QTableWidget::item{padding:6px;color:#1e293b;"
            "border-bottom:1px solid #f1f5f9;}")
        log_layout.addWidget(self.log_table)
        body_layout.addWidget(log_card)

        body_layout.addStretch()

    # ─────────────────────────────────────────────────────
    @staticmethod
    def _card() -> QFrame:
        card = QFrame()
        card.setAttribute(Qt.WA_StyledBackground, True)
        card.setStyleSheet(
            "QFrame{background:white;border-radius:12px;"
            "border:1px solid #e2e8f0;}")
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        card.setContentsMargins(20, 18, 20, 18)
        return card

    def _load(self):
        s = get_all_settings()
        self.shop_name_i.setText(s.get("shop_name", ""))
        self.shop_address_i.setText(s.get("shop_address", ""))
        self.shop_phone_i.setText(s.get("shop_phone", ""))
        self.shop_email_i.setText(s.get("shop_email", ""))
        self.inv_prefix_i.setText(s.get("invoice_prefix", "INV"))
        self.inv_footer_i.setPlainText(s.get("invoice_footer",
            "Thank you for your business!"))
        u = session.user
        if u:
            self.prof_name_i.setText(u.get("name", ""))
            self.prof_username_i.setText(u.get("username", ""))
            self.prof_phone_i.setText(u.get("phone", "") or "")
            self.prof_email_i.setText(u.get("email", "") or "")
        self.notif_stock_cb.setChecked(s.get("notif_stock", "1") == "1")
        self.notif_expiry_cb.setChecked(s.get("notif_expiry", "1") == "1")
        self.notif_payment_cb.setChecked(s.get("notif_payment", "1") == "1")
        self._refresh_theme_btns()
        self._load_log()

    def _set_theme(self, theme: str):
        apply_theme(theme)
        self._refresh_theme_btns()

    def _refresh_theme_btns(self):
        t = current_theme()
        active  = ("QPushButton{background:#2e7d32;color:white;border-radius:8px;"
                   "padding:9px 22px;font-size:13px;font-weight:700;border:none;}"
                   "QPushButton:hover{background:#1b5e20;}")
        inactive = _GRAY
        self.light_btn.setStyleSheet(active  if t == "light" else inactive)
        self.dark_btn.setStyleSheet( active  if t == "dark"  else inactive)

    def _load_log(self):
        from database.connection import get_connection
        from PySide6.QtWidgets import QTableWidgetItem
        query = self.log_search.text().lower().strip()
        conn = get_connection()
        rows = conn.execute("""
            SELECT al.timestamp, COALESCE(u.name, u.username, 'System') AS user_name,
                   al.action, al.details
            FROM activity_logs al
            LEFT JOIN users u ON al.user_id = u.id
            ORDER BY al.id DESC LIMIT 200
        """).fetchall()
        conn.close()
        filtered = [r for r in rows if not query or
                    query in (r["action"] or "").lower() or
                    query in (r["user_name"] or "").lower() or
                    query in (r["details"] or "").lower()]
        self.log_table.setRowCount(len(filtered))
        for row_idx, r in enumerate(filtered):
            for col, val in enumerate([
                r["timestamp"] or "", r["user_name"] or "—",
                r["action"] or "", r["details"] or ""
            ]):
                item = QTableWidgetItem(str(val))
                item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
                self.log_table.setItem(row_idx, col, item)
            self.log_table.setRowHeight(row_idx, 36)

    def _save_shop(self):
        set_setting("shop_name",    self.shop_name_i.text().strip())
        set_setting("shop_address", self.shop_address_i.text().strip())
        set_setting("shop_phone",   self.shop_phone_i.text().strip())
        set_setting("shop_email",   self.shop_email_i.text().strip())
        QMessageBox.information(self, "Saved", "Shop information saved.")

    def _save_invoice(self):
        set_setting("invoice_prefix", self.inv_prefix_i.text().strip() or "INV")
        set_setting("invoice_footer", self.inv_footer_i.toPlainText().strip())
        QMessageBox.information(self, "Saved", "Invoice settings saved.")

    def _save_profile(self):
        user = session.user
        if not user:
            return
        name     = self.prof_name_i.text().strip()
        username = self.prof_username_i.text().strip()
        if not name or not username:
            QMessageBox.warning(self, "Validation", "Name and username are required.")
            return
        update_user(user["id"], {
            "name":          name,
            "username":      username,
            "role":          user.get("role", "Staff"),
            "phone":         self.prof_phone_i.text().strip(),
            "email":         self.prof_email_i.text().strip(),
            "profile_image": user.get("profile_image", ""),
        })
        session.user["name"]     = name
        session.user["username"] = username
        QMessageBox.information(self, "Saved", "Profile updated successfully.")

    def _backup_db(self):
        os.makedirs(BACKUPS_DIR, exist_ok=True)
        ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
        dest = os.path.join(BACKUPS_DIR, f"backup_{ts}.db")
        shutil.copy2(DB_PATH, dest)
        QMessageBox.information(self, "Backup Complete",
            f"Database backed up to:\n{dest}")

    def _restore_db(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Backup File", BACKUPS_DIR, "DB Files (*.db)")
        if not path:
            return
        if QMessageBox.question(self, "Confirm Restore",
                "This will REPLACE the current database and restart the app.\n"
                "Are you sure?",
                QMessageBox.Yes | QMessageBox.No) != QMessageBox.Yes:
            return
        shutil.copy2(path, DB_PATH)
        QMessageBox.information(self, "Restored",
            "Database restored. Please restart the application.")

    def _save_notif_prefs(self):
        set_setting("notif_stock",   "1" if self.notif_stock_cb.isChecked() else "0")
        set_setting("notif_expiry",  "1" if self.notif_expiry_cb.isChecked() else "0")
        set_setting("notif_payment", "1" if self.notif_payment_cb.isChecked() else "0")
        QMessageBox.information(self, "Saved", "Notification preferences saved.")

    def _change_password(self):
        from models.user_model import get_user_by_credentials
        user = session.user
        if not user:
            QMessageBox.warning(self, "Error", "Not logged in.")
            return

        cur  = self.cur_pass_i.text()
        new  = self.new_pass_i.text()
        conf = self.conf_pass_i.text()

        if not cur or not new:
            QMessageBox.warning(self, "Validation", "All password fields are required.")
            return
        if new != conf:
            QMessageBox.warning(self, "Validation", "New passwords do not match.")
            return
        if len(new) < 4:
            QMessageBox.warning(self, "Validation", "Password must be at least 4 characters.")
            return

        valid = get_user_by_credentials(user["username"], cur)
        if not valid:
            QMessageBox.warning(self, "Wrong Password", "Current password is incorrect.")
            return

        update_password(user["id"], new)
        self.cur_pass_i.clear()
        self.new_pass_i.clear()
        self.conf_pass_i.clear()
        QMessageBox.information(self, "Success", "Password changed successfully.")
