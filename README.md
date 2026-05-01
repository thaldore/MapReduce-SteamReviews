# SteamSum | MapReduce Steam Review Analyzer

Bu proje, Steam üzerinden çekilen 10.000 oyun yorumunu **MapReduce** mimarisi kullanarak analiz eden ve sonuçları modern bir web arayüzünde sunan tam kapsamlı (full-stack) bir uygulamadır.

## 🚀 Özellikler

- **Hızlı Analiz:** Python `multiprocessing` modülü sayesinde işlemci çekirdeklerini paralel kullanarak binlerce yorumu saniyeler içinde işler.
- **Duygu Analizi:** Her oyun için olumlu/olumsuz yorum oranlarını hesaplar.
- **Kelime Frekansı:** En çok kullanılan anahtar kelimeleri belirler ve global bir "Kelime Bulutu" oluşturur.
- **Modern Dashboard:** Glassmorphism tasarımı, etkileşimli grafikler (Chart.js) ve hızlı arama özelliği.

## 🛠️ Mimari ve Yöntemler

### 1. Veri Toplama (`fetch_reviews.py`)

Steam Review API kullanılarak en popüler 100 oyunun her birinden 100'er adet yorum çekilir ve `raw_reviews.json` dosyasına kaydedilir.

### 2. MapReduce İşleme (`backend/analyzer.py`)

- **Map Stage:** Veri, işlemci çekirdek sayısına bölünür. Her çekirdek kendi veri parçasını temizler (stop words temizliği), duyguları sayar ve kelime frekanslarını çıkarır.
- **Reduce Stage:** Tüm çekirdeklerden gelen sonuçlar birleştirilerek tek bir analiz raporu (`analysis_results.json`) oluşturulur.

### 3. Backend (`backend/app.py`)

Flask framework'ü kullanılarak API endpoint'leri sunulur. Analiz sonuçlarını servis eder ve isteğe bağlı olarak MapReduce işlemini tetikler.

### 4. Frontend (`frontend/`)

HTML5, CSS3 (Vanilla) ve JavaScript (ES6+) kullanılarak geliştirilmiştir.

- **Chart.js:** Duygu dağılımı grafikleri için.
- **CSS Grid/Flexbox:** Responsive ve modern düzen için.

## 📦 Kurulum

1. Bağımlılıkları yükleyin:

```bash
pip install flask flask-cors requests
```

1. Verileri çekin (Zaten çekildiyse bu adımı geçebilirsiniz):

```bash
python fetch_reviews.py
```

1. Backend sunucusunu başlatın:

```bash
python backend/app.py
```

1. Tarayıcınızda şu adrese gidin:

`http://127.0.0.1:5000`

## 💻 Donanım Optimizasyonu

Bu proje, özellikle çok çekirdekli işlemciler (Örn: Intel i7-13620H) için optimize edilmiştir. `multiprocessing.Pool` kullanımı sayesinde CPU kullanımı maksimuma çıkarılarak analiz süresi minimize edilmiştir.

---
*Bu proje MapReduce mantığını anlamak ve modern web teknolojileriyle birleştirmek amacıyla geliştirilmiştir.*
