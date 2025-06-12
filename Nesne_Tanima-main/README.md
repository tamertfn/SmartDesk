# 🧠 SmartDesk AI — Gerçek Zamanlı Nesne Tanıma ve Takip Sistemi

SmartDesk, gerçek zamanlı nesne tanıma ve takip özelliklerine sahip hibrit mimaride çalışan bir Android uygulamasıdır. Amaç, dağınık masa ortamlarında nesnelerin hızlı ve doğru şekilde bulunmasını sağlamaktır. Sistem, cihaz üzerinde çalışan YOLOv8n ile hızlı tespit yapar; düşük güven skoruna sahip nesneleri daha güçlü bir model olan YOLOv11l ile sunucuda yeniden işler.

---

## 🚀 Özellikler

- 📱 **Android Uygulaması (Kotlin)**
- 📷 **Gerçek Zamanlı Kamera Görüntüsü ile Nesne Tanıma (YOLOv8n)**
- ☁️ **Sunucu Tabanlı Gelişmiş Tespit (YOLOv11l, Dockerized Server)**
- ⚡ **GPU/CPU Desteği ile Hızlı Performans**
- 🔁 **Edge–Server Hibrit Mimarisi**
- 🔒 **Modüler ve Ölçeklenebilir Tasarım (Docker + NVIDIA Runtime)**

---

## 🛠 Kullanılan Teknolojiler

| Katman         | Teknoloji                  |
|----------------|----------------------------|
| Mobil Uygulama | Kotlin, CameraX, TensorFlow Lite, Jetpack, Coroutines |
| Edge Model     | YOLOv8n (TFLite formatında) |
| Sunucu Modeli  | YOLOv11l (Linux, Uvicorn, Python, Torch) |
| Çalışma Ortamı | Docker, NVIDIA GPU, Kubernetes-Ready |

---

## 🧩 Nesne Sınıfları

**Mobil (Edge) Model Nesneleri (Open Images Dataset):**
Laptop, Keyboard, Mouse, Book, Pen, Mug, Glasses, Flashlight, Mobile phone, Watch, Fork, Spoon, Knife, Bowl, Bottle, Headphones, Coin, Snack, Glove, Necklace, iPod

**Sunucu (Server) Model Nesneleri:**
Laptop, Mobile phone, Keys, Bag, Screen, Wallet, Pen, Calculator, Lecture notes, Student ID card, Charging cable, Apple Pencil, iPad-Air, iPad-Pro, Keyboard, Mouse, Markers, Water bottle, Earphones, Watch, Glasses

---

## 🧪 Model Eğitimi

- Eğitimler Ultralytics YOLO kütüphanesi ile yapılmıştır.
- Edge model `.tflite` biçiminde optimize edilerek Android cihazlara entegre edilmiştir.
- Server model, Linux üzerinde çalışan bir Docker konteyner içinde, GPU destekli olarak çalışmaktadır.

---

## ⚙️ Sunucu Mimarisi

- Python + Uvicorn sunucu
- YOLOv11l modelini işler
- Base64 formatında gelen görseli çözümleyerek nesne tespiti yapar
- Dockerized yapı sayesinde kolay dağıtım ve ölçeklenebilirlik

---

## 📷 Uygulama Akışı

1. Android cihaz kamerası görüntüyü alır.
2. YOLOv8n ile nesneler tespit edilir.
3. Confidence < 0.75 ise görsel parçası sunucuya gönderilir.
4. Server’da YOLOv11l ile yeniden analiz yapılır.
5. Sonuç kullanıcı arayüzüne geri döner.

---

## 📈 Geliştirme Durumu

- ✅ Mobil uygulama arayüzü geliştirildi
- ✅ YOLOv8n ile cihazda tespit yapılıyor
- ✅ YOLOv11l sunucu tarafı Docker ile hazır
- 🚧 Nesne veri seti özelleştiriliyor
- 🚧 Kullanıcı arayüzü zenginleştirilecek
- 🚧 Kapsam genişletme ve cloud senkronizasyonu planlanıyor

---

## 👥 Katkı Sağlayanlar

- Hasan Tamer Tefon
- Hüseyin Göksu Hacıoğlu

---



---

## 📞 İletişim

Her türlü öneri, katkı veya sorun bildirimi için:
📧 goksu.hacioglu@gmail.com  
📧 hasantamertefon@hotmail.com
