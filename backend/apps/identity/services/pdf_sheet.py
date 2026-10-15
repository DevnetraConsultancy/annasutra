"""AnnaSutra Printable A4 Sticker Sheet PDF Generator.
Generates multi-page A4 sticker sheets with vector layout and crisp QR codes
for peel-and-stick physical agricultural packaging application.
Conforms to Handover Section 9.
"""

import io
from typing import List, Optional

import qrcode
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

from apps.identity.services.entity_allocation import format_serial_display


def generate_qr_image_bytes(url: str) -> io.BytesIO:
    """Generate in-memory PNG bytes for a QR code."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=1,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#0B3D2E", back_color="#FFFFFF")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf


def render_a4_sticker_sheet(
    serials: List[str],
    entity_code: str,
    org_name: Optional[str] = None,
    domain: str = "annasutra.in",
) -> bytes:
    """Render an A4 PDF containing peel-and-stick labels for all serials.
    Layout: 4 columns x 6 rows = 24 labels per page.
    """
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    page_width, page_height = A4  # 595.27 x 841.89 points

    # Geometry: 4 cols x 6 rows = 24 labels per page
    cols = 4
    rows = 6
    labels_per_page = cols * rows

    margin_x = 8 * mm
    margin_y = 10 * mm

    grid_width = page_width - (2 * margin_x)
    grid_height = page_height - (2 * margin_y)

    cell_width = grid_width / cols
    cell_height = grid_height / rows

    # Pre-render QR images for efficiency
    qr_cache = {}
    for s in serials:
        url = f"https://{domain}/L/{s}"
        qr_cache[s] = generate_qr_image_bytes(url)

    total_labels = len(serials)
    num_pages = (total_labels + labels_per_page - 1) // labels_per_page if total_labels > 0 else 1

    for page_idx in range(num_pages):
        start_idx = page_idx * labels_per_page
        end_idx = min(start_idx + labels_per_page, total_labels)
        page_serials = serials[start_idx:end_idx]

        # Draw page header watermark / title
        p.setFont("Helvetica-Bold", 8)
        p.setFillColor(colors.HexColor("#0B3D2E"))
        p.drawString(margin_x, page_height - 7 * mm, f"AnnaSutra Produce Traceability — Sheet {page_idx + 1}/{num_pages} — Entity: {entity_code}")
        p.setFont("Helvetica", 7)
        p.setFillColor(colors.HexColor("#64748B"))
        p.drawRightString(page_width - margin_x, page_height - 7 * mm, "Standard A4 (4x6 Grid) — 13-Char Crockford Base32")

        for idx, serial in enumerate(page_serials):
            col = idx % cols
            row = idx // cols

            # Bottom-left of current cell
            x = margin_x + (col * cell_width)
            y = page_height - margin_y - ((row + 1) * cell_height)

            # Padding inside cell
            pad = 2.5 * mm
            box_x = x + pad
            box_y = y + pad
            box_w = cell_width - (2 * pad)
            box_h = cell_height - (2 * pad)

            # 1. Outer sticker boundary (light border with subtle corner curve)
            p.setStrokeColor(colors.HexColor("#CBD5E1"))
            p.setLineWidth(0.6)
            p.roundRect(box_x, box_y, box_w, box_h, 3, stroke=1, fill=0)

            # 2. Header banner inside sticker
            p.setFillColor(colors.HexColor("#0B3D2E"))
            p.rect(box_x, box_y + box_h - 4.5 * mm, box_w, 4.5 * mm, stroke=0, fill=1)

            # Brand name & emblem in banner
            p.setFillColor(colors.HexColor("#F5A623"))
            p.circle(box_x + 3 * mm, box_y + box_h - 2.25 * mm, 1.2 * mm, stroke=0, fill=1)
            p.setFont("Helvetica-Bold", 6.5)
            p.setFillColor(colors.white)
            p.drawString(box_x + 5.5 * mm, box_y + box_h - 3.2 * mm, "ANNASUTRA")

            p.setFont("Helvetica-Bold", 5.5)
            p.setFillColor(colors.HexColor("#FDE047"))
            p.drawRightString(box_x + box_w - 2 * mm, box_y + box_h - 3.2 * mm, entity_code)

            # 3. QR Code image
            qr_bytes = qr_cache.get(serial)
            if qr_bytes:
                qr_bytes.seek(0)
                qr_reader = ImageReader(qr_bytes)
                qr_size = min(box_w - 4 * mm, box_h - 13 * mm)
                qr_x = box_x + ((box_w - qr_size) / 2)
                qr_y = box_y + 6 * mm + ((box_h - 10.5 * mm - qr_size) / 2)
                p.drawImage(qr_reader, qr_x, qr_y, width=qr_size, height=qr_size)

            # 4. Human-readable serial code below QR
            display_serial = format_serial_display(serial)
            p.setFont("Courier-Bold", 6.8)
            p.setFillColor(colors.HexColor("#0F172A"))
            p.drawCentredString(box_x + (box_w / 2), box_y + 4.2 * mm, display_serial)

            # 5. Bottom micro-caption
            p.setFont("Helvetica", 4.5)
            p.setFillColor(colors.HexColor("#64748B"))
            p.drawCentredString(box_x + (box_w / 2), box_y + 1.8 * mm, "SCAN TO VERIFY ORIGIN & HARVEST")

        p.showPage()

    p.save()
    buffer.seek(0)
    return buffer.getvalue()
