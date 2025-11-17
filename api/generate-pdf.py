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
    
    def _safe_text(self, text):
        """Türkçe karakterleri ve özel sembolleri İngilizce karakterlere çevir"""
        if text is None:
            return ""
        
        text = str(text)
        
        # Türkçe karakter mapping
        turkish_to_english = {
            'ı': 'i', 'İ': 'I',
            'ş': 's', 'Ş': 'S',
            'ğ': 'g', 'Ğ': 'G',
            'ü': 'u', 'Ü': 'U',
            'ö': 'o', 'Ö': 'O',
            'ç': 'c', 'Ç': 'C'
        }
        
        # Özel sembol mapping
        symbol_mapping = {
            '€': 'EUR',
            '£': 'GBP',
            '$': 'USD',
            '¥': 'JPY'
        }
        
        # Karakterleri çevir
        result = ""
        for char in text:
            if char in turkish_to_english:
                result += turkish_to_english[char]
            elif char in symbol_mapping:
                result += symbol_mapping[char]
            else:
                result += char
        
        return result
    
    def _format_currency(self, currency, amount):
        """Para birimi formatla - sembolden sonra boşluk ekle"""
        currency_text = self._safe_text(currency)
        return f"{currency_text} {amount:,.2f}"
    
    def header(self):
        # Template image'ı ekle
        if os.path.exists(template_path):
            self.image(template_path, x=0, y=0, w=210, h=297)
        else:
            # Template yoksa beyaz background
            self.set_fill_color(255, 255, 255)
            self.rect(0, 0, 210, 297, 'F')

    def add_invoice(self, data):
        # Invoice bilgileri - SAĞ ÜSTTE (örnekteki gibi)
        invoice_no = data.get('invoice_no', f"PRO-{int(os.urandom(4).hex(), 16) % 1000000:06d}")
        
        self.set_y(20)
        self.set_x(120)
        self.set_font("helvetica", "B", 16)
        self.set_text_color(0)
        self.cell(0, 8, "PROFORMA INVOICE", ln=1, align="R")
        
        self.set_x(120)
        self.set_font("helvetica", "", 10)
        self.set_text_color(100)
        self.cell(0, 5, f"Invoice #: {invoice_no}", ln=1, align="R")
        
        self.set_x(120)
        self.cell(0, 5, f"Date: {data['invoice_date']}", ln=1, align="R")
        
        # Billed By ve Billed To bölümleri - KUTUSUZ, sadece yazı (örnekteki gibi)
        self.set_y(50)
        self.set_x(10)
        self.set_draw_color(180)
        self.set_line_width(0.2)
        
        # Billed By (sol) - kutusuz
        self.set_font("helvetica", "B", 10)
        self.set_text_color(0)
        self.multi_cell(90, 5.5, f"Billed By:\n{self._safe_text(data['billed_by'])}", border=1)
        
        # Billed To (sağ) - kutusuz
        self.set_y(50)
        self.set_x(110)
        self.multi_cell(90, 5.5, f"Billed To:\n{self._safe_text(data['billed_to'])}", border=1)
        
        # Items table - SADECE Item ve Amount (örnekteki gibi)
        self.set_y(102)
        self.set_x(10)
        self.set_fill_color(225, 236, 247)
        self.set_text_color(0, 51, 102)
        self.set_font("helvetica", "B", 12)
        
        # Sadece Item ve Amount sütunları
        headers = ["Item", "Amount"]
        col_widths = [140, 50]  # Item geniş, Amount dar

        # Header row
        for header, width in zip(headers, col_widths):
            self.cell(width, 9, header, 1, 0, "C", True)
        self.ln()

        # Items rows
        self.set_font("helvetica", "", 11)
        self.set_text_color(0)
        total = 0.0
        currency = self._safe_text(data.get('currency', '£'))
        
        for item in data.get("items", []):
            item_name = self._safe_text(item.get("item", ""))
            quantity = item.get("quantity", 1)
            rate = item.get("rate", 0)
            amount = quantity * rate
            note = item.get("note", None)

            self.set_x(10)
            self.cell(col_widths[0], 9, item_name, 1)
            self.cell(col_widths[1], 9, self._format_currency(currency, amount), 1, 0, "R")
            total += amount
            self.ln()

            if note:
                self.set_x(12)
                self.set_font("helvetica", "I", 10)
                self.set_text_color(90)
                self.multi_cell(sum(col_widths) - 4, 6, self._safe_text(note))
                self.set_font("helvetica", "", 11)
                self.set_text_color(0)

        # Summary section - SAĞ ALTTA (örnekteki gibi)
        deposit = data.get("deposit", 0.0)
        remaining = total - deposit
        
        # Sağ alt köşeye yerleştir
        summary_y = self.get_y() + 10
        summary_x = 110  # Sağ taraf
        
        self.set_y(summary_y)
        self.set_x(summary_x)
        
        # Total, Deposit, Remaining - sağ hizalı
        self.set_font("helvetica", "B", 12)
        self.cell(90, 8, f"Total: {self._format_currency(currency, total)}", 0, 1, "R")
        
        self.set_x(summary_x)
        self.set_font("helvetica", "", 11)
        self.cell(90, 8, f"Deposit: {self._format_currency(currency, deposit)}", 0, 1, "R")
        
        self.set_x(summary_x)
        self.set_font("helvetica", "B", 12)
        self.cell(90, 8, f"Remaining: {self._format_currency(currency, remaining)}", 0, 1, "R")

        # Cash note
        if data.get("cash_note"):
            self.set_font("helvetica", "I", 10)
            self.set_text_color(120)
            self.set_y(self.get_y() + 3)
            self.set_x(10)
            self.multi_cell(0, 5, self._safe_text(data["cash_note"]))
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
