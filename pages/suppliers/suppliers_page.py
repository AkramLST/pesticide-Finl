from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QLineEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QMessageBox, QDialog,
    QFormLayout, QTextEdit, QDoubleSpinBox, QComboBox
)
from PySide6.QtCore import Qt
from database.connection import get_connection
from models.supplier_model import (
    get_all_suppliers, get_supplier_balance, insert_supplier, update_supplier, delete_supplier
)
from models.payment_model import record_supplier_payment
from utils.config import PAYMENT_METHODS
from utils.session import session
from utils.helpers import format_datetime, format_currency

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
_GREEN = ("QPushButton{background:#2e7d32;color:white;border-radius:8px;"
          "padding:8px 16px;font-size:13px;font-weight:700;border:none;}"
          "QPushButton:hover{background:#1b5e20;}")
_GRAY  = ("QPushButton{background:#f1f5f9;color:#475569;border-radius:8px;"
          "padding:8px 14px;font-size:13px;border:1.5px solid #e2e8f0;}"
          "QPushButton:hover{background:#e2e8f0;}")
_RED   = ("QPushButton{background:#fef2f2;color:#dc2626;border:1px solid #fecaca;"
          "border-radius:8px;font-size:13px;font-weight:600;padding:8px 14px;}"
          "QPushButton:hover{background:#fee2e2;}")

COL_ID    = 0
COL_NAME  = 1
COL_PHONE = 2
COL_EMAIL = 3
COL_ADDR  = 4
COL_PRODS = 5
COL_PURCHASED = 6
COL_PAID = 7
COL_PENDING = 8
COL_UPD   = 9


def _product_count(supplier_id: int) -> int:
    conn = get_connection()
    row = conn.execute(
        "SELECT COALESCE(SUM(quantity), 0) as cnt FROM supplier_purchases WHERE supplier_id=?",
        (supplier_id,)
    ).fetchone()
    conn.close()
    return row["cnt"] if row else 0


class SuppliersPage(QWidget):

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

        title = QLabel("🚚  Suppliers")
        title.setStyleSheet("font-size:20px;font-weight:700;color:#0f172a;")

        self.search = QLineEdit()
        self.search.setPlaceholderText("🔍  Search by name, phone or email…")
        self.search.setFixedWidth(280)
        self.search.setStyleSheet(
            "QLineEdit{border:1.5px solid #e2e8f0;border-radius:8px;"
            "padding:8px 14px;font-size:13px;background:white;}"
            "QLineEdit:focus{border-color:#2e7d32;}")
        self.search.textChanged.connect(self._filter)

        add_btn = QPushButton("➕  Add Supplier")
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
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            "ID", "Name", "Phone", "Email", "Address", "Products",
            "Purchased", "Paid", "Pending", "Last Updated"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setColumnWidth(COL_ID,    45)
        self.table.setColumnWidth(COL_NAME,  180)
        self.table.setColumnWidth(COL_PHONE, 120)
        self.table.setColumnWidth(COL_EMAIL, 180)
        self.table.setColumnWidth(COL_ADDR,  180)
        self.table.setColumnWidth(COL_PRODS, 80)
        self.table.setColumnWidth(COL_PURCHASED, 110)
        self.table.setColumnWidth(COL_PAID, 100)
        self.table.setColumnWidth(COL_PENDING, 110)
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
            ("Record Payment", _GREEN, self._record_payment),
            ("📦  View Products", "QPushButton{background:#eff6ff;color:#1d4ed8;border:1px solid #bfdbfe;"
             "border-radius:8px;font-size:13px;font-weight:600;padding:0 14px;}"
             "QPushButton:hover{background:#dbeafe;}", self._view_products),
            ("✏  Edit",   _GRAY, self._edit),
            ("🗑  Delete", _RED,  self._delete),
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
    def _update_stats(self, suppliers):
        while self._sbar.count():
            item = self._sbar.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        total_prods = sum(s.get("_prod_count", 0) for s in suppliers)
        total_paid = sum(float(s.get("_balance", {}).get("total_paid", 0) or 0) for s in suppliers)
        total_pending = sum(float(s.get("_balance", {}).get("outstanding", 0) or 0) for s in suppliers)
        for text, color in [
            (f"Total Suppliers: <b>{len(suppliers)}</b>", "#475569"),
            (f"📦 Products Supplied: <b>{total_prods}</b>", "#2e7d32"),
            (f"💵 Paid: <b>{format_currency(total_paid)}</b>", "#0f766e"),
            (f"⏳ Pending: <b>{format_currency(total_pending)}</b>", "#dc2626"),
        ]:
            lbl = QLabel(text)
            lbl.setStyleSheet(f"font-size:13px;color:{color};")
            self._sbar.addWidget(lbl)
        self._sbar.addStretch()

    def load_data(self):
        rows = get_all_suppliers()
        for s in rows:
            s["_prod_count"] = _product_count(s["id"])
            s["_balance"] = get_supplier_balance(s["id"])
        self._all = rows
        self._filter()

    def _filter(self):
        q = self.search.text().lower().strip()
        result = [s for s in self._all
                  if not q
                  or q in (s.get("name","") or "").lower()
                  or q in (s.get("phone","") or "").lower()
                  or q in (s.get("email","") or "").lower()]
        self._populate(result)
        self._update_stats(result)

    def _populate(self, suppliers):
        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(suppliers))
        for row, s in enumerate(suppliers):
            cells = [
                str(s.get("id","")),
                s.get("name",""),
                s.get("phone","") or "—",
                s.get("email","") or "—",
                s.get("address","") or "—",
                str(s.get("_prod_count", 0)),
                format_currency((s.get("_balance") or {}).get("purchase_total", 0)),
                format_currency((s.get("_balance") or {}).get("total_paid", 0)),
                format_currency((s.get("_balance") or {}).get("outstanding", 0)),
                format_datetime(s.get("updated_at","") or ""),
            ]
            for col, text in enumerate(cells):
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
                if col == COL_PRODS:
                    item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, col, item)
            self.table.setRowHeight(row, 42)
        self.table.setSortingEnabled(True)

    def _selected(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(self, "Select Row", "Please select a supplier first.")
            return None
        sid = int(self.table.item(row, COL_ID).text())
        return next((s for s in self._all if s["id"] == sid), None)

    def _view_products(self):
        s = self._selected()
        if s:
            SupplierProductsDialog(s).exec()

    def _record_payment(self):
        supplier = self._selected()
        if not supplier:
            return
        outstanding = float((supplier.get("_balance") or {}).get("outstanding", 0) or 0)
        if outstanding <= 0:
            QMessageBox.information(self, "No Balance", "This supplier has no pending balance.")
            return
        if SupplierPaymentDialog(supplier, outstanding).exec():
            self.load_data()

    def _add(self):
        if SupplierDialog().exec():
            self.load_data()

    def _edit(self):
        s = self._selected()
        if s and SupplierDialog(s).exec():
            self.load_data()

    def _delete(self):
        s = self._selected()
        if not s:
            return
        if s.get("_prod_count", 0) > 0:
            QMessageBox.warning(self, "Cannot Delete",
                f"This supplier has {s['_prod_count']} active product(s).\n"
                "Reassign or delete those products first.")
            return
        if QMessageBox.question(self, "Confirm", f"Delete supplier '{s['name']}'?",
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            delete_supplier(s["id"])
            self.load_data()


# ─── Supplier Add/Edit Dialog ─────────────────────────────────────────────────
class SupplierDialog(QDialog):

    def __init__(self, supplier: dict = None):
        super().__init__()
        self.supplier = supplier
        self.setWindowTitle("Edit Supplier" if supplier else "Add Supplier")
        self.resize(440, 320)
        self._build()
        if supplier:
            self._prefill()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 18, 20, 18)
        root.setSpacing(12)

        heading = QLabel("✏  Edit Supplier" if self.supplier else "➕  Add Supplier")
        heading.setStyleSheet("font-size:18px;font-weight:700;color:#0f172a;")
        root.addWidget(heading)

        _fs = ("QLineEdit,QTextEdit{border:1.5px solid #e2e8f0;border-radius:7px;"
               "padding:8px;font-size:13px;background:white;}"
               "QLineEdit:focus,QTextEdit:focus{border-color:#2e7d32;}")

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignRight)

        self.name_i    = QLineEdit(); self.name_i.setStyleSheet(_fs)
        self.phone_i   = QLineEdit(); self.phone_i.setStyleSheet(_fs)
        self.email_i   = QLineEdit(); self.email_i.setStyleSheet(_fs)
        self.address_i = QLineEdit(); self.address_i.setStyleSheet(_fs)
        self.notes_i   = QTextEdit(); self.notes_i.setFixedHeight(60)
        self.notes_i.setStyleSheet(_fs)
        self.opening_i = QDoubleSpinBox()
        self.opening_i.setRange(0, 1_000_000_000)
        self.opening_i.setPrefix("Rs ")
        self.opening_i.setDecimals(2)
        self.opening_i.setStyleSheet(_fs)

        form.addRow("Name *:",   self.name_i)
        form.addRow("Phone:",    self.phone_i)
        form.addRow("Email:",    self.email_i)
        form.addRow("Address:",  self.address_i)
        form.addRow("Opening Balance:", self.opening_i)
        form.addRow("Notes:",    self.notes_i)
        root.addLayout(form)

        btn_row = QHBoxLayout()
        cancel = QPushButton("Cancel"); cancel.setStyleSheet(_GRAY)
        cancel.clicked.connect(self.reject)
        save = QPushButton("Save"); save.setStyleSheet(_GREEN)
        save.clicked.connect(self._save)
        btn_row.addWidget(cancel); btn_row.addStretch(); btn_row.addWidget(save)
        root.addLayout(btn_row)

    def _prefill(self):
        s = self.supplier
        self.name_i.setText(s.get("name",""))
        self.phone_i.setText(s.get("phone","") or "")
        self.email_i.setText(s.get("email","") or "")
        self.address_i.setText(s.get("address","") or "")
        self.notes_i.setPlainText(s.get("notes","") or "")
        self.opening_i.setValue(s.get("opening_balance", 0) or 0)

    def _save(self):
        name = self.name_i.text().strip()
        if not name:
            QMessageBox.warning(self, "Validation", "Name is required.")
            return
        data = {
            "name":    name,
            "phone":   self.phone_i.text().strip(),
            "email":   self.email_i.text().strip(),
            "address": self.address_i.text().strip(),
            "notes":   self.notes_i.toPlainText().strip(),
            "opening_balance": self.opening_i.value(),
        }
        try:
            if self.supplier:
                update_supplier(self.supplier["id"], data)
            else:
                insert_supplier(data)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


# ─── Supplier Products Dialog ─────────────────────────────────────────────────
class SupplierProductsDialog(QDialog):

    def __init__(self, supplier: dict):
        super().__init__()
        self.setWindowTitle(f"Products — {supplier['name']}")
        self.resize(680, 400)
        self._build(supplier)

    def _build(self, supplier):
        from models.product_model import get_supplier_purchase_entries
        from utils.helpers import format_currency

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 14, 16, 14)
        root.setSpacing(10)

        products = get_supplier_purchase_entries(supplier["id"])
        total_purchased_qty = sum(int(p.get("quantity", 0) or 0) for p in products)
        total_purchased_val = sum(float(p.get("total_amount", 0) or 0) for p in products)

        heading = QLabel(
            f"<b>{supplier['name']}</b> — Purchased Products History<br>"
            f"<span style='font-size:12px;color:#475569;'>"
            f"Total Purchased Units: <b>{total_purchased_qty}</b> | Total Value: <b>{format_currency(total_purchased_val)}</b>"
            f"</span>"
        )
        heading.setStyleSheet("font-size:15px;color:#0f172a;")
        root.addWidget(heading)

        table = QTableWidget()
        table.setColumnCount(9)
        table.setHorizontalHeaderLabels(
            ["Entry", "Product", "Batch", "Category", "Purchased Qty",
             "Unit Cost", "Total", "Paid", "Purchase Date"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setAlternatingRowColors(True)
        table.setShowGrid(False)
        table.setStyleSheet(_TABLE_STYLE)
        table.setRowCount(len(products))

        for row, p in enumerate(products):
            for col, val in enumerate([
                str(p.get("id", "")),
                p.get("product_name", "") or "Deleted product",
                p.get("batch_number", "") or "-",
                p.get("category", "") or "-",
                str(p.get("quantity", 0)),
                format_currency(p.get("unit_cost", 0)),
                format_currency(p.get("total_amount", 0)),
                format_currency(p.get("amount_paid", 0)),
                format_datetime(p.get("purchase_date", "") or ""),
            ]):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
                table.setItem(row, col, item)
            table.setRowHeight(row, 40)

        root.addWidget(table)

        close = QPushButton("Close")
        close.setStyleSheet(_GRAY)
        close.clicked.connect(self.accept)
        root.addWidget(close, alignment=Qt.AlignRight)


class SupplierPaymentDialog(QDialog):

    def __init__(self, supplier: dict, outstanding: float):
        super().__init__()
        self.supplier = supplier
        self.setWindowTitle("Record Supplier Payment")
        self.resize(420, 250)

        root = QVBoxLayout(self)
        root.addWidget(QLabel(
            f"<b>{supplier['name']}</b><br>Outstanding: {format_currency(outstanding)}"
        ))
        form = QFormLayout()
        self.amount = QDoubleSpinBox()
        self.amount.setRange(0.01, outstanding)
        self.amount.setValue(outstanding)
        self.amount.setPrefix("Rs ")
        self.amount.setDecimals(2)
        self.method = QComboBox()
        self.method.addItems(PAYMENT_METHODS)
        self.notes = QLineEdit()
        form.addRow("Amount:", self.amount)
        form.addRow("Payment Method:", self.method)
        form.addRow("Notes:", self.notes)
        root.addLayout(form)

        buttons = QHBoxLayout()
        cancel = QPushButton("Cancel")
        cancel.setStyleSheet(_GRAY)
        cancel.clicked.connect(self.reject)
        save = QPushButton("Confirm Payment")
        save.setStyleSheet(_GREEN)
        save.clicked.connect(self._save)
        buttons.addWidget(cancel)
        buttons.addStretch()
        buttons.addWidget(save)
        root.addLayout(buttons)

    def _save(self):
        try:
            user_id = session.user.get("id") if session.user else None
            record_supplier_payment(
                self.supplier["id"], self.amount.value(),
                self.method.currentText(), self.notes.text().strip(), user_id,
            )
            self.accept()
        except Exception as exc:
            QMessageBox.critical(self, "Payment Error", str(exc))
