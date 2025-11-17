from flask import Flask, render_template, request, send_file, jsonify
from fpdf import FPDF
import os
import io
from datetime import datetime

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

class PDF(FPDF):
    def header(self):
        # Template görselini direkt dosya yolundan yükle (Vercel'de build sırasında mevcut)
        template_path = "template_clean.jpg"
        if os.path.exists(template_path):
            try:
                self.image(template_path, x=0, y=0, w=210, h=297)
            except Exception:
                # Template yüklenemezse devam et (template olmadan PDF oluştur)
                pass

    def add_content(self, data):
        self.set_font("Arial", "B", 16)
        self.set_text_color(0, 51, 102)
        self.set_y(50)
        self.cell(0, 10, data.get("title", "Treatment Plan"), ln=True, align="C")

        self.set_font("Arial", "B", 11)
        self.multi_cell(0, 6, f"Tailored for:\n")
        self.set_font("Arial", "", 11)
        self.multi_cell(0, 6, data.get('billed_to', ''))

        self.set_y(95)
        self.set_font("Arial", "B", 12)
        self.set_fill_color(225, 236, 247)
        self.set_text_color(0, 51, 102)
        self.cell(180, 9, "Included Therapies", 1, 1, "C", True)

        self.set_font("Arial", "", 11)
        self.set_text_color(0)
        treatments = data.get("treatments", [])
        for i, item in enumerate(treatments, 1):
            # Ana satır (kutulu)
            self.cell(180, 8, f"{i}. {item.get('name', '')}", border=1, ln=1)

            # Eğer not varsa, alt satıra italik ve gri olarak yaz (kutusuz)
            if item.get("note"):
                self.set_font("Arial", "I", 10)
                self.set_text_color(100)
                self.cell(180, 6, f"   {item['note']}", border=0, ln=1)
                self.set_font("Arial", "", 11)
                self.set_text_color(0)

        total = data.get("total", "")
        if total:
            self.set_y(self.get_y() + 10)
            self.set_font("Arial", "B", 12)
            self.cell(0, 10, f"Total Package Price: {total}", ln=True, align="R")
            self.set_font("Arial", "I", 9)
            self.set_text_color(80)
            self.cell(0, 6, "Payment is done in cash", ln=True, align="R")
            self.set_text_color(0)
        
        consultant = data.get("consultant", "Yunus")
        self.set_font("Arial", "B", 10)
        self.cell(0, 6, "Your Medical Consultant:", ln=True, align="R")
        self.set_font("Arial", "", 10)
        self.cell(0, 6, consultant, ln=True, align="R")

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
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_pdf():
    try:
        # Form verilerini al
        data = {
            "title": request.form.get("title", "Treatment Plan"),
            "billed_to": request.form.get("billed_to", ""),
            "total": request.form.get("total", ""),
            "consultant": request.form.get("consultant", "Yunus"),
            "treatments": []
        }

        # Tedavileri parse et
        treatment_names = request.form.getlist("treatment_name[]")
        treatment_notes = request.form.getlist("treatment_note[]")
        
        for name, note in zip(treatment_names, treatment_notes):
            if name.strip():  # Boş olmayan tedavileri ekle
                data["treatments"].append({
                    "name": name.strip(),
                    "note": note.strip() if note else ""
                })

        # PDF oluştur - template görseli gömülü (template_clean.jpg dosyasından otomatik yüklenir)
        pdf = PDF()
        pdf.add_page()  # add_page() otomatik olarak header() metodunu çağırır
        pdf.add_content(data)

        # PDF'i memory'de sakla
        pdf_bytes = pdf.output(dest='S').encode('latin-1')

        # Dosya adı oluştur
        name = data["billed_to"].split("\n")[0].replace(" ", "_") if data["billed_to"] else "treatment_plan"
        file_name = f"treatment_plan_{name}.pdf"

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
    # Template klasörünü oluştur
    os.makedirs("templates", exist_ok=True)
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
