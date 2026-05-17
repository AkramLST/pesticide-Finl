import os
import webbrowser
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QLineEdit, QComboBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QMessageBox, QDialog,
    QScrollArea, QFormLayout, QDoubleSpinBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from models.sale_model import get_all_sales, get_sale_items, soft_delete_sale
from utils.helpers import format_currency, format_datetime
from utils.config import PAYMENT_METHODS, INVOICES_DIR

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

COL_ID   = 0
COL_INV  = 1
COL_CUST = 2
COL_PROD = 3
COL_QTY  = 4
COL_DISC = 5
COL_TOTAL= 6
COL_PAID = 7
COL_REM  = 8
COL_MTH  = 9
COL_DATE = 10
COL_BY   = 11


class SalesPage(QWidget):

    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("background:#f1f5f9;")
        self._all_sales = []
        self._build_ui()
        self.load_data()

    # ─────────────────────────────────────────────────────
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

        title = QLabel("🛒  Sales")
        title.setStyleSheet("font-size:20px;font-weight:700;color:#0f172a;")

        self.search = QLineEdit()
        self.search.setPlaceholderText("🔍  Search invoice # or customer…")
        self.search.setFixedWidth(240)
        self.search.setStyleSheet(
            "QLineEdit{border:1.5px solid #e2e8f0;border-radius:8px;"
            "padding:8px 14px;font-size:13px;background:white;}"
            "QLineEdit:focus{border-color:#2e7d32;}")
        self.search.textChanged.connect(self._filter)

        self.method_cb = QComboBox()
        self.method_cb.setFixedWidth(140)
        self.method_cb.addItem("All Methods")
        self.method_cb.addItems(PAYMENT_METHODS)
        self.method_cb.setStyleSheet(
            "QComboBox{border:1.5px solid #e2e8f0;border-radius:8px;"
            "padding:7px 12px;font-size:13px;background:white;}"
            "QComboBox::drop-down{border:none;}")
        self.method_cb.currentTextChanged.connect(self._filter)

        self.status_cb = QComboBox()
        self.status_cb.setFixedWidth(140)
        self.status_cb.addItems(["All Status", "Fully Paid", "Pending"])
        self.status_cb.setStyleSheet(self.method_cb.styleSheet())
        self.status_cb.currentTextChanged.connect(self._filter)

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
        hl.addWidget(self.method_cb)
        hl.addWidget(self.status_cb)
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
        self.table.setColumnCount(12)
        self.table.setHorizontalHeaderLabels([
            "ID", "Invoice #", "Customer", "Product",
            "Qty", "Discount", "Total", "Paid",
            "Remaining", "Method", "Date", "Sold By"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setColumnWidth(COL_ID,   45)
        self.table.setColumnWidth(COL_INV,  110)
        self.table.setColumnWidth(COL_CUST, 130)
        self.table.setColumnWidth(COL_PROD, 150)
        self.table.setColumnWidth(COL_QTY,  50)
        self.table.setColumnWidth(COL_DISC, 80)
        self.table.setColumnWidth(COL_TOTAL,100)
        self.table.setColumnWidth(COL_PAID, 100)
        self.table.setColumnWidth(COL_REM,  100)
        self.table.setColumnWidth(COL_MTH,  110)
        self.table.setColumnWidth(COL_DATE, 140)

        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.setSortingEnabled(True)
        self.table.setStyleSheet(_TABLE_STYLE)
        self.table.doubleClicked.connect(self._view_invoice)

        # Action bar below table
        wrap = QFrame()
        wrap.setAttribute(Qt.WA_StyledBackground, True)
        wrap.setStyleSheet("background:white;border:none;")
        wl = QVBoxLayout(wrap)
        wl.setContentsMargins(16, 12, 16, 8)
        wl.setSpacing(6)

        act_row = QHBoxLayout()
        view_btn = QPushButton("📄  View Invoice")
        view_btn.setFixedHeight(36)
        view_btn.setStyleSheet(
            "QPushButton{background:#eff6ff;color:#1d4ed8;border:1px solid #bfdbfe;"
            "border-radius:8px;font-size:13px;font-weight:600;padding:0 16px;}"
            "QPushButton:hover{background:#dbeafe;}")
        view_btn.clicked.connect(self._view_invoice)

        pay_btn = QPushButton("💵  Record Payment")
        pay_btn.setFixedHeight(36)
        pay_btn.setStyleSheet(
            "QPushButton{background:#d1fae5;color:#065f46;border:1px solid #6ee7b7;"
            "border-radius:8px;font-size:13px;font-weight:600;padding:0 16px;}"
            "QPushButton:hover{background:#a7f3d0;}")
        pay_btn.clicked.connect(self._record_payment)

        del_btn = QPushButton("🗑  Delete Sale")
        del_btn.setFixedHeight(36)
        del_btn.setStyleSheet(
            "QPushButton{background:#fef2f2;color:#dc2626;border:1px solid #fecaca;"
            "border-radius:8px;font-size:13px;font-weight:600;padding:0 16px;}"
            "QPushButton:hover{background:#fee2e2;}")
        del_btn.clicked.connect(self._delete_sale)

        xl_btn = QPushButton("📊  Export Excel")
        xl_btn.setFixedHeight(36)
        xl_btn.setStyleSheet(
            "QPushButton{background:#d1fae5;color:#065f46;border:1px solid #6ee7b7;"
            "border-radius:8px;font-size:13px;font-weight:600;padding:0 16px;}"
            "QPushButton:hover{background:#a7f3d0;}")
        xl_btn.clicked.connect(self._export_excel)

        pdf_btn = QPushButton("📄  Export PDF")
        pdf_btn.setFixedHeight(36)
        pdf_btn.setStyleSheet(
            "QPushButton{background:#fef3c7;color:#92400e;border:1px solid #fde68a;"
            "border-radius:8px;font-size:13px;font-weight:600;padding:0 16px;}"
            "QPushButton:hover{background:#fef9c3;}")
        pdf_btn.clicked.connect(self._export_pdf)

        hint = QLabel("Double-click a row to open invoice PDF")
        hint.setStyleSheet("font-size:12px;color:#94a3b8;")

        act_row.addWidget(view_btn)
        act_row.addWidget(pay_btn)
        act_row.addWidget(del_btn)
        act_row.addStretch()
        act_row.addWidget(xl_btn)
        act_row.addWidget(pdf_btn)
        act_row.addWidget(hint)

        wl.addWidget(self.table)
        wl.addLayout(act_row)
        root.addWidget(wrap)

    # ─────────────────────────────────────────────────────
    def _update_stats(self, sales):
        while self._sbar.count():
            item = self._sbar.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        total_rev  = sum(s.get("total_amount", 0) or 0 for s in sales)
        total_paid = sum(s.get("paid_amount",  0) or 0 for s in sales)
        total_pend = sum(s.get("remaining_amount", 0) or 0 for s in sales)
        pending_cnt = sum(1 for s in sales if (s.get("remaining_amount") or 0) > 0)

        for text, color in [
            (f"Showing  <b>{len(sales)}</b>  sales", "#475569"),
            (f"💰 Revenue: <b>{format_currency(total_rev)}</b>", "#2e7d32"),
            (f"✅ Collected: <b>{format_currency(total_paid)}</b>", "#10b981"),
            (f"⏳ Pending: <b>{format_currency(total_pend)}</b>  ({pending_cnt} sales)", "#ef4444"),
        ]:
            lbl = QLabel(text)
            lbl.setStyleSheet(f"font-size:13px;color:{color};")
            self._sbar.addWidget(lbl)
        self._sbar.addStretch()

    # ─────────────────────────────────────────────────────
    def load_data(self):
        raw = get_all_sales()
        # Enrich with first product name from sale_items
        for s in raw:
            items = get_sale_items(s["id"])
            s["_product"] = items[0]["product_name"] if items else "—"
            s["_qty"]     = sum(i["quantity"] for i in items)
        self._all_sales = raw
        self._filter()

    def _filter(self):
        q       = self.search.text().lower().strip()
        method  = self.method_cb.currentText()
        status  = self.status_cb.currentText()

        result = []
        for s in self._all_sales:
            if q and q not in (s.get("invoice_number","") or "").lower() \
                 and q not in (s.get("customer_name","") or "").lower():
                continue
            if method != "All Methods" and s.get("payment_method","") != method:
                continue
            rem = s.get("remaining_amount", 0) or 0
            if status == "Fully Paid"  and rem > 0:    continue
            if status == "Pending"     and rem <= 0:   continue
            result.append(s)

        self._populate(result)
        self._update_stats(result)

    def _populate(self, sales):
        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(sales))
        for row, s in enumerate(sales):
            rem = s.get("remaining_amount", 0) or 0
            row_color = QColor("#fef2f2") if rem > 0 else None

            cells = [
                str(s.get("id","")),
                s.get("invoice_number",""),
                s.get("customer_name") or "Walk-in",
                s.get("_product",""),
                str(s.get("_qty","")),
                format_currency(s.get("discount",0) or 0),
                format_currency(s.get("total_amount",0) or 0),
                format_currency(s.get("paid_amount",0) or 0),
                format_currency(rem),
                s.get("payment_method",""),
                format_datetime(s.get("sale_date","") or ""),
                s.get("seller_name") or s.get("sold_by","") or "—",
            ]
            for col, text in enumerate(cells):
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
                if row_color:
                    item.setBackground(row_color)
                if col == COL_REM and rem > 0:
                    item.setForeground(QColor("#dc2626"))
                elif col == COL_REM:
                    item.setForeground(QColor("#16a34a"))
                if col in (COL_QTY,):
                    item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, col, item)
            self.table.setRowHeight(row, 42)
        self.table.setSortingEnabled(True)

    # ─────────────────────────────────────────────────────
    def _selected_sale(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(self, "Select Row", "Please select a sale first.")
            return None
        sale_id = int(self.table.item(row, COL_ID).text())
        return next((s for s in self._all_sales if s["id"] == sale_id), None)

    def _view_invoice(self):
        sale = self._selected_sale()
        if not sale:
            return
        inv = sale.get("invoice_number","")
        pdf = os.path.join(INVOICES_DIR, f"{inv}.pdf")
        if os.path.exists(pdf):
            try:
                os.startfile(pdf)
            except Exception as e:
                QMessageBox.warning(self, "Error", str(e))
        else:
            QMessageBox.information(self, "Not Found",
                f"Invoice PDF not found:\n{pdf}")

    def _record_payment(self):
        sale = self._selected_sale()
        if not sale:
            return
        rem = sale.get("remaining_amount", 0) or 0
        if rem <= 0:
            QMessageBox.information(self, "Fully Paid", "This sale is already fully paid.")
            return
        PaymentDialog(sale, self.load_data).exec()

    def _export_excel(self):
        if not self._all_sales:
            QMessageBox.information(self, "Empty", "No data to export.")
            return
        try:
            from services.export_service import export_sales_excel
            path = export_sales_excel(self._all_sales)
            QMessageBox.information(self, "Exported", f"Excel saved to:\n{path}")
            os.startfile(path)
        except Exception as e:
            QMessageBox.critical(self, "Export Error", str(e))

    def _export_pdf(self):
        if not self._all_sales:
            QMessageBox.information(self, "Empty", "No data to export.")
            return
        try:
            from services.export_service import export_sales_pdf
            path = export_sales_pdf(self._all_sales)
            QMessageBox.information(self, "Exported", f"PDF saved to:\n{path}")
            os.startfile(path)
        except Exception as e:
            QMessageBox.critical(self, "Export Error", str(e))

    def _delete_sale(self):
        sale = self._selected_sale()
        if not sale:
            return
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Delete sale {sale.get('invoice_number','')}?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            soft_delete_sale(sale["id"])
            self.load_data()


# ─── Payment Dialog ─────────────────────────────────────────────────────────
class PaymentDialog(QDialog):

    def __init__(self, sale: dict, refresh_cb):
        super().__init__()
        self.sale = sale
        self.refresh_cb = refresh_cb
        self.setWindowTitle("Record Payment")
        self.resize(380, 240)
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setSpacing(14)
        root.setContentsMargins(20, 18, 20, 18)

        rem = self.sale.get("remaining_amount", 0) or 0
        root.addWidget(QLabel(f"<b>Invoice:</b>  {self.sale.get('invoice_number','')}"))
        root.addWidget(QLabel(f"<b>Remaining:</b>  {format_currency(rem)}"))

        form = QFormLayout()
        self.amount_spin = QDoubleSpinBox()
        self.amount_spin.setRange(0.01, rem)
        self.amount_spin.setValue(rem)
        self.amount_spin.setPrefix("Rs ")
        self.amount_spin.setDecimals(0)
        self.amount_spin.setStyleSheet(
            "QDoubleSpinBox{border:1.5px solid #e2e8f0;border-radius:7px;"
            "padding:8px;font-size:13px;}")
        form.addRow("Amount to Pay:", self.amount_spin)
        root.addLayout(form)

        btn_row = QHBoxLayout()
        ok = QPushButton("✅  Confirm Payment")
        ok.setStyleSheet(
            "QPushButton{background:#2e7d32;color:white;border-radius:8px;"
            "padding:10px 20px;font-size:13px;font-weight:700;border:none;}"
            "QPushButton:hover{background:#1b5e20;}")
        ok.clicked.connect(self._confirm)
        cancel = QPushButton("Cancel")
        cancel.setStyleSheet(
            "QPushButton{background:#f1f5f9;color:#475569;border-radius:8px;"
            "padding:10px 16px;font-size:13px;border:1.5px solid #e2e8f0;}"
            "QPushButton:hover{background:#e2e8f0;}")
        cancel.clicked.connect(self.reject)
        btn_row.addWidget(cancel)
        btn_row.addWidget(ok)
        root.addLayout(btn_row)

    def _confirm(self):
        from database.connection import get_connection
        amount = self.amount_spin.value()
        rem    = self.sale.get("remaining_amount", 0) or 0
        new_paid = (self.sale.get("paid_amount", 0) or 0) + amount
        new_rem  = max(0.0, rem - amount)
        conn = get_connection()
        conn.execute(
            "UPDATE sales SET paid_amount=?, remaining_amount=? WHERE id=?",
            (new_paid, new_rem, self.sale["id"])
        )
        conn.commit()
        conn.close()
        QMessageBox.information(self, "Success",
            f"Payment of {format_currency(amount)} recorded.\n"
            f"Remaining: {format_currency(new_rem)}")
        self.refresh_cb()
        self.accept()
