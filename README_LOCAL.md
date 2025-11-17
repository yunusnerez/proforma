# Yerel Geliştirme Kılavuzu

Bu projeyi yerel olarak çalıştırmak için aşağıdaki adımları takip edin.

## Gereksinimler

- **Node.js** 18+ (npm ile birlikte)
- **Python** 3.9+ (pip3 ile birlikte)
- **Vercel CLI** (Python API'yi test etmek için - opsiyonel)

## Kurulum

### 1. Node.js Bağımlılıklarını Yükle

```bash
npm install
```

### 2. Python Bağımlılıklarını Yükle

```bash
pip3 install fpdf2 Pillow
```

veya

```bash
pip3 install -r requirements.txt
```

**Not:** Eğer `requirements.txt` dosyasındaki versiyonlar Python 3.13 ile uyumlu değilse, yukarıdaki komutu kullanın (versiyon kısıtlaması olmadan).

## Yerel Çalıştırma

### Seçenek 1: Vercel CLI ile (Önerilen - Tüm özellikler çalışır)

Bu yöntem hem Next.js frontend'i hem de Python API'yi tam olarak test etmenizi sağlar:

```bash
# Vercel CLI'yi global olarak yükle (eğer yoksa)
npm i -g vercel

# Yerel development server'ı başlat
vercel dev
```

Bu komut:
- Next.js frontend'i çalıştırır
- Python serverless function'ları simüle eder
- Tüm API endpoint'lerini test edebilmenizi sağlar

Tarayıcınızda `http://localhost:3000` adresine gidin.

### Seçenek 2: Sadece Next.js Dev Server (Frontend testi)

Eğer sadece frontend'i test etmek istiyorsanız:

```bash
npm run dev
```

**Not:** Bu yöntemle Python API endpoint'i (`/api/generate-pdf`) çalışmayabilir. Tam test için Vercel CLI kullanın.

## Kullanım

1. Tarayıcınızda `http://localhost:3000` adresine gidin
2. Formu doldurun:
   - Invoice bilgilerini girin
   - Billed By ve Billed To bilgilerini ekleyin
   - Item'ları ekleyin/düzenleyin
   - Gerekli ayarları yapın
3. "Generate PDF" butonuna tıklayın
4. PDF otomatik olarak indirilecektir

## Önemli Dosyalar

- `app/page.tsx` - Ana form sayfası
- `app/globals.css` - Stil dosyası
- `api/generate-pdf.py` - PDF oluşturma API endpoint'i
- `api/new_template.jpg` - PDF template görseli

## Sorun Giderme

### Python paketleri yüklenmiyor

Eğer `requirements.txt` dosyasındaki versiyonlar Python sürümünüzle uyumlu değilse:

```bash
pip3 install fpdf2 Pillow
```

### Vercel CLI yok

```bash
npm i -g vercel
```

### Port zaten kullanılıyor

Eğer 3000 portu kullanılıyorsa, Next.js otomatik olarak başka bir port seçecektir (örn: 3001). Terminal çıktısına bakın.

### API çalışmıyor

- Vercel CLI ile çalıştırdığınızdan emin olun (`vercel dev`)
- `api/generate-pdf.py` dosyasının mevcut olduğunu kontrol edin
- `api/new_template.jpg` dosyasının mevcut olduğunu kontrol edin

## Production Build

Production build oluşturmak için:

```bash
npm run build
npm start
```

Bu komutlar production-ready bir build oluşturur ve test edebilmenizi sağlar.

