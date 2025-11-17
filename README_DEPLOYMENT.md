# Treatment Plan Generator - Deployment Guide

Bu proje, Python Flask kullanarak bir Treatment Plan PDF generator web uygulamasıdır.

## 🚀 Deployment Seçenekleri

### 1. Vercel (Önerilen - Ücretsiz)

**Adımlar:**
1. GitHub'a projeyi push edin
2. [Vercel](https://vercel.com) hesabı oluşturun
3. "New Project" → GitHub repo'nuzu seçin
4. Build settings:
   - Framework Preset: Other
   - Build Command: (boş bırakın)
   - Output Directory: (boş bırakın)
5. Deploy edin!

**Not:** `vercel.json` dosyası zaten hazır.

### 2. Railway (Kolay - Ücretsiz Tier)

**Adımlar:**
1. [Railway](https://railway.app) hesabı oluşturun
2. "New Project" → "Deploy from GitHub repo"
3. Repo'nuzu seçin
4. Railway otomatik olarak Flask uygulamanızı algılar
5. Deploy edin!

**Gerekli:** `Procfile` dosyası oluşturun:
```
web: gunicorn app:app
```

### 3. Render (Ücretsiz Tier)

**Adımlar:**
1. [Render](https://render.com) hesabı oluşturun
2. "New Web Service" → GitHub repo'nuzu bağlayın
3. Settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
4. Deploy edin!

## 📋 Lokal Test

```bash
# Virtual environment oluştur
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Dependencies yükle
pip install -r requirements.txt

# Uygulamayı çalıştır
python app.py
```

Tarayıcıda `http://localhost:5000` adresine gidin.

## 📁 Dosya Yapısı

```
proforma_invoice_toolkit/
├── app.py                 # Flask uygulaması
├── templates/
│   └── index.html        # Web formu
├── requirements.txt      # Python dependencies
├── vercel.json          # Vercel config
├── template_clean.jpg    # PDF template (opsiyonel)
└── README_DEPLOYMENT.md  # Bu dosya
```

## ⚠️ Önemli Notlar

1. **Template Image:** `template_clean.jpg` dosyasını projeye eklemeyi unutmayın
2. **Production için:** Gunicorn kullanmanız önerilir:
   ```bash
   pip install gunicorn
   gunicorn app:app
   ```
3. **Environment Variables:** Gerekirse `.env` dosyası kullanabilirsiniz

## 🔧 Sorun Giderme

- **Port hatası:** Render/Railway port'u otomatik ayarlar, `app.py`'de `port=5000` kısmını kaldırın
- **Template bulunamadı:** `template_clean.jpg` dosyasının root dizinde olduğundan emin olun
- **Import hatası:** `requirements.txt`'deki tüm paketlerin yüklü olduğunu kontrol edin

