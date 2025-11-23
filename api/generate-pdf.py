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
        # Title - ortada, büyük ve mavi
        title = self._safe_text(data.get('title', 'Invoice'))
        self.set_y(45)
        self.set_x(70)
        self.set_font("helvetica", "B", 16)
        self.set_text_color(0, 51, 102)
        self.cell(0, 20, title, ln=True, align="L")

        self.set_font("helvetica", "", 11)
        self.set_text_color(0)

        # Billed By ve Billed To - border olmadan
        billed_by_content = self._safe_text(data['billed_by'])
        billed_to_content = self._safe_text(data['billed_to'])
        
        # Satır sayılarını hesapla (sadece boş olmayan satırlar)
        billed_by_lines = [line.strip() for line in billed_by_content.split('\n') if line.strip()][:6]
        billed_to_lines = [line.strip() for line in billed_to_content.split('\n') if line.strip()][:6]
        
        # Yüksekliği hesapla
        header_height = 7
        line_height = 6
        max_content_lines = max(len(billed_by_lines), len(billed_to_lines))
        content_height = header_height + (max_content_lines * line_height)
        
        start_y = 65
        left_x = 10
        content_width = 90
        # Sağ taraf için: sayfa genişliği (210mm) - margin (10mm) - content genişliği
        right_x = 210 - 10 - content_width  # = 110, ama daha açık hesaplama
        
        # Billed By içeriği - SOL TARAF, SOL HİZALI
        current_y = start_y
        self.set_x(left_x)
        self.set_y(current_y)
        self.set_font("helvetica", "B", 12)
        self.set_text_color(0)
        self.cell(content_width, header_height, "Billed By:", ln=0, align="L")
        
        current_y += header_height
        self.set_x(left_x)
        self.set_y(current_y)
        self.set_font("helvetica", "", 10)
        self.set_text_color(50)
        for i, line in enumerate(billed_by_lines):
            self.set_x(left_x)
            self.set_y(current_y)
            self.cell(content_width, line_height, line, ln=0, align="L")
            current_y += line_height
        
        # Billed To içeriği - template'teki sağdaki boşluğa ortalanmış şekilde
        bubble_x = 125  # Template'teki sağdaki boşluğun başlangıç x değeri
        bubble_width = 55  # Boşluğun yaklaşık genişliği
        
        current_y = start_y
        self.set_xy(bubble_x, current_y)  # Koordinata git
        self.set_font("helvetica", "B", 12)
        self.set_text_color(0)
        # align="L" yapıyoruz ki kutunun içinde sola yaslı dursun
        self.cell(bubble_width, header_height, "Billed To:", ln=0, align="L")
        
        current_y += header_height
        self.set_font("helvetica", "", 10)
        self.set_text_color(50)
        
        for i, line in enumerate(billed_to_lines):
            # KRİTİK GÜNCELLEME: Her satırı yazmadan önce imleci tekrar sağa (125'e) çekiyoruz
            self.set_xy(bubble_x, current_y)
            
            # border=0 (çizgi yok), align="L" (sola yaslı)
            self.cell(bubble_width, line_height, line, ln=0, align="L")
            
            # Manuel olarak bir alt satıra iniyoruz
            current_y += line_height
        
        # max_height'ı güncelle
        max_height = content_height

        # Invoice number ve date - dinamik pozisyon (Billed By/To'nun altına)
        invoice_y = 65 + max_height + 5  # Billed By/To'nun altına 5mm boşluk
        self.set_y(invoice_y)
        self.set_x(10)
        
        # Invoice number - generate basit bir unique number
        invoice_no = data.get('invoice_no', f"A{int(os.urandom(4).hex(), 16) % 1000000:06d}")
        
        self.cell(90, 8, f"Invoice No: {invoice_no}", ln=0)
        self.set_x(110)
        self.cell(90, 8, f"Invoice Date: {data['invoice_date']}", ln=1)

        # Items table - dinamik pozisyon (Invoice No/Date'in altına)
        items_y = invoice_y + 12  # Invoice No/Date'in altına 12mm boşluk
        self.set_y(items_y)
        self.set_x(10)
        self.set_fill_color(225, 236, 247)
        self.set_text_color(0, 51, 102)
        self.set_font("helvetica", "B", 12)

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

            col_idx = 1
            if data.get("show_quantity", True):
                self.cell(col_widths[col_idx], 9, str(quantity), 1, 0, "R")
                col_idx += 1
            if data.get("show_rate", False):
                self.cell(col_widths[col_idx], 9, self._format_currency(currency, rate), 1, 0, "R")
                col_idx += 1
            if data.get("show_amount", True):
                self.cell(col_widths[col_idx], 9, self._format_currency(currency, amount), 1, 0, "R")
            total += amount
            self.ln()

            if note:
                self.set_x(12)
                self.set_font("helvetica", "I", 10)
                self.set_text_color(90)
                self.multi_cell(sum(col_widths), 6, self._safe_text(note))
                self.set_font("helvetica", "", 11)
                self.set_text_color(0)

        # Summary section - SAĞ ALTTA, items tablosunun bittiği yerden itibaren
        deposit = data.get("deposit", 0.0)
        remaining = total - deposit
        
        # Items tablosunun bitiş pozisyonunu al
        items_end_y = self.get_y()
        
        # Summary'yi items tablosunun bittiği yerden itibaren sağ altta yerleştir
        summary_start_y = items_end_y + 10  # Items tablosundan 10mm boşluk
        summary_x = 110  # Sağ taraf
        summary_width = 90
        
        self.set_y(summary_start_y)
        self.set_x(summary_x)
        
        # Summary - sağ hizalı, items tablosundan ayrı
        self.set_font("helvetica", "B", 12)
        self.set_text_color(0)
        self.cell(summary_width, 8, f"Total: {self._format_currency(currency, total)}", 0, 1, "R")
        
        self.set_x(summary_x)
        self.set_font("helvetica", "", 11)
        self.set_text_color(60)
        self.cell(summary_width, 8, f"Deposit: {self._format_currency(currency, deposit)}", 0, 1, "R")
        
        # Remaining kısmı opsiyonel - varsayılan olarak gösterilir
        if data.get("show_remaining", True):
            self.set_x(summary_x)
            self.set_font("helvetica", "B", 12)
            self.set_text_color(0)
            self.cell(summary_width, 8, f"Remaining: {self._format_currency(currency, remaining)}", 0, 1, "R")

        # Cash note - Summary'nin altında
        if data.get("cash_note"):
            self.set_font("helvetica", "I", 10)
            self.set_text_color(120)
            self.set_y(self.get_y() + 3)
            self.set_x(summary_x)
            self.multi_cell(summary_width, 5, self._safe_text(data["cash_note"]), 0, "R")
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
