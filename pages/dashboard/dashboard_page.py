from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame,
    QSizePolicy, QGraphicsDropShadowEffect, QScrollArea,
    QTableWidget, QTableWidgetItem, QHeaderView, QPushButton
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from datetime import datetime, timedelta

from models.product_model import get_all_products, get_low_stock_products
from models.sale_model import get_sales_summary, get_all_sales, get_weekly_sales, get_pending_sales
from models.customer_model import get_all_customers
from models.supplier_model import get_all_suppliers
from utils.helpers import format_currency, format_datetime

# ── Stat card definitions: (title, icon, accent_color, bg_gradient)
_CARDS = [
    ("Total Products",    "📦", "#3b82f6", "#eff6ff", "#dbeafe"),
    ("Total Customers",   "👥", "#10b981", "#f0fdf4", "#d1fae5"),
    ("Total Suppliers",   "🚚", "#8b5cf6", "#f5f3ff", "#ede9fe"),
    ("Total Revenue",     "💰", "#f59e0b", "#fffbeb", "#fef3c7"),
    ("Pending Payments",  "⏳", "#ef4444", "#fef2f2", "#fee2e2"),
    ("Low Stock Items",   "⚠",  "#f97316", "#fff7ed", "#ffedd5"),
]


class DashboardPage(QWidget):

    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("background-color: #f1f5f9;")
        self._build_ui()

    # ──────────────────────────────────────────────────────
    def _build_ui(self):
        stats = self._load_stats()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: #f1f5f9; border:none;")

        content = QWidget()
        content.setStyleSheet("background: #f1f5f9;")
        root = QVBoxLayout(content)
        root.setContentsMargins(28, 24, 28, 28)
        root.setSpacing(24)

        # ── Header
        header = QHBoxLayout()
        page_title = QLabel("Dashboard")
        page_title.setStyleSheet("font-size:26px; font-weight:700; color:#0f172a;")
        refresh_btn = QPushButton("↻  Refresh")
        refresh_btn.setFixedSize(110, 36)
        refresh_btn.setStyleSheet("""
            QPushButton { background:#2e7d32; color:white; border-radius:8px;
                          font-size:13px; font-weight:600; border:none; }
            QPushButton:hover { background:#1b5e20; }
        """)
        refresh_btn.clicked.connect(self._refresh)
        header.addWidget(page_title)
        header.addStretch()
        header.addWidget(refresh_btn)
        root.addLayout(header)

        # ── Low-stock banner
        low_stock_items = get_low_stock_products()
        if low_stock_items:
            banner = QFrame()
            banner.setStyleSheet("""
                QFrame { background:#fef3c7; border:1.5px solid #f59e0b;
                         border-radius:10px; padding:4px; }
            """)
            b_layout = QHBoxLayout(banner)
            b_layout.setContentsMargins(14, 8, 14, 8)
            icon = QLabel("⚠")
            icon.setStyleSheet("font-size:18px;")
            msg = QLabel(
                f"<b>{len(low_stock_items)} product(s)</b> are low on stock: "
                + ", ".join(p["name"] for p in low_stock_items[:5])
                + ("…" if len(low_stock_items) > 5 else "")
            )
            msg.setStyleSheet("font-size:13px; color:#92400e;")
            b_layout.addWidget(icon)
            b_layout.addWidget(msg)
            b_layout.addStretch()
            root.addWidget(banner)

        # ── Stat Cards row
        self._card_widgets = {}
        cards_row = QHBoxLayout()
        cards_row.setSpacing(16)
        values = [
            str(stats["products"]),
            str(stats["customers"]),
            str(stats["suppliers"]),
            stats["revenue"],
            stats["pending"],
            str(stats["low_stock"]),
        ]
        for (title, icon, accent, bg1, bg2), value in zip(_CARDS, values):
            cards_row.addWidget(self._make_stat_card(title, icon, value, accent, bg1, bg2))
        root.addLayout(cards_row)

        # ── Charts row
        charts_row = QHBoxLayout()
        charts_row.setSpacing(20)
        charts_row.addWidget(self._make_weekly_sales_chart(), stretch=3)
        charts_row.addWidget(self._make_inventory_pie_chart(), stretch=2)
        root.addLayout(charts_row)

        # ── Bottom section: Recent Sales + Low Stock table + Pending
        bottom = QHBoxLayout()
        bottom.setSpacing(20)
        bottom.addWidget(self._make_recent_sales_panel(), stretch=3)
        bottom.addWidget(self._make_low_stock_panel(low_stock_items), stretch=2)
        root.addLayout(bottom)

        # ── Pending payments panel
        root.addWidget(self._make_pending_payments_panel())

        root.addStretch()
        scroll.setWidget(content)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    # ──────────────────────────────────────────────────────
    def _make_stat_card(self, title, icon, value, accent, bg1, bg2) -> QFrame:
        card = QFrame()
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        card.setFixedHeight(110)
        card.setAttribute(Qt.WA_StyledBackground, True)
        card.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 {bg1}, stop:1 {bg2});
                border-radius: 14px;
                border: 1.5px solid {accent}33;
            }}
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(16)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 35))
        card.setGraphicsEffect(shadow)

        layout = QHBoxLayout(card)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(14)

        icon_lbl = QLabel(icon)
        icon_lbl.setFixedSize(48, 48)
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setStyleSheet(f"""
            background:{accent}22; border-radius:12px;
            font-size:22px;
        """)

        text_col = QVBoxLayout()
        text_col.setSpacing(2)
        val_lbl = QLabel(value)
        val_lbl.setStyleSheet(f"font-size:24px; font-weight:800; color:{accent};")
        ttl_lbl = QLabel(title)
        ttl_lbl.setStyleSheet("font-size:12px; color:#64748b; font-weight:500;")
        text_col.addWidget(val_lbl)
        text_col.addWidget(ttl_lbl)

        layout.addWidget(icon_lbl)
        layout.addLayout(text_col)
        layout.addStretch()
        return card

    # ──────────────────────────────────────────────────────
    def _make_recent_sales_panel(self) -> QFrame:
        panel = QFrame()
        panel.setAttribute(Qt.WA_StyledBackground, True)
        panel.setStyleSheet("""
            QFrame { background:white; border-radius:14px;
                     border:1px solid #e2e8f0; }
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(16)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 25))
        panel.setGraphicsEffect(shadow)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(12)

        hdr = QHBoxLayout()
        title = QLabel("🛒  Recent Sales")
        title.setStyleSheet("font-size:15px; font-weight:700; color:#0f172a;")
        hdr.addWidget(title)
        hdr.addStretch()
        layout.addLayout(hdr)

        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["Invoice", "Customer", "Amount", "Paid", "Date"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setAlternatingRowColors(True)
        table.setShowGrid(False)
        table.setStyleSheet("""
            QTableWidget { border:none; font-size:13px; background:white;
                           alternate-background-color:#f8fafc; }
            QHeaderView::section { background:#f1f5f9; color:#475569;
                font-weight:600; padding:8px; border:none; font-size:12px; }
            QTableWidget::item { padding:8px; color:#1e293b; }
            QTableWidget::item:selected { background:#dbeafe; color:#1e40af; }
        """)

        sales = get_all_sales()[:8]
        table.setRowCount(len(sales))
        for r, s in enumerate(sales):
            table.setItem(r, 0, QTableWidgetItem(s.get("invoice_number", "")))
            table.setItem(r, 1, QTableWidgetItem(s.get("customer_name") or "Walk-in"))
            table.setItem(r, 2, QTableWidgetItem(format_currency(s.get("total_amount", 0))))
            table.setItem(r, 3, QTableWidgetItem(format_currency(s.get("paid_amount", 0))))
            table.setItem(r, 4, QTableWidgetItem(format_datetime(s.get("sale_date", ""))))

        layout.addWidget(table)
        return panel

    # ──────────────────────────────────────────────────────
    def _make_low_stock_panel(self, items: list) -> QFrame:
        panel = QFrame()
        panel.setAttribute(Qt.WA_StyledBackground, True)
        panel.setStyleSheet("""
            QFrame { background:white; border-radius:14px;
                     border:1px solid #e2e8f0; }
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(16)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 25))
        panel.setGraphicsEffect(shadow)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(12)

        title = QLabel("⚠  Low Stock Alerts")
        title.setStyleSheet("font-size:15px; font-weight:700; color:#0f172a;")
        layout.addWidget(title)

        if not items:
            ok = QLabel("✅  All products are well stocked!")
            ok.setStyleSheet("color:#10b981; font-size:13px; padding:12px 0;")
            ok.setAlignment(Qt.AlignCenter)
            layout.addWidget(ok)
        else:
            table = QTableWidget()
            table.setColumnCount(3)
            table.setHorizontalHeaderLabels(["Product", "Qty", "Min"])
            table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            table.verticalHeader().setVisible(False)
            table.setEditTriggers(QTableWidget.NoEditTriggers)
            table.setShowGrid(False)
            table.setAlternatingRowColors(True)
            table.setStyleSheet("""
                QTableWidget { border:none; font-size:13px; background:white;
                               alternate-background-color:#fff7ed; }
                QHeaderView::section { background:#fff7ed; color:#92400e;
                    font-weight:600; padding:8px; border:none; font-size:12px; }
                QTableWidget::item { padding:8px; color:#1e293b; }
            """)
            table.setRowCount(len(items))
            for r, p in enumerate(items):
                qty = p.get("quantity", 0)
                threshold = p.get("low_stock_threshold", 5)
                name_item = QTableWidgetItem(p.get("name", ""))
                qty_item  = QTableWidgetItem(str(qty))
                min_item  = QTableWidgetItem(str(threshold))
                if qty == 0:
                    qty_item.setForeground(QColor("#ef4444"))
                else:
                    qty_item.setForeground(QColor("#f97316"))
                table.setItem(r, 0, name_item)
                table.setItem(r, 1, qty_item)
                table.setItem(r, 2, min_item)
            layout.addWidget(table)

        layout.addStretch()
        return panel

    # ──────────────────────────────────────────────────────
    def _chart_panel(self, title: str) -> tuple:
        """Create a white card panel, return (panel, inner_layout)."""
        panel = QFrame()
        panel.setAttribute(Qt.WA_StyledBackground, True)
        panel.setStyleSheet("QFrame{background:white;border-radius:14px;border:1px solid #e2e8f0;}")
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(14)
        shadow.setOffset(0, 3)
        shadow.setColor(QColor(0, 0, 0, 22))
        panel.setGraphicsEffect(shadow)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(10)
        lbl = QLabel(title)
        lbl.setStyleSheet("font-size:15px;font-weight:700;color:#0f172a;")
        layout.addWidget(lbl)
        return panel, layout

    def _make_weekly_sales_chart(self) -> QFrame:
        panel, layout = self._chart_panel("📊  Weekly Sales (Last 7 Days)")

        # Build date labels for last 7 days
        today = datetime.now().date()
        days  = [(today - timedelta(days=6 - i)) for i in range(7)]
        day_strs = {str(d): d.strftime("%a") for d in days}

        raw = {r["day"]: r["total"] for r in get_weekly_sales()}
        values = [raw.get(str(d), 0) for d in days]
        labels = [day_strs[str(d)] for d in days]

        fig, ax = plt.subplots(figsize=(5, 2.6))
        fig.patch.set_facecolor("white")
        ax.set_facecolor("#f8fafc")
        colors = ["#2e7d32" if v == max(values) else "#86efac" for v in values]
        bars = ax.bar(labels, values, color=colors, width=0.55, zorder=3)
        ax.set_ylabel("Rs", fontsize=9, color="#64748b")
        ax.tick_params(colors="#64748b", labelsize=9)
        ax.spines[["top", "right", "left"]].set_visible(False)
        ax.yaxis.grid(True, color="#e2e8f0", linewidth=0.8, zorder=0)
        ax.set_axisbelow(True)
        for bar, val in zip(bars, values):
            if val > 0:
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + max(values) * 0.01,
                        f"{val:,.0f}", ha="center", va="bottom", fontsize=8, color="#0f172a")
        fig.tight_layout()

        canvas = FigureCanvas(fig)
        canvas.setFixedHeight(220)
        layout.addWidget(canvas)
        plt.close(fig)
        return panel

    def _make_inventory_pie_chart(self) -> QFrame:
        panel, layout = self._chart_panel("🥧  Inventory Status")

        products  = get_all_products()
        in_stock  = sum(1 for p in products if p.get("quantity", 0) > p.get("low_stock_threshold", 5))
        low_stock = sum(1 for p in products if 0 < p.get("quantity", 0) <= p.get("low_stock_threshold", 5))
        out_stock = sum(1 for p in products if p.get("quantity", 0) == 0)

        sizes  = [in_stock, low_stock, out_stock]
        labels = ["In Stock", "Low Stock", "Out of Stock"]
        colors = ["#4ade80", "#fbbf24", "#f87171"]
        sizes  = [s for s, l in zip(sizes, labels) if s > 0]
        colors = [c for c, s in zip(colors, [in_stock, low_stock, out_stock]) if s > 0]
        labels = [l for l, s in zip(labels, [in_stock, low_stock, out_stock]) if s > 0]

        fig, ax = plt.subplots(figsize=(3.5, 2.6))
        fig.patch.set_facecolor("white")
        if sizes:
            wedges, texts, autotexts = ax.pie(
                sizes, labels=labels, colors=colors,
                autopct="%1.0f%%", startangle=140,
                wedgeprops=dict(edgecolor="white", linewidth=2),
                textprops={"fontsize": 9, "color": "#0f172a"},
            )
            for at in autotexts:
                at.set_fontsize(9)
                at.set_color("white")
                at.set_fontweight("bold")
        else:
            ax.text(0.5, 0.5, "No Data", ha="center", va="center", transform=ax.transAxes,
                    fontsize=12, color="#94a3b8")
            ax.axis("off")
        fig.tight_layout()

        canvas = FigureCanvas(fig)
        canvas.setFixedHeight(220)
        layout.addWidget(canvas)
        plt.close(fig)
        return panel

    def _make_pending_payments_panel(self) -> QFrame:
        panel = QFrame()
        panel.setAttribute(Qt.WA_StyledBackground, True)
        panel.setStyleSheet("QFrame{background:white;border-radius:14px;border:1px solid #e2e8f0;}")
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(14)
        shadow.setOffset(0, 3)
        shadow.setColor(QColor(0, 0, 0, 22))
        panel.setGraphicsEffect(shadow)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(10)

        title = QLabel("⏳  Pending Payments")
        title.setStyleSheet("font-size:15px;font-weight:700;color:#0f172a;")
        layout.addWidget(title)

        pending = get_pending_sales()
        if not pending:
            ok = QLabel("✅  No pending payments!")
            ok.setStyleSheet("color:#10b981;font-size:13px;padding:8px 0;")
            ok.setAlignment(Qt.AlignCenter)
            layout.addWidget(ok)
        else:
            table = QTableWidget()
            table.setColumnCount(4)
            table.setHorizontalHeaderLabels(["Invoice", "Customer", "Remaining", "Date"])
            table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            table.verticalHeader().setVisible(False)
            table.setEditTriggers(QTableWidget.NoEditTriggers)
            table.setShowGrid(False)
            table.setAlternatingRowColors(True)
            table.setFixedHeight(min(len(pending) * 42 + 44, 220))
            table.setStyleSheet("""
                QTableWidget{border:none;font-size:13px;background:white;
                             alternate-background-color:#fef2f2;}
                QHeaderView::section{background:#fef2f2;color:#dc2626;
                    font-weight:600;padding:8px;border:none;font-size:12px;}
                QTableWidget::item{padding:8px;color:#1e293b;}
                QTableWidget::item:selected{background:#fee2e2;color:#991b1b;}
            """)
            table.setRowCount(len(pending))
            for r, row in enumerate(pending):
                table.setItem(r, 0, QTableWidgetItem(row.get("invoice_number", "")))
                table.setItem(r, 1, QTableWidgetItem(row.get("customer_name") or "Walk-in"))
                amt = QTableWidgetItem(format_currency(row.get("remaining_amount", 0)))
                amt.setForeground(QColor("#dc2626"))
                table.setItem(r, 2, amt)
                table.setItem(r, 3, QTableWidgetItem(format_datetime(row.get("sale_date", ""))))
            layout.addWidget(table)
        return panel

    # ──────────────────────────────────────────────────────
    def _load_stats(self) -> dict:
        try:
            products  = get_all_products()
            customers = get_all_customers()
            suppliers = get_all_suppliers()
            low_stock = get_low_stock_products()
            summary   = get_sales_summary()
        except Exception:
            return {"products": 0, "customers": 0, "suppliers": 0,
                    "revenue": "Rs 0", "pending": "Rs 0", "low_stock": 0}
        return {
            "products":  len(products),
            "customers": len(customers),
            "suppliers": len(suppliers),
            "revenue":   format_currency(summary.get("total_revenue", 0)),
            "pending":   format_currency(summary.get("total_pending", 0)),
            "low_stock": len(low_stock),
        }

    def _refresh(self):
        layout = self.layout()
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._build_ui()
