from http.server import BaseHTTPRequestHandler
import json
import os
from fpdf import FPDF

# Vercel'de file system erişimi için path'leri ayarla
template_path = os.path.join(os.path.dirname(__file__), 'new_template.jpg')
if not os.path.exists(template_path):
    # Fallback to parent directory for local dev
    template_path = os.path.join(os.path.dirname(__file__), '..', 'new_template.jpg')

class PDF(FPDF):
    def header(self):
        # Template image'ı ekle
        if os.path.exists(template_path):
            self.image(template_path, x=0, y=0, w=210, h=297)
        else:
            # Template yoksa beyaz background
            self.set_fill_color(255, 255, 255)
            self.rect(0, 0, 210, 297, 'F')

    def add_invoice(self, data):
        self.set_y(45)
        self.set_font("Arial", "B", 16)
        self.set_text_color(0, 51, 102)
        self.cell(0, 20, data["title"], ln=True, align="C")

        self.set_font("Arial", "", 11)
        self.set_text_color(0)

        self.set_y(65)
        self.set_x(10)
        self.set_draw_color(180)
        self.set_line_width(0.2)
        self.multi_cell(90, 5.5, f"Billed By:\n{data['billed_by']}", border=1)

        self.set_y(65)
        self.set_x(110)
        self.multi_cell(90, 5.5, f"Billed To:\n{data['billed_to']}", border=1)

        self.set_y(85)
        self.set_x(10)
        
        # Invoice number - generate basit bir unique number
        invoice_no = data.get('invoice_no', f"A{int(os.urandom(4).hex(), 16) % 1000000:06d}")
        
        self.cell(90, 8, f"Invoice No: {invoice_no}", ln=0)
        self.set_x(110)
        self.cell(90, 8, f"Invoice Date: {data['invoice_date']}", ln=1)

        self.set_y(102)
        self.set_x(10)
        self.set_fill_color(225, 236, 247)
        self.set_text_color(0, 51, 102)
        self.set_font("Arial", "B", 12)

        headers = ["Item"]
        if data.get("show_quantity", True):
            headers.append("Quantity")
        if data.get("show_rate", False):
            headers.append("Rate")
        if data.get("show_amount", True):
            headers.append("Amount")

        col_widths = [80]
        if data.get("show_quantity", True):
            col_widths.append(30)
        if data.get("show_rate", False):
            col_widths.append(40)
        if data.get("show_amount", True):
            col_widths.append(40)

        for header, width in zip(headers, col_widths):
            self.cell(width, 9, header, 1, 0, "C", True)
        self.ln()

        self.set_font("Arial", "", 11)
        self.set_text_color(0)
        total = 0.0
        for item in data.get("items", []):
            item_name = item.get("item", "")
            quantity = item.get("quantity", 1)
            rate = item.get("rate", 0)
            amount = quantity * rate
            note = item.get("note", None)

            self.set_x(10)
            self.cell(col_widths[0], 9, item_name, 1)

            col_idx = 1
            if data.get("show_quantity", True):
                self.cell(col_widths[col_idx], 9, str(quantity), 1, 0, "R")
                col_idx += 1
            if data.get("show_rate", False):
                self.cell(col_widths[col_idx], 9, f"{data.get('currency', '£')}{rate:,.2f}", 1, 0, "R")
                col_idx += 1
            if data.get("show_amount", True):
                self.cell(col_widths[col_idx], 9, f"{data.get('currency', '£')}{amount:,.2f}", 1, 0, "R")
            total += amount
            self.ln()

            if note:
                self.set_x(12)
                self.set_font("Arial", "I", 10)
                self.set_text_color(90)
                self.multi_cell(sum(col_widths), 6, note)
                self.set_font("Arial", "", 11)
                self.set_text_color(0)

        self.set_font("Arial", "B", 12)
        self.set_x(10)
        self.cell(sum(col_widths[:-1]), 10, "Total", 1)
        self.cell(col_widths[-1], 10, f"{data.get('currency', '£')}{total:,.2f}", 1, 1, "R")

        deposit = data.get("deposit", 0.0)
        remaining = total - deposit

        self.set_font("Arial", "", 11)
        self.set_x(10)
        self.cell(sum(col_widths[:-1]), 10, "Deposit", 1)
        self.cell(col_widths[-1], 10, f"{data.get('currency', '£')}{deposit:,.2f}", 1, 1, "R")

        self.set_font("Arial", "B", 12)
        self.set_x(10)
        self.cell(sum(col_widths[:-1]), 10, "Remaining", 1)
        self.cell(col_widths[-1], 10, f"{data.get('currency', '£')}{remaining:,.2f}", 1, 1, "R")

        if data.get("cash_note"):
            self.set_font("Arial", "I", 10)
            self.set_text_color(120)
            self.set_y(self.get_y() + 3)
            self.set_x(10)
            self.cell(0, 10, data["cash_note"], ln=True)
            self.set_text_color(0)

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            # PDF oluştur
            pdf = PDF()
            pdf.add_page()
            pdf.add_invoice(data)

            # PDF'i base64 olarak encode et
            pdf_output = pdf.output(dest='S').encode('latin-1')
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/pdf')
            self.send_header('Content-Disposition', 'attachment; filename="invoice.pdf"')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(pdf_output)

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            error_response = json.dumps({'error': str(e)})
            self.wfile.write(error_response.encode('utf-8'))

