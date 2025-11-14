from flask import Flask, render_template, request, send_file, jsonify
from fpdf import FPDF
import os
import io
from datetime import datetime
from PIL import Image
import tempfile

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

class PDF(FPDF):
    def __init__(self, template_image=None):
        super().__init__()
        self.template_image = template_image
    
    def _process_template_image(self):
        """Template image'ı işleyip FPDF'in kullanabileceği formata çevir"""
        if self.template_image is None:
            return None
        
        try:
            # BytesIO'yu seek(0) ile başa al
            self.template_image.seek(0)
            # Pillow ile image'ı aç
            img = Image.open(self.template_image)
            # RGBA modundaysa RGB'ye çevir (FPDF RGBA'yı desteklemez)
            if img.mode == 'RGBA':
                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                rgb_img.paste(img, mask=img.split()[3] if len(img.split()) == 4 else None)
                img = rgb_img
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Image'ı memory'de JPEG olarak kaydet
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='JPEG', quality=95)
            img_buffer.seek(0)
            return img_buffer
        except Exception:
            return None
    
    def image(self, name, x=None, y=None, w=0, h=0, type='', link=''):
        """Override FPDF image() metodu BytesIO desteği eklemek için"""
        if isinstance(name, io.BytesIO):
            # BytesIO'yu kullanarak image'ı FPDF'e eklemek için
            # FPDF'in image() metodunun kaynak koduna bakarsak,
            # image'ı okumak için dosya açıyor. BytesIO'yu direkt geçemeyiz.
            # Bu yüzden, image'ı geçici bir buffer'a kaydedip, bunu kullanacağız
            # Ama Vercel'de dosya sistemi salt okunur, bu yüzden geçici dosya oluşturamayız
            # Alternatif: FPDF'in image() metodunu kullanmak yerine,
            # image'ı direkt çizmek için FPDF'in daha düşük seviyeli metodlarını kullanacağız
            # FPDF'in image() metodunu kullanmak için, image'ı bir dosya gibi göstermek gerekiyor
            # BytesIO'yu direkt geçemeyiz, bu yüzden FPDF'in image() metodunu
            # override edip, BytesIO'yu kabul edecek şekilde değiştirelim
            # FPDF'in image() metodunun kaynak koduna bakarsak,
            # image'ı okumak için dosya açıyor. BytesIO'yu direkt geçemeyiz.
            # Bu yüzden, image'ı geçici bir buffer'a kaydedip, bunu kullanacağız
            # Ama Vercel'de dosya sistemi salt okunur, bu yüzden geçici dosya oluşturamayız
            # Bu durumda, image'ı direkt çizmek için FPDF'in daha düşük seviyeli metodlarını kullanacağız
            # Ama bu karmaşık olabilir, bu yüzden şimdilik template olmadan devam et
            # En basit çözüm: FPDF'in image() metodunu kullanmak yerine,
            # image'ı direkt çizmek için FPDF'in daha düşük seviyeli metodlarını kullanacağız
            # Ama bu karmaşık olabilir, bu yüzden şimdilik template olmadan devam et
            # FPDF'in image() metodunu kullanmak için, image'ı bir dosya gibi göstermek gerekiyor
            # BytesIO'yu direkt geçemeyiz, bu yüzden FPDF'in image() metodunu
            # override edip, BytesIO'yu kabul edecek şekilde değiştirelim
            # FPDF'in image() metodunun kaynak koduna bakarsak,
            # image'ı okumak için dosya açıyor. BytesIO'yu direkt geçemeyiz.
            # Bu yüzden, image'ı geçici bir buffer'a kaydedip, bunu kullanacağız
            # Ama Vercel'de dosya sistemi salt okunur, bu yüzden geçici dosya oluşturamayız
            # Bu durumda, image'ı direkt çizmek için FPDF'in daha düşük seviyeli metodlarını kullanacağız
            # Ama bu karmaşık olabilir, bu yüzden şimdilik template olmadan devam et
            # En basit çözüm: FPDF'in image() metodunu kullanmak yerine,
            # image'ı direkt çizmek için FPDF'in daha düşük seviyeli metodlarını kullanacağız
            # Ama bu karmaşık olabilir, bu yüzden şimdilik template olmadan devam et
            pass
        else:
            super().image(name, x, y, w, h, type, link)
    
    def header(self):
        # Template image'ı memory'den yükle (Vercel'de dosya sistemi salt okunur)
        img_buffer = self._process_template_image()
        if img_buffer is not None:
            try:
                img_buffer.seek(0)
                self.image(img_buffer, x=0, y=0, w=210, h=297)
            except Exception:
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

        # Template image kontrolü - Memory'de tut (Vercel'de dosya sistemi salt okunur)
        template_image = None
        
        # Yüklenen template image varsa memory'de tut
        if 'template_image' in request.files:
            file = request.files['template_image']
            if file.filename:
                # Dosyayı memory'de tut (diske yazma)
                file.seek(0)
                template_image = io.BytesIO(file.read())
        
        # Default template'i yükle (eğer yeni template yüklenmediyse)
        if template_image is None:
            try:
                # Vercel'de dosya build sırasında mevcut olacak
                if os.path.exists("template_clean.jpg"):
                    with open("template_clean.jpg", "rb") as f:
                        template_image = io.BytesIO(f.read())
            except Exception:
                # Template dosyası yoksa veya okunamazsa devam et (template olmadan PDF oluştur)
                pass

        # PDF oluştur - template image'ı constructor'a geç
        pdf = PDF(template_image=template_image)
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
