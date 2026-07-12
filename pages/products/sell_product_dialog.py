import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QSpinBox, QDoubleSpinBox,
    QFormLayout, QFrame, QMessageBox, QTabWidget, QWidget,
    QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt, Signal

from models.product_model import get_product_by_id, deduct_stock
from models.customer_model import get_all_customers, insert_customer
from models.sale_model import insert_sale
from models.payment_model import record_sale_payment
from utils.config import PAYMENT_METHODS
from utils.session import session
from utils.helpers import format_currency, generate_invoice_number
from services.invoice_service import generate_invoice

_GREEN_BTN = """
    QPushButton { background:#2e7d32; color:white; padding:10px 20px;
        border-radius:8px; font-size:14px; font-weight:bold; border:none; }
    QPushButton:hover { background:#1b5e20; }
"""
_GRAY_BTN = """
    QPushButton { background:#f1f5f9; color:#475569; padding:10px 20px;
        border-radius:8px; font-size:13px; border:1.5px solid #e2e8f0; }
    QPushButton:hover { background:#e2e8f0; }
"""
_FIELD = """
    QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
        padding: 8px 10px; border: 1.5px solid #e2e8f0;
        border-radius: 7px; font-size: 13px; background: white;
    }
    QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
        border-color: #2e7d32;
    }
    QLineEdit[readOnly="true"] { background: #f8fafc; color: #64748b; }
"""


class SellProductDialog(QDialog):

    sale_completed = Signal()

    def __init__(self, product: dict):
        super().__init__()
        self.product = product
        self.setWindowTitle(f"Sell — {product.get('name', '')}")
        self.resize(560, 660)
        self._customer_id = None
        self._build_ui()

    # ─────────────────────────────────────────────────────
    def _build_ui(self):
        self.setStyleSheet(_FIELD + "QDialog { background:#f8fafc; }")
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        content = QWidget()
        content.setStyleSheet("background:#f8fafc;")
        root = QVBoxLayout(content)
        root.setContentsMargins(22, 18, 22, 18)
        root.setSpacing(14)
        scroll.setWidget(content)
        outer.addWidget(scroll)

        # ── Product info card
        pcard = QFrame()
        pcard.setAttribute(Qt.WA_StyledBackground, True)
        pcard.setStyleSheet("background:white;border-radius:10px;border:1px solid #e2e8f0;")
        pc_layout = QHBoxLayout(pcard)
        pc_layout.setContentsMargins(14, 12, 14, 12)

        p = self.product
        name_lbl = QLabel(f"<b>{p.get('name','')}</b>")
        name_lbl.setStyleSheet("font-size:15px;color:#0f172a;")
        avail_lbl = QLabel(f"Available: <b>{p.get('quantity', 0)}</b> units")
        avail_lbl.setStyleSheet("font-size:13px;color:#475569;")
        price_lbl = QLabel(f"Unit Price: <b>{format_currency(p.get('sale_price', 0))}</b>")
        price_lbl.setStyleSheet("font-size:13px;color:#2e7d32;")

        info_col = QVBoxLayout()
        info_col.addWidget(name_lbl)
        info_col.addWidget(avail_lbl)
        info_col.addWidget(price_lbl)
        pc_layout.addLayout(info_col)
        root.addWidget(pcard)

        # ── Sale fields
        sale_frame = QFrame()
        sale_frame.setAttribute(Qt.WA_StyledBackground, True)
        sale_frame.setStyleSheet("background:white;border-radius:10px;border:1px solid #e2e8f0;")
        sf_layout = QVBoxLayout(sale_frame)
        sf_layout.setContentsMargins(16, 14, 16, 14)

        sale_lbl = QLabel("Sale Details")
        sale_lbl.setStyleSheet("font-size:14px;font-weight:700;color:#0f172a;")
        sf_layout.addWidget(sale_lbl)

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignRight)

        self.qty_spin = QSpinBox()
        self.qty_spin.setRange(1, p.get("quantity", 1) or 1)
        self.qty_spin.setValue(1)
        self.qty_spin.valueChanged.connect(self._recalculate)

        self.discount_spin = QDoubleSpinBox()
        self.discount_spin.setRange(0, 100)
        self.discount_spin.setSuffix(" %")
        self.discount_spin.setDecimals(1)
        self.discount_spin.valueChanged.connect(self._recalculate)

        self.total_lbl = QLineEdit("0")
        self.total_lbl.setReadOnly(True)

        self.paid_spin = QDoubleSpinBox()
        self.paid_spin.setRange(0, 9_999_999)
        self.paid_spin.setPrefix("Rs ")
        self.paid_spin.setDecimals(0)
        self.paid_spin.valueChanged.connect(self._recalculate)

        self.remaining_lbl = QLineEdit("0")
        self.remaining_lbl.setReadOnly(True)

        self.payment_combo = QComboBox()
        self.payment_combo.addItems(PAYMENT_METHODS)

        form.addRow("Quantity *:", self.qty_spin)
        form.addRow("Discount:", self.discount_spin)
        form.addRow("Total Amount:", self.total_lbl)
        form.addRow("Amount Paid:", self.paid_spin)
        form.addRow("Remaining:", self.remaining_lbl)
        form.addRow("Payment Method:", self.payment_combo)
        sf_layout.addLayout(form)
        root.addWidget(sale_frame)

        # ── Customer section (tabs)
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border:1px solid #e2e8f0; border-radius:10px;
                background:white; }
            QTabBar::tab { padding:8px 18px; font-size:13px; color:#64748b; }
            QTabBar::tab:selected { color:#2e7d32; border-bottom:2px solid #2e7d32;
                font-weight:700; }
        """)

        # Tab 1: Existing customer
        ex_tab = QWidget()
        ex_tab.setStyleSheet("background:white;")
        ex_layout = QVBoxLayout(ex_tab)
        ex_layout.setContentsMargins(14, 12, 14, 12)

        self.cust_search = QLineEdit()
        self.cust_search.setPlaceholderText("Search customer by name or phone…")
        self.cust_search.textChanged.connect(self._filter_customers)

        self.cust_combo = QComboBox()
        self.cust_combo.setFixedHeight(36)
        self._customers = get_all_customers()
        self._populate_customers(self._customers)
        self.cust_combo.currentIndexChanged.connect(self._on_customer_selected)

        ex_layout.addWidget(QLabel("Search:"))
        ex_layout.addWidget(self.cust_search)
        ex_layout.addWidget(QLabel("Select Customer:"))
        ex_layout.addWidget(self.cust_combo)
        ex_layout.addStretch()

        # Tab 2: New customer
        new_tab = QWidget()
        new_tab.setStyleSheet("background:white;")
        new_layout = QFormLayout(new_tab)
        new_layout.setContentsMargins(14, 12, 14, 12)
        new_layout.setSpacing(10)
        new_layout.setLabelAlignment(Qt.AlignRight)

        self.new_name    = QLineEdit()
        self.new_phone   = QLineEdit()
        self.new_address = QLineEdit()
        self.new_notes   = QLineEdit()

        new_layout.addRow("Name *:",    self.new_name)
        new_layout.addRow("Phone:",     self.new_phone)
        new_layout.addRow("Address:",   self.new_address)
        new_layout.addRow("Notes:",     self.new_notes)

        self.tabs.addTab(ex_tab,  "👥  Existing Customer")
        self.tabs.addTab(new_tab, "➕  New Customer")
        root.addWidget(self.tabs)

        # ── Buttons
        btn_row = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet(_GRAY_BTN)
        cancel_btn.clicked.connect(self.reject)
        confirm_btn = QPushButton("✅  Confirm Sale")
        confirm_btn.setStyleSheet(_GREEN_BTN)
        confirm_btn.clicked.connect(self._confirm)
        btn_row.addWidget(cancel_btn)
        btn_row.addStretch()
        btn_row.addWidget(confirm_btn)
        root.addLayout(btn_row)

        self._recalculate()

    # ─────────────────────────────────────────────────────
    def _recalculate(self):
        unit_price = self.product.get("sale_price", 0) or 0
        qty        = self.qty_spin.value()
        disc_pct   = self.discount_spin.value()
        subtotal   = unit_price * qty
        disc_amt   = subtotal * disc_pct / 100
        total      = subtotal - disc_amt
        paid       = self.paid_spin.value()
        remaining  = max(0.0, total - paid)
        self.total_lbl.setText(format_currency(total))
        self.remaining_lbl.setText(format_currency(remaining))
        self.remaining_lbl.setStyleSheet(
            "color:#dc2626; font-weight:600;" if remaining > 0
            else "color:#16a34a; font-weight:600;"
        )

    def _populate_customers(self, customers):
        self.cust_combo.blockSignals(True)
        self.cust_combo.clear()
        self.cust_combo.addItem("— Walk-in (no customer) —", None)
        for c in customers:
            self.cust_combo.addItem(f"{c['name']}  ({c.get('phone','') or 'no phone'})", c["id"])
        self.cust_combo.blockSignals(False)

    def _filter_customers(self, text: str):
        filtered = [c for c in self._customers
                    if text.lower() in c.get("name", "").lower()
                    or text.lower() in (c.get("phone", "") or "").lower()]
        self._populate_customers(filtered)

    def _on_customer_selected(self, _):
        self._customer_id = self.cust_combo.currentData()

    # ─────────────────────────────────────────────────────
    def _confirm(self):
        p = self.product
        qty       = self.qty_spin.value()
        disc_pct  = self.discount_spin.value()
        unit_price = p.get("sale_price", 0) or 0
        subtotal  = unit_price * qty
        disc_amt  = subtotal * disc_pct / 100
        total     = subtotal - disc_amt
        paid      = self.paid_spin.value()
        remaining = max(0.0, total - paid)

        # Validate stock
        fresh = get_product_by_id(p["id"])
        if fresh and fresh["quantity"] < qty:
            QMessageBox.warning(self, "Insufficient Stock",
                f"Only {fresh['quantity']} units available.")
            return

        # Resolve customer
        customer_id   = None
        customer_name = "Walk-in"
        customer_phone   = ""
        customer_address = ""

        if self.tabs.currentIndex() == 0:
            customer_id = self.cust_combo.currentData()
            if customer_id:
                cust = next((c for c in self._customers if c["id"] == customer_id), None)
                if cust:
                    customer_name    = cust.get("name", "")
                    customer_phone   = cust.get("phone", "")
                    customer_address = cust.get("address", "")
        else:
            new_name = self.new_name.text().strip()
            if not new_name:
                QMessageBox.warning(self, "Validation", "New customer name is required.")
                return
            customer_id = insert_customer({
                "name":    new_name,
                "phone":   self.new_phone.text().strip(),
                "address": self.new_address.text().strip(),
                "notes":   self.new_notes.text().strip(),
            })
            customer_name    = new_name
            customer_phone   = self.new_phone.text().strip()
            customer_address = self.new_address.text().strip()

        inv_number = generate_invoice_number()
        sold_by    = session.user.get("username", "") if session.user else ""

        user_id = session.user.get("id") if session.user else None
        sale_data = {
            "invoice_number":  inv_number,
            "customer_id":     customer_id,
            "total_amount":    total,
            "discount":        disc_amt,
            "paid_amount":     paid,
            "remaining_amount": remaining,
            "payment_method":  self.payment_combo.currentText(),
            "notes":           "",
            "sold_by":         user_id,
        }
        items_data = [{
            "product_id": p["id"],
            "quantity":   qty,
            "unit_price": unit_price,
            "discount":   disc_amt,
            "subtotal":   subtotal - disc_amt,
        }]

        try:
            sale_id = insert_sale(sale_data, items_data)
            deduct_stock(p["id"], qty)
            if paid > 0:
                record_sale_payment(
                    sale_id,
                    paid,
                    self.payment_combo.currentText(),
                    notes="Initial payment at sale",
                    recorded_by=user_id,
                )

            # Generate PDF invoice
            inv_sale = {
                "id":              sale_id,
                **sale_data,
                "discount_amount":  disc_amt,
                "customer_name":    customer_name,
                "customer_phone":   customer_phone,
                "customer_address": customer_address,
                "sale_date":        "",
                "sold_by":          sold_by,
            }
            inv_items = [{
                "name":         p.get("name", ""),
                "quantity":     qty,
                "unit_price":   unit_price,
                "discount_pct": disc_pct,
                "subtotal":     subtotal - disc_amt,
            }]
            pdf_path = generate_invoice(inv_sale, inv_items)

            QMessageBox.information(
                self, "Sale Complete",
                f"✅  Sale recorded successfully!\n\n"
                f"Invoice: {inv_number}\n"
                f"Total: {format_currency(total)}\n"
                f"Remaining: {format_currency(remaining)}\n\n"
                f"PDF saved to:\n{pdf_path}"
            )

            # Open PDF
            try:
                os.startfile(pdf_path)
            except Exception:
                pass

            self.sale_completed.emit()
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
