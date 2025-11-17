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
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        # Unicode desteği için DejaVu fontunu kullan
        dejavu_path = os.path.join(os.path.dirname(__file__), 'DejaVuSans.ttf')
        if os.path.exists(dejavu_path):
            try:
                self.add_font('DejaVu', '', dejavu_path, uni=True)
                self.add_font('DejaVu', 'B', dejavu_path, uni=True)
                self.add_font('DejaVu', 'I', dejavu_path, uni=True)
                self.unicode_font = 'DejaVu'
            except:
                self.unicode_font = 'helvetica'
        else:
            self.unicode_font = 'helvetica'
    
    def _safe_text(self, text):
        """Türkçe karakterleri güvenli şekilde işle - Unicode desteği"""
        if text is None:
            return ""
        return str(text)
    
    def _set_font(self, style='', size=12):
        """Unicode font kullanarak font ayarla"""
        if self.unicode_font == 'DejaVu':
            self.set_font('DejaVu', style, size)
        else:
            self.set_font('helvetica', style, size)
    
    def header(self):
        # Template image'ı ekle
        if os.path.exists(template_path):
            self.image(template_path, x=0, y=0, w=210, h=297)
        else:
            # Template yoksa beyaz background
            self.set_fill_color(255, 255, 255)
            self.rect(0, 0, 210, 297, 'F')

    def add_invoice(self, data):
        # Header section - Logo ve başlık
        self.set_y(20)
        
        # Logo alanı (sol üst)
        self.set_x(15)
        self._set_font("B", 18)
        self.set_text_color(220, 20, 60)  # Kırmızı renk
        self.cell(40, 10, "You", ln=0)
        self._set_font("", 10)
        self.set_text_color(0)
        self.cell(0, 10, "Clinic", ln=1)
        
        self.set_x(15)
        self._set_font("", 8)
        self.set_text_color(100)
        self.cell(0, 5, "Specialized care management", ln=1)
        
        # PROFORMA INVOICE başlığı (sağ üst)
        self.set_y(20)
        self.set_x(120)
        self._set_font("B", 16)
        self.set_text_color(0)
        self.cell(0, 8, "PROFORMA INVOICE", ln=1, align="R")
        
        self.set_x(120)
        self._set_font("", 10)
        self.set_text_color(100)
        
        # Invoice number - generate basit bir unique number
        invoice_no = data.get('invoice_no', f"PRO-{int(os.urandom(4).hex(), 16) % 1000000:06d}")
        self.cell(0, 5, f"Invoice #: {invoice_no}", ln=1, align="R")
        
        self.set_x(120)
        self.cell(0, 5, f"Date: {data['invoice_date']}", ln=1, align="R")
        
        # Billed By ve Billed To bölümleri
        self.set_y(50)
        self.set_x(15)
        self._set_font("B", 10)
        self.set_text_color(0)
        self.cell(0, 6, "BILLED BY:", ln=1)
        
        self.set_x(15)
        self._set_font("", 9)
        self.set_text_color(50)
        # Billed By bilgilerini parse et
        billed_by_lines = self._safe_text(data['billed_by']).split('\n')
        for line in billed_by_lines[:6]:  # Max 6 satır
            if line.strip():
                self.cell(0, 4.5, line.strip(), ln=1)
        
        # Billed To (sağ taraf)
        self.set_y(50)
        self.set_x(120)
        self._set_font("B", 10)
        self.set_text_color(0)
        self.cell(0, 6, "BILLED TO:", ln=1, align="R")
        
        self.set_x(120)
        self._set_font("", 9)
        self.set_text_color(50)
        # Billed To bilgilerini parse et
        billed_to_lines = self._safe_text(data['billed_to']).split('\n')
        for line in billed_to_lines[:6]:  # Max 6 satır
            if line.strip():
                self.cell(0, 4.5, line.strip(), ln=1, align="R")
        
        # Items table
        self.set_y(110)
        self.set_x(15)
        self.set_fill_color(240, 240, 240)
        self.set_text_color(0)
        self._set_font("B", 10)
        
        headers = ["Item"]
        if data.get("show_quantity", True):
            headers.append("Quantity")
        if data.get("show_rate", False):
            headers.append("Rate")
        if data.get("show_amount", True):
            headers.append("Amount")

        col_widths = [100]
        if data.get("show_quantity", True):
            col_widths.append(25)
        if data.get("show_rate", False):
            col_widths.append(30)
        if data.get("show_amount", True):
            col_widths.append(35)

        # Header row
        for header, width in zip(headers, col_widths):
            self.cell(width, 8, header, 1, 0, "C", True)
        self.ln()

        # Items rows
        self._set_font("", 9)
        self.set_text_color(0)
        total = 0.0
        for item in data.get("items", []):
            item_name = self._safe_text(item.get("item", ""))
            quantity = item.get("quantity", 1)
            rate = item.get("rate", 0)
            amount = quantity * rate
            note = item.get("note", None)

            self.set_x(15)
            self.cell(col_widths[0], 8, item_name, 1)

            col_idx = 1
            if data.get("show_quantity", True):
                self.cell(col_widths[col_idx], 8, str(quantity), 1, 0, "C")
                col_idx += 1
            if data.get("show_rate", False):
                self.cell(col_widths[col_idx], 8, f"{data.get('currency', '£')}{rate:,.2f}", 1, 0, "R")
                col_idx += 1
            if data.get("show_amount", True):
                self.cell(col_widths[col_idx], 8, f"{data.get('currency', '£')}{amount:,.2f}", 1, 0, "R")
            total += amount
            self.ln()

            if note:
                self.set_x(17)
                self._set_font("I", 8)
                self.set_text_color(100)
                self.multi_cell(sum(col_widths) - 4, 5, self._safe_text(note))
                self._set_font("", 9)
                self.set_text_color(0)

        # Summary section
        summary_y = self.get_y() + 5
        self.set_y(summary_y)
        self.set_x(15)
        
        # Total, Deposit, Remaining
        summary_width = sum(col_widths)
        right_col = summary_width - 60
        
        self._set_font("B", 10)
        self.cell(60, 8, "Total:", 0, 0, "L")
        self.cell(right_col, 8, f"{data.get('currency', '£')}{total:,.2f}", 0, 1, "R")
        
        deposit = data.get("deposit", 0.0)
        remaining = total - deposit
        
        self._set_font("", 9)
        self.set_x(15)
        self.cell(60, 8, "Deposit:", 0, 0, "L")
        self.cell(right_col, 8, f"{data.get('currency', '£')}{deposit:,.2f}", 0, 1, "R")
        
        self._set_font("B", 10)
        self.set_x(15)
        self.cell(60, 8, "Remaining:", 0, 0, "L")
        self.cell(right_col, 8, f"{data.get('currency', '£')}{remaining:,.2f}", 0, 1, "R")

        # Cash note
        if data.get("cash_note"):
            self.set_y(self.get_y() + 5)
            self.set_x(15)
            self._set_font("I", 9)
            self.set_text_color(100)
            self.multi_cell(0, 5, self._safe_text(data["cash_note"]))
            self.set_text_color(0)
        
        # Footer
        self.set_y(280)
        self.set_x(15)
        self._set_font("", 8)
        self.set_text_color(150)
        self.cell(0, 4, "youstemcell.com  |  @youclinictr  |  Izmir, Turkey", ln=1, align="C")

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

            # PDF'i bytes olarak al
            pdf_output = pdf.output(dest='S')
            
            # Eğer string ise bytes'a çevir, değilse direkt kullan
            if isinstance(pdf_output, str):
                pdf_output = pdf_output.encode('latin-1')
            elif isinstance(pdf_output, bytearray):
                pdf_output = bytes(pdf_output)
            
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
