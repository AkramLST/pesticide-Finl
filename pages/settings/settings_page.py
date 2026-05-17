from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QLineEdit, QTextEdit, QFormLayout,
    QScrollArea, QMessageBox, QSizePolicy
)
from PySide6.QtCore import Qt

from models.settings_model import get_all_settings, set_setting
from models.user_model import update_password
from utils.session import session

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

    def _change_password(self):
        from models.user_model import get_user_by_credentials
        user = session.get_user()
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
