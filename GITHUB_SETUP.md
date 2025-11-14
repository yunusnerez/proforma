# GitHub'a Yükleme Adımları

## 1. GitHub'da Repository Oluştur

1. [GitHub.com](https://github.com) adresine git ve giriş yap
2. Sağ üstteki "+" butonuna tıkla → "New repository"
3. Repository adı: `treatment-plan-generator` (veya istediğin bir isim)
4. **Public** veya **Private** seç (önerilen: Public - ücretsiz deployment için)
5. **"Initialize this repository with a README" seçme!** (zaten dosyalarımız var)
6. "Create repository" butonuna tıkla

## 2. Terminal'de Şu Komutları Çalıştır

```bash
cd /Users/yunusnerez/Desktop/proforma_invoice_toolkit

# GitHub repository URL'ini ekle (kendi repository URL'ini kullan)
git remote add origin https://github.com/KULLANICI_ADIN/treatment-plan-generator.git

# Dosyaları GitHub'a push et
git branch -M main
git push -u origin main
```

**Önemli:** `KULLANICI_ADIN` kısmını kendi GitHub kullanıcı adınla değiştir!

## 3. Vercel'e Deploy Et

1. [Vercel.com](https://vercel.com) adresine git
2. "Sign Up" → GitHub hesabınla giriş yap
3. "Add New Project" butonuna tıkla
4. GitHub repository'ni seç
5. Vercel otomatik olarak ayarları algılayacak:
   - Framework: Other
   - Build Command: (boş)
   - Output Directory: (boş)
6. "Deploy" butonuna tıkla
7. Birkaç dakika içinde siten hazır olacak! 🎉

## Alternatif: GitHub CLI ile (Daha Kolay)

Eğer GitHub CLI yüklüyse:

```bash
gh repo create treatment-plan-generator --public --source=. --remote=origin --push
```

Bu komut otomatik olarak:
- GitHub'da repository oluşturur
- Remote ekler
- Push yapar

