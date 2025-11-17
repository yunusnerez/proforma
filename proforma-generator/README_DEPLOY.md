# Vercel Deployment Guide

Bu proje Vercel'de deploy edilmek için hazırlanmıştır.

## Gereksinimler

- Node.js 18+ 
- Vercel hesabı

## Local Test (Opsiyonel)

```bash
# Dependencies yükle
npm install

# Development server başlat
npm run dev
```

## Vercel'e Deploy

### Yöntem 1: Vercel CLI ile

```bash
# Vercel CLI yükle (eğer yoksa)
npm i -g vercel

# Deploy et
vercel

# Production'a deploy et
vercel --prod
```

### Yöntem 2: Vercel Dashboard ile

1. https://vercel.com adresine git
2. "New Project" butonuna tıkla
3. GitHub/GitLab repository'ni seç veya "Import Git Repository" ile projeyi yükle
4. Root directory olarak `/Users/yunusnerez/Desktop/proforma_invoice_toolkit` seç
5. Framework Preset: Next.js
6. Build Command: `npm run build` (otomatik gelecek)
7. Output Directory: `.next` (otomatik gelecek)
8. Install Command: `npm install`
9. "Deploy" butonuna tıkla

## Önemli Notlar

- Template image (`new_template.jpg`) API klasöründe bulunmalı (zaten kopyalandı)
- Python runtime otomatik olarak Vercel tarafından yönetilir
- PDF oluşturma işlemi serverless function'da gerçekleşir
- Invoice counter dosyası kullanılmıyor (her istek için unique number üretiliyor)

## Environment Variables

Şu an için environment variable gerekmiyor. İleride gerekiyorsa Vercel dashboard'dan ekleyebilirsiniz.

