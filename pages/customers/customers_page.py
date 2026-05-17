from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QLineEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QMessageBox, QDialog,
    QFormLayout, QTextEdit, QDoubleSpinBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

import os
from models.customer_model import (
    get_all_customers, insert_customer, update_customer, delete_customer
)
from models.sale_model import get_all_sales, get_sale_items
from utils.helpers import format_currency, format_datetime

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
_BLUE  = ("QPushButton{background:#eff6ff;color:#1d4ed8;border:1px solid #bfdbfe;"
          "border-radius:8px;font-size:13px;font-weight:600;padding:8px 14px;}"
          "QPushButton:hover{background:#dbeafe;}")
_RED   = ("QPushButton{background:#fef2f2;color:#dc2626;border:1px solid #fecaca;"
          "border-radius:8px;font-size:13px;font-weight:600;padding:8px 14px;}"
          "QPushButton:hover{background:#fee2e2;}")
_GRAY  = ("QPushButton{background:#f1f5f9;color:#475569;border-radius:8px;"
          "padding:8px 14px;font-size:13px;border:1.5px solid #e2e8f0;}"
          "QPushButton:hover{background:#e2e8f0;}")

COL_ID    = 0
COL_NAME  = 1
COL_PHONE = 2
COL_ADDR  = 3
COL_PAID  = 4
COL_PEND  = 5
COL_LAST  = 6


class CustomersPage(QWidget):

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

        title = QLabel("👥  Customers")
        title.setStyleSheet("font-size:20px;font-weight:700;color:#0f172a;")

        self.search = QLineEdit()
        self.search.setPlaceholderText("🔍  Search by name or phone…")
        self.search.setFixedWidth(260)
        self.search.setStyleSheet(
            "QLineEdit{border:1.5px solid #e2e8f0;border-radius:8px;"
            "padding:8px 14px;font-size:13px;background:white;}"
            "QLineEdit:focus{border-color:#2e7d32;}")
        self.search.textChanged.connect(self._filter)

        add_btn = QPushButton("➕  Add Customer")
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
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "Name", "Phone", "Address",
            "Total Paid", "Pending", "Last Purchase"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setColumnWidth(COL_ID,    45)
        self.table.setColumnWidth(COL_NAME,  180)
        self.table.setColumnWidth(COL_PHONE, 120)
        self.table.setColumnWidth(COL_ADDR,  180)
        self.table.setColumnWidth(COL_PAID,  120)
        self.table.setColumnWidth(COL_PEND,  120)
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
            ("📋  History",       _BLUE, self._history),
            ("�  Statement PDF", _GREEN.replace("#2e7d32","#7c3aed").replace("#1b5e20","#6d28d9"), self._statement),
            ("�💵  Add Payment",   _GREEN.replace("#2e7d32","#0369a1").replace("#1b5e20","#075985"), self._payment),
            ("✏  Edit",           _GRAY, self._edit),
            ("🗑  Delete",         _RED,  self._delete),
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
    def _update_stats(self, customers):
        while self._sbar.count():
            item = self._sbar.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        total_paid = sum(c.get("total_paid", 0) or 0 for c in customers)
        total_pend = sum(c.get("total_pending", 0) or 0 for c in customers)
        for text, color in [
            (f"Total: <b>{len(customers)}</b>", "#475569"),
            (f"💰 Collected: <b>{format_currency(total_paid)}</b>", "#2e7d32"),
            (f"⏳ Pending: <b>{format_currency(total_pend)}</b>", "#ef4444"),
        ]:
            lbl = QLabel(text)
            lbl.setStyleSheet(f"font-size:13px;color:{color};")
            self._sbar.addWidget(lbl)
        self._sbar.addStretch()

    def load_data(self):
        self._all = get_all_customers()
        self._filter()

    def _filter(self):
        q = self.search.text().lower().strip()
        result = [c for c in self._all
                  if not q or q in (c.get("name","") or "").lower()
                  or q in (c.get("phone","") or "").lower()]
        self._populate(result)
        self._update_stats(result)

    def _populate(self, customers):
        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(customers))
        for row, c in enumerate(customers):
            pend = c.get("total_pending", 0) or 0
            cells = [
                str(c.get("id","")),
                c.get("name",""),
                c.get("phone","") or "—",
                c.get("address","") or "—",
                format_currency(c.get("total_paid",0) or 0),
                format_currency(pend),
                format_datetime(c.get("last_purchase_date","") or ""),
            ]
            for col, text in enumerate(cells):
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
                if col == COL_PEND and pend > 0:
                    item.setForeground(QColor("#dc2626"))
                self.table.setItem(row, col, item)
            self.table.setRowHeight(row, 42)
        self.table.setSortingEnabled(True)

    def _selected(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(self, "Select Row", "Please select a customer first.")
            return None
        cid = int(self.table.item(row, COL_ID).text())
        return next((c for c in self._all if c["id"] == cid), None)

    def _add(self):
        dlg = CustomerDialog()
        if dlg.exec():
            self.load_data()

    def _edit(self):
        c = self._selected()
        if c:
            dlg = CustomerDialog(c)
            if dlg.exec():
                self.load_data()

    def _delete(self):
        c = self._selected()
        if not c:
            return
        if QMessageBox.question(self, "Confirm", f"Delete customer '{c['name']}'?",
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            delete_customer(c["id"])
            self.load_data()

    def _history(self):
        c = self._selected()
        if c:
            PurchaseHistoryDialog(c).exec()

    def _statement(self):
        c = self._selected()
        if not c:
            return
        sales = self._sales_for(c)
        if not sales:
            QMessageBox.information(self, "No Sales",
                "No sales records found for this customer.")
            return
        try:
            from services.export_service import export_customer_statement
            path = export_customer_statement(c, sales)
            QMessageBox.information(self, "Statement Generated",
                f"PDF saved to:\n{path}")
            os.startfile(path)
        except Exception as e:
            QMessageBox.critical(self, "Export Error", str(e))

    @staticmethod
    def _sales_for(customer: dict) -> list:
        sales = [s for s in get_all_sales() if s.get("customer_id") == customer["id"]]
        for s in sales:
            items = get_sale_items(s["id"])
            s["_product"] = items[0]["product_name"] if items else "—"
            s["_qty"]     = sum(i["quantity"] for i in items)
        return sales

    def _payment(self):
        c = self._selected()
        if not c:
            return
        pend = c.get("total_pending", 0) or 0
        if pend <= 0:
            QMessageBox.information(self, "No Pending", "This customer has no pending balance.")
            return
        CustomerPaymentDialog(c, self.load_data).exec()


# ─── Customer Add/Edit Dialog ────────────────────────────────────────────────
class CustomerDialog(QDialog):

    def __init__(self, customer: dict = None):
        super().__init__()
        self.customer = customer
        self.setWindowTitle("Edit Customer" if customer else "Add Customer")
        self.resize(420, 300)
        self._build()
        if customer:
            self._prefill()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 18, 20, 18)
        root.setSpacing(12)

        heading = QLabel("✏  Edit Customer" if self.customer else "➕  Add Customer")
        heading.setStyleSheet("font-size:18px;font-weight:700;color:#0f172a;")
        root.addWidget(heading)

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignRight)

        self.name_input    = QLineEdit()
        self.phone_input   = QLineEdit()
        self.address_input = QLineEdit()
        self.notes_input   = QTextEdit()
        self.notes_input.setFixedHeight(60)

        _field_style = ("QLineEdit,QTextEdit{border:1.5px solid #e2e8f0;border-radius:7px;"
                        "padding:8px;font-size:13px;background:white;}"
                        "QLineEdit:focus,QTextEdit:focus{border-color:#2e7d32;}")
        for w in (self.name_input, self.phone_input, self.address_input, self.notes_input):
            w.setStyleSheet(_field_style)

        form.addRow("Name *:",    self.name_input)
        form.addRow("Phone:",     self.phone_input)
        form.addRow("Address:",   self.address_input)
        form.addRow("Notes:",     self.notes_input)
        root.addLayout(form)

        btn_row = QHBoxLayout()
        cancel = QPushButton("Cancel")
        cancel.setStyleSheet(_GRAY)
        cancel.clicked.connect(self.reject)
        save = QPushButton("Save")
        save.setStyleSheet(_GREEN)
        save.clicked.connect(self._save)
        btn_row.addWidget(cancel)
        btn_row.addStretch()
        btn_row.addWidget(save)
        root.addLayout(btn_row)

    def _prefill(self):
        c = self.customer
        self.name_input.setText(c.get("name",""))
        self.phone_input.setText(c.get("phone","") or "")
        self.address_input.setText(c.get("address","") or "")
        self.notes_input.setPlainText(c.get("notes","") or "")

    def _save(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Validation", "Name is required.")
            return
        data = {
            "name":    name,
            "phone":   self.phone_input.text().strip(),
            "address": self.address_input.text().strip(),
            "notes":   self.notes_input.toPlainText().strip(),
        }
        try:
            if self.customer:
                update_customer(self.customer["id"], data)
            else:
                insert_customer(data)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


# ─── Purchase History Dialog ─────────────────────────────────────────────────
class PurchaseHistoryDialog(QDialog):

    def __init__(self, customer: dict):
        super().__init__()
        self.setWindowTitle(f"Purchase History — {customer['name']}")
        self.resize(700, 400)
        self._build(customer)

    def _build(self, customer):
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 14, 16, 14)
        root.setSpacing(10)

        heading = QLabel(f"<b>{customer['name']}</b>  purchase history")
        heading.setStyleSheet("font-size:15px;color:#0f172a;")
        root.addWidget(heading)

        sales = [s for s in get_all_sales() if s.get("customer_id") == customer["id"]]

        table = QTableWidget()
        table.setColumnCount(7)
        table.setHorizontalHeaderLabels(
            ["Invoice", "Product", "Qty", "Total", "Paid", "Remaining", "Date"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setAlternatingRowColors(True)
        table.setShowGrid(False)
        table.setStyleSheet(_TABLE_STYLE)
        table.setRowCount(len(sales))

        for row, s in enumerate(sales):
            items  = get_sale_items(s["id"])
            prod   = items[0]["product_name"] if items else "—"
            qty    = sum(i["quantity"] for i in items)
            rem    = s.get("remaining_amount", 0) or 0
            cells  = [
                s.get("invoice_number",""),
                prod, str(qty),
                format_currency(s.get("total_amount",0) or 0),
                format_currency(s.get("paid_amount",0) or 0),
                format_currency(rem),
                format_datetime(s.get("sale_date","") or ""),
            ]
            for col, text in enumerate(cells):
                item = QTableWidgetItem(text)
                if col == 5 and rem > 0:
                    item.setForeground(QColor("#dc2626"))
                table.setItem(row, col, item)
            table.setRowHeight(row, 40)

        root.addWidget(table)

        close = QPushButton("Close")
        close.setStyleSheet(_GRAY)
        close.clicked.connect(self.accept)
        root.addWidget(close, alignment=Qt.AlignRight)


# ─── Customer Payment Dialog ─────────────────────────────────────────────────
class CustomerPaymentDialog(QDialog):

    def __init__(self, customer: dict, refresh_cb):
        super().__init__()
        self.customer = customer
        self.refresh_cb = refresh_cb
        self.setWindowTitle(f"Add Payment — {customer['name']}")
        self.resize(380, 220)
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 18, 20, 18)
        root.setSpacing(12)

        pend = self.customer.get("total_pending", 0) or 0
        root.addWidget(QLabel(f"<b>Customer:</b>  {self.customer['name']}"))
        root.addWidget(QLabel(f"<b>Pending Balance:</b>  {format_currency(pend)}"))

        form = QFormLayout()
        self.amount_spin = QDoubleSpinBox()
        self.amount_spin.setRange(0.01, pend)
        self.amount_spin.setValue(pend)
        self.amount_spin.setPrefix("Rs ")
        self.amount_spin.setDecimals(0)
        self.amount_spin.setStyleSheet(
            "QDoubleSpinBox{border:1.5px solid #e2e8f0;border-radius:7px;"
            "padding:8px;font-size:13px;}")
        form.addRow("Amount:", self.amount_spin)
        root.addLayout(form)

        btn_row = QHBoxLayout()
        cancel = QPushButton("Cancel")
        cancel.setStyleSheet(_GRAY)
        cancel.clicked.connect(self.reject)
        ok = QPushButton("✅  Confirm")
        ok.setStyleSheet(_GREEN)
        ok.clicked.connect(self._confirm)
        btn_row.addWidget(cancel)
        btn_row.addStretch()
        btn_row.addWidget(ok)
        root.addLayout(btn_row)

    def _confirm(self):
        from database.connection import get_connection
        amount = self.amount_spin.value()
        pend   = self.customer.get("total_pending", 0) or 0
        paid   = self.customer.get("total_paid", 0) or 0
        conn = get_connection()
        conn.execute(
            "UPDATE customers SET total_paid=?, total_pending=?, "
            "updated_at=datetime('now','localtime') WHERE id=?",
            (paid + amount, max(0.0, pend - amount), self.customer["id"])
        )
        conn.commit()
        conn.close()
        QMessageBox.information(self, "Success",
            f"Payment of {format_currency(amount)} recorded.")
        self.refresh_cb()
        self.accept()
