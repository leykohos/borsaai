# 📈 BorsaAI - Teknik Analiz ve Yapay Zeka Robotu

BorsaAI, hisse senedi verilerini canlı olarak çeken, teknik indikatörlerle analiz eden ve **Google Gemini AI** kullanarak finansal tablo üzerine anlık stratejik yorumlar üreten güçlü bir web tabanlı analiz aracıdır. Başlangıçta Borsa İstanbul şirketlerinden `ALBRK.IS` (Albaraka Türk) için yapılandırılmıştır, ancak herhangi bir sembol ile kolayca çalıştırılabilir.

![BorsaAI](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Framework-Flask-green.svg)
![Chart.js](https://img.shields.io/badge/Charts-Chart.js-red.svg)
![Gemini AI](https://img.shields.io/badge/AI-Google%20Gemini-orange.svg)

---

## 🚀 Özellikler

- **Gelişmiş Grafikler:** `Chart.js` tabanlı 🕯️ Mum (Candlestick) ve 📈 Çizgi fiyat grafikleri. 
- **Zengin İndikatörler:** MACD, RSI (14), Stochastic RSI, ve Bollinger Bantları analizleri.
- **Yapay Zeka Destekli Yorum (Gemini):** Mevcut teknik verilere ve algoritmik "Al" sinyallerine dayanarak Gemini 2.5 Flash modeli üzerinden anlık senaryolar, risk faktörleri ve teknik görünüm raporu oluşturma.
- **Dinamik Periyot Seçimi:** İnceleme yapmak için Saatlik (1h), Günlük (1d), Haftalık (1wk) ve Aylık (1mo) zaman dilimlerinde hızlı geçiş.
- **Geçmişe Yönelik Sinyal Tarama:** RSI ve MACD kesişimlerini takip ederek çalışan algoritmik bir "Al Sinyali" avcısı. Sinyallerden sonraki (1 Hafta, 1 Ay, 3 Ay) getiri performanslarını hesaplama.

---

## 🛠️ Kurulum

Projeyi kendi bilgisayarınızda çalıştırmak için aşağıdaki adımları izleyin:

### 1. Projeyi Klonlayın
```bash
git clone https://github.com/KULLANICI_ADINIZ/borsaai.git
cd borsaai
```

### 2. Sanal Ortam (Virtual Environment) Oluşturun (Önerilen)
```bash
python -m venv venv
# Windows için:
venv\Scripts\activate
# macOS ve Linux için:
source venv/bin/activate
```

### 3. Gerekli Kütüphaneleri Yükleyin
```bash
pip install -r requirements.txt
```

### 4. Ortam Değişkenlerini Ayarlayın
Proje dizininde bir `.env` dosyası oluşturun ve içerisine Google Gemini API Anahtarınızı ekleyin.
(`.env` dosyası repoda bulunmaz, `.gitignore` ile korunmaktadır.)

```env
GEMINI_API_KEY=sizin_gizli_api_anahtariniz_buraya
```
> **Not:** Gemini API anahtarınızı ücretsiz olarak [Google AI Studio](https://aistudio.google.com/) üzerinden alabilirsiniz.

---

## 💻 Kullanım

Sunucuyu başlatmak için aşağıdaki komutu çalıştırın:
```bash
python app.py
```
Sunucu başladığında tarayıcınızda `http://localhost:5000` adresine giderek uygulamayı kullanmaya başlayabilirsiniz. 
- Sağ sekmede bulunan **⚡ AI Analizi Başlat** butonuna tıklayarak son verilere göre yapay zeka yapılmış detaylı durum değerlendirmesini okuyabilirsiniz.
- Üst panelden **Mum Grafiği** veya **Çizgi Grafiği** seçimi yapabilirsiniz.
- Periyot tuşları ile verileri (Günlük, Haftalık vd.) değiştirebilirsiniz.

---

## 🧩 Proje Yapısı

- `app.py`: Ana Flask web sunucusu, API uç noktaları (endpoints) ve Gemini HTTP entegrasyonu.
- `indicators.py`: Pandas / Numpy kullanılarak manuel olarak yazılmış teknik analiz fonksiyonları ve sinyal algoritmaları.
- `app.js`: Arayüz (Frontend) mantığı, grafik güncellemeleri ve asenkron veri çekme.
- `index.html` & `style.css`: HTML5 iskeleti ve Vanilla CSS ile estetik tasarım sistemi.
- `requirements.txt`: Gerekli Python bağımlılıkları.

---

## 🔮 Gelecekte Eklenebilecekler

- Hisse sembolünü arayüz üzerinden dinamik olarak değiştirebilme.
- Kullanıcının kendi "Al / Sat" stratejilerini (koşullarını) kod yazmadan belirleyebilmesi.
- TradingView tarzı eklenti bildirimleri veya alarm botu entegrasyonu (Telegram/Discord vb.).

---

## ⚠️ Yasal Uyarı

Bu proje **tamamen eğitim ve geliştirme amaçlıdır**. Proje içerisinde üretilen veriler, teknik analiz göstergeleri, algoritmik "Al/Sat" sinyalleri veya yapay zeka tarafından sağlanan analiz yorumları kesinlikle **Yatırım Tavsiyesi Değildir (YTD)**. 
Finansal piyasalarda işlem yapmak yüksek risk içerir. Uygulamanın kullanımından doğabilecek maddi manevi zararlardan geliştirici sorumlu tutulamaz. Veriler [Yahoo Finance](https://finance.yahoo.com/) üzerinden 15 dakika gecikmeli olarak sağlanıyor olabilir.
