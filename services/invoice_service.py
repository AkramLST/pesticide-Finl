import os
from typing import Optional
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Spacer, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT

from utils.config import INVOICES_DIR as INVOICE_DIR, APP_NAME
from models.settings_model import get_setting
from models.payment_model import get_sale_payments

W, H = A4


def generate_invoice(sale: dict, items: list, payments: Optional[list] = None) -> str:
    """
    Generate a PDF invoice and save to exports/invoices/.
    Returns the full file path.

    sale  = { invoice_number, customer_name, customer_phone, customer_address,
              total_amount, discount_amount, paid_amount, remaining_amount,
              payment_method, sale_date, sold_by }
    items = [ { name, quantity, unit_price, discount_pct, subtotal }, ... ]
    """
    os.makedirs(INVOICE_DIR, exist_ok=True)
    inv_no   = sale.get("invoice_number", "INV-0000")
    filename = os.path.join(INVOICE_DIR, f"{inv_no}.pdf")

    shop_name    = get_setting("shop_name")    or APP_NAME
    shop_address = get_setting("shop_address") or ""
    shop_phone   = get_setting("shop_phone")   or ""
    inv_footer   = get_setting("invoice_footer") or "Thank you for your business!"

    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
    )

    styles = getSampleStyleSheet()
    h1 = ParagraphStyle("h1", parent=styles["Normal"],
                        fontSize=20, fontName="Helvetica-Bold",
                        textColor=colors.HexColor("#1b5e20"),
                        alignment=TA_CENTER, spaceAfter=2)
    sub = ParagraphStyle("sub", parent=styles["Normal"],
                         fontSize=9, textColor=colors.HexColor("#475569"),
                         alignment=TA_CENTER, spaceAfter=1)
    label_s = ParagraphStyle("lbl", parent=styles["Normal"],
                              fontSize=10, fontName="Helvetica-Bold",
                              textColor=colors.HexColor("#0f172a"))
    val_s = ParagraphStyle("val", parent=styles["Normal"],
                            fontSize=10, textColor=colors.HexColor("#334155"))
    right_s = ParagraphStyle("rgt", parent=styles["Normal"],
                              fontSize=10, alignment=TA_RIGHT,
                              textColor=colors.HexColor("#334155"))
    footer_s = ParagraphStyle("ftr", parent=styles["Normal"],
                               fontSize=9, alignment=TA_CENTER,
                               textColor=colors.HexColor("#64748b"))

    story = []

    # ── Header
    story.append(Paragraph(shop_name, h1))
    if shop_address:
        story.append(Paragraph(shop_address, sub))
    if shop_phone:
        story.append(Paragraph(f"Phone: {shop_phone}", sub))
    story.append(Spacer(1, 0.3 * cm))
    story.append(HRFlowable(width="100%", thickness=2,
                             color=colors.HexColor("#2e7d32"), spaceAfter=8))

    # ── Invoice meta
    sale_date = sale.get("sale_date", datetime.now().strftime("%Y-%m-%d %H:%M"))
    meta_data = [
        [Paragraph("<b>Invoice #:</b>", label_s), Paragraph(inv_no, val_s),
         Paragraph(f"<b>Date:</b>", label_s),     Paragraph(str(sale_date), val_s)],
        [Paragraph("<b>Sold By:</b>", label_s),   Paragraph(sale.get("sold_by", ""), val_s),
         Paragraph("<b>Payment:</b>", label_s),   Paragraph(sale.get("payment_method", ""), val_s)],
    ]
    meta_tbl = Table(meta_data, colWidths=[3 * cm, 6 * cm, 3 * cm, 5 * cm])
    meta_tbl.setStyle(TableStyle([
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING",    (0, 0), (-1, -1), 3),
    ]))
    story.append(meta_tbl)
    story.append(Spacer(1, 0.3 * cm))

    # ── Customer info
    cust = sale.get("customer_name") or "Walk-in"
    cust_phone = sale.get("customer_phone", "") or ""
    cust_addr  = sale.get("customer_address", "") or ""
    cust_info = f"<b>Customer:</b>  {cust}"
    if cust_phone:
        cust_info += f"   |   <b>Phone:</b>  {cust_phone}"
    if cust_addr:
        cust_info += f"   |   <b>Address:</b>  {cust_addr}"
    story.append(Paragraph(cust_info, val_s))
    story.append(Spacer(1, 0.4 * cm))
    story.append(HRFlowable(width="100%", thickness=0.5,
                             color=colors.HexColor("#e2e8f0"), spaceAfter=8))

    # ── Items table
    thead = ["#", "Product", "Qty", "Unit Price", "Disc %", "Subtotal"]
    trows = [thead]
    for i, item in enumerate(items, 1):
        trows.append([
            str(i),
            item.get("name", ""),
            str(item.get("quantity", 0)),
            f"Rs {item.get('unit_price', 0):,.0f}",
            f"{item.get('discount_pct', 0):.0f}%",
            f"Rs {item.get('subtotal', 0):,.0f}",
        ])

    col_w = [1 * cm, 7.5 * cm, 1.5 * cm, 3 * cm, 2 * cm, 3 * cm]
    items_tbl = Table(trows, colWidths=col_w, repeatRows=1)
    items_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0),  colors.HexColor("#2e7d32")),
        ("TEXTCOLOR",     (0, 0), (-1, 0),  colors.white),
        ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, 0),  10),
        ("ALIGN",         (0, 0), (-1, -1), "LEFT"),
        ("ALIGN",         (2, 1), (-1, -1), "RIGHT"),
        ("FONTSIZE",      (0, 1), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ("GRID",          (0, 0), (-1, -1), 0.4, colors.HexColor("#e2e8f0")),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
    ]))
    story.append(items_tbl)
    story.append(Spacer(1, 0.5 * cm))

    # ── Totals
    total   = sale.get("total_amount", 0)
    disc    = sale.get("discount_amount", 0)
    paid    = sale.get("paid_amount", 0)
    remain  = sale.get("remaining_amount", 0)

    totals = [
        ["", "Subtotal:", f"Rs {(total + disc):,.0f}"],
        ["", "Discount:", f"- Rs {disc:,.0f}"],
        ["", "Grand Total:", f"Rs {total:,.0f}"],
        ["", "Amount Paid:", f"Rs {paid:,.0f}"],
        ["", "Remaining:", f"Rs {remain:,.0f}"],
    ]
    tot_tbl = Table(totals, colWidths=[10.5 * cm, 4 * cm, 3.5 * cm])
    tot_tbl.setStyle(TableStyle([
        ("ALIGN",         (1, 0), (2, -1), "RIGHT"),
        ("FONTSIZE",      (0, 0), (-1, -1), 10),
        ("FONTNAME",      (1, 2), (2, 2),  "Helvetica-Bold"),
        ("FONTNAME",      (1, 4), (2, 4),  "Helvetica-Bold"),
        ("TEXTCOLOR",     (2, 4), (2, 4),
         colors.HexColor("#dc2626") if remain > 0 else colors.HexColor("#16a34a")),
        ("LINEABOVE",     (1, 2), (2, 2),  1, colors.HexColor("#2e7d32")),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(tot_tbl)
    story.append(Spacer(1, 0.6 * cm))

    payments = payments if payments is not None else get_sale_payments(
        sale.get("id") or sale.get("sale_id") or 0
    )
    if payments:
        story.append(Paragraph("Payment History", ParagraphStyle(
            "payh", parent=styles["Normal"], fontSize=11,
            fontName="Helvetica-Bold", textColor=colors.HexColor("#0f172a"),
            spaceAfter=6
        )))
        pay_rows = [["Date", "Amount", "Remaining", "Method", "Notes"]]
        for pay in payments:
            pay_rows.append([
                str(pay.get("payment_date", "")),
                f"Rs {float(pay.get('amount_paid', 0) or 0):,.0f}",
                f"Rs {float(pay.get('remaining_balance', 0) or 0):,.0f}",
                pay.get("payment_method", "") or "—",
                pay.get("notes", "") or "",
            ])
        pay_tbl = Table(pay_rows, colWidths=[4 * cm, 3 * cm, 3 * cm, 3 * cm, 4 * cm], repeatRows=1)
        pay_tbl.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
            ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#e2e8f0")),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(pay_tbl)
        story.append(Spacer(1, 0.4 * cm))

    story.append(HRFlowable(width="100%", thickness=0.5,
                             color=colors.HexColor("#e2e8f0"), spaceAfter=6))
    story.append(Paragraph(inv_footer, footer_s))

    doc.build(story)
    return filename
