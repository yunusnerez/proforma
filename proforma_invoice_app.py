from flask import Flask, render_template, request, send_file, jsonify
from fpdf import FPDF
import os
import io
from datetime import datetime
from pdf2image import convert_from_path
from PIL import Image
import tempfile

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

def get_next_invoice_number():
    file_path = "invoice_counter.txt"
    if not os.path.exists(file_path):
        with open(file_path, "w") as f:
            f.write("A013000")
    with open(file_path, "r") as f:
        current = f.read().strip()
    prefix = current[:1]
    number = int(current[1:]) + 1
    new_number = f"{prefix}{number:06}"
    with open(file_path, "w") as f:
        f.write(new_number)
    return new_number

def pdf_to_image(pdf_path):
    """Convert first page of PDF to image"""
    try:
        # Try to get poppler path from environment variable (for deployment platforms)
        poppler_path = os.environ.get('POPPLER_PATH', None)
        
        # Convert PDF to image
        if poppler_path:
            images = convert_from_path(pdf_path, first_page=1, last_page=1, dpi=150, poppler_path=poppler_path)
        else:
            images = convert_from_path(pdf_path, first_page=1, last_page=1, dpi=150)
        
        if images:
            # Save to temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
            images[0].save(temp_file.name, 'JPEG')
            return temp_file.name
    except Exception as e:
        print(f"Error converting PDF to image: {e}")
        # If PDF conversion fails, try to use a fallback image if exists
        fallback_path = "new_template.jpg"
        if os.path.exists(fallback_path):
            return fallback_path
    return None

class PDF(FPDF):
    def header(self):
        # Template PDF'ini image'a çevir ve kullan
        template_path = "new_template.pdf"
        if os.path.exists(template_path):
            try:
                # PDF'i image'a çevir
                img_path = pdf_to_image(template_path)
                if img_path:
                    self.image(img_path, x=0, y=0, w=210, h=297)
                    # Temporary file'ı sil
                    try:
                        os.unlink(img_path)
                    except:
                        pass
            except Exception as e:
                print(f"Error loading template: {e}")
                # Template yüklenemezse devam et (template olmadan PDF oluştur)
                pass

    def add_invoice(self, data):
        self.set_y(45)
        self.set_font("Arial", "B", 16)
        self.set_text_color(0, 51, 102)
        self.cell(0, 20, data.get("title", "Invoice"), ln=True, align="C")

        self.set_font("Arial", "", 11)
        self.set_text_color(0)

        self.set_y(65)
        self.set_x(10)
        self.set_draw_color(180)
        self.set_line_width(0.2)
        self.multi_cell(90, 5.5, f"Billed By:\n{data.get('billed_by', '')}", border=1)

        self.set_y(65)
        self.set_x(110)
        self.multi_cell(90, 5.5, f"Billed To:\n{data.get('billed_to', '')}", border=1)

        self.set_y(85)
        self.set_x(10)
        self.cell(90, 8, f"Invoice No: {data.get('invoice_no', '')}", ln=0)
        self.set_x(110)
        self.cell(90, 8, f"Invoice Date: {data.get('invoice_date', '')}", ln=1)

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

        # Deposit ve Remaining ekle (eğer deposit varsa)
        deposit = data.get("deposit", 0.0)
        if deposit > 0:
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

@app.after_request
def after_request(response):
    # X-Frame-Options header'ını kaldır (iframe'e izin ver)
    response.headers.pop('X-Frame-Options', None)
    # Content-Security-Policy ayarları - iframe'e izin ver
    response.headers['Content-Security-Policy'] = "frame-ancestors *"
    # CORS headers (opsiyonel ama iyi pratik)
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

@app.route('/')
def index():
    return render_template('invoice_form.html')

@app.route('/generate', methods=['POST'])
def generate_pdf():
    try:
        # Form verilerini al
        invoice_no = get_next_invoice_number()
        
        data = {
            "title": request.form.get("title", "Invoice"),
            "invoice_no": invoice_no,
            "invoice_date": request.form.get("invoice_date", datetime.now().strftime("%Y-%m-%d")),
            "billed_by": request.form.get("billed_by", ""),
            "billed_to": request.form.get("billed_to", ""),
            "currency": request.form.get("currency", "£"),
            "show_quantity": request.form.get("show_quantity") == "on",
            "show_rate": request.form.get("show_rate") == "on",
            "show_amount": request.form.get("show_amount") == "on",
            "cash_note": request.form.get("cash_note", ""),
            "deposit": float(request.form.get("deposit", 0) or 0),
            "items": []
        }

        # Items'ları parse et
        item_names = request.form.getlist("item_name[]")
        item_quantities = request.form.getlist("item_quantity[]")
        item_rates = request.form.getlist("item_rate[]")
        item_notes = request.form.getlist("item_note[]")
        
        for name, qty, rate, note in zip(item_names, item_quantities, item_rates, item_notes):
            if name.strip():  # Boş olmayan item'ları ekle
                data["items"].append({
                    "item": name.strip(),
                    "quantity": float(qty) if qty else 1,
                    "rate": float(rate) if rate else 0,
                    "note": note.strip() if note else ""
                })

        # PDF oluştur
        pdf = PDF()
        pdf.set_doc_option("core_fonts_encoding", "windows-1252")
        pdf.add_page()
        pdf.add_invoice(data)

        # PDF'i memory'de sakla
        pdf_bytes = pdf.output(dest='S').encode('latin-1')

        # Dosya adı oluştur
        name = data["billed_to"].split("\n")[0].replace(" ", "_") if data["billed_to"] else "invoice"
        file_name = f"invoice_{invoice_no}_{name}.pdf"

        # PDF'i response olarak döndür
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=file_name
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Gerekli klasörleri oluştur
    os.makedirs("templates", exist_ok=True)
    os.makedirs("invoices", exist_ok=True)
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)

