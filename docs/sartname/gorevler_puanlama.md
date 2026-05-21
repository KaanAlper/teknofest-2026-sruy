# Görev Gereksinimleri ve Puan Hesabı

Bu dosya geliştirme önceliklendirmesi için **görevleri puana göre** sıralar ve **kabul kriterlerini** netleştirir.

## Puan-Maliyet Önceliklendirme Tablosu

| Öncelik | Görev | Puan | Risk | Gerekçe |
|:-:|---|:-:|:-:|---|
| P0 | Tanımlı görevi tamamlama (uçtan uca) | +30 | Y | Diğer tüm puanları çoğaltır |
| P0 | Haritalama | +30 | O | SLAM olmadan hiçbiri çalışmaz |
| P0 | Kullanıcı arayüzü (tam) | +20 | D | Eksik bilgi başı −4, kümülatif |
| P0 | Rota hazırlama | +20 | O | Senaryonun temel taşı |
| P0 | PLC haberleşme | +20 | Y | Protokol son ana iletilecek; soyutlama gerek |
| P0 | Kapı geçişi (PLC ile) | +20 | Y | PLC'ye bağlı |
| P1 | Sunum | +10 | D | Hazırlık + provada netleşir |
| P1 | Çizgi takibi (görüntü) | +10 | O | OpenCV ile makul |
| P1 | QR kod okuma + pose | +10 | D | pyzbar/ArUco kombinasyonu |
| P1 | Çarpışma engelleme | +10 | D | LIDAR + Nav2 maliyet haritası |
| P2 | Otomatik şarj kabiliyeti | +5 | Y | Tek başına +5 ama saha set-up gerek |
| P2 | Yerlilik | +5 | D | Yerli motor sürücü kartı veya yazılım |
| P2 | Özgünlük | +5 | D | Forklift mekanizmasında yenilik |
| P2 | Erken bitirme | +1/dk | D | Optimizasyon sonucunda kazanılır |

> Risk: D=düşük, O=orta, Y=yüksek

**P0 toplamı:** 140 puan + erken bitirme bonusu → görev tamamlama kritik.

## Ceza Yönetimi

| Ceza | Tetik | Limit |
|---|---|:-:|
| −5 / sapma | Rotadan >10 cm sapma | 2× max |
| −5 / tolerans | Bölge toleransı dışı | 2× max |
| −4 / eksik bilgi | GUI'de gerekli bilgi yok | her biri 2× |
| −1 / dk | Geç bitirme | süreklilik |
| Diskalifiye | Yük >2 kez düşme | tek seferlik |
| Diskalifiye | Otonom dışı dış müdahale | tek seferlik |

## Kabul Kriterleri (Acceptance Criteria)

### G1 — Haritalama (+30)
- [ ] 2D LIDAR ile saha haritası `.pgm/.yaml` olarak kaydediliyor
- [ ] Harita üzerinde duvarlar, kapı bölgesi, alma/bırakma alanları net
- [ ] GUI'den **"Haritala"** butonuyla başlatılıp **"Bitir"** ile kaydediliyor
- [ ] 60 dk içinde tamamlanabiliyor
- **Demo metrik:** Harita çözünürlüğü ≤5 cm/pixel; gürültü < %5

### G2 — Rota Hazırlama (+20)
- [ ] GUI'de harita üzerine bekleme/alma/bırakma/düğüm noktaları tıklanarak işaretlenebiliyor
- [ ] Düğümler bir grafa kaydediliyor (yaml/json)
- [ ] Robot manuel sürülerek noktalar "tutturulabiliyor"
- **Veri modeli:** `{node_id, type, x, y, theta, neighbors[]}`

### G3 — PLC Haberleşme (+20)
- [ ] WiFi üzerinden TCP bağlantı
- [ ] Protokol adapter pattern (`PlcGateway` arayüzü); Modbus TCP, OPC UA, ham TCP üç adapter
- [ ] Mesaj akışı GUI'de scroll log olarak görünür
- [ ] Bağlantı kopması durumunda 5 sn'de yeniden bağlanma

### G4 — Görüntü ile Çizgi Takibi (+10)
- [ ] RGB kamera frame'lerinde HSV maskeleme + Canny + contour ile çizgi merkez ekseni çıkar
- [ ] PID kontrolcüsü sapma → açısal hız
- [ ] Çizgi kaybolunca güvenli duruş

### G5 — QR Kod Okuma + Pose (+10)
- [ ] `pyzbar` veya OpenCV WeChat QR decoder ile ID çöz
- [ ] ArUco kullanılırsa `solvePnP` ile 6-DOF pose
- [ ] QR ID → harita üzerindeki nokta eşlemesi
- **Çözünürlük hedefi:** ID 50 cm'den, pose 1 m'den ±2 cm

### G6 — Çarpışma Engelleme (+10)
- [ ] LIDAR önünde 50 cm dinamik tampon; engel varsa durağan
- [ ] Engel kalkınca 2 sn içinde devam
- [ ] Nav2 `obstacle_layer` + `inflation_layer` aktif

### G7 — Kapı Geçişi (+20)
- [ ] q5 QR noktasında dur → PLC'ye `door_request`
- [ ] PLC `door_open` mesajı bekle (timeout 30 sn)
- [ ] İzin alınca devam, GUI'de durum güncellemesi
- [ ] Dönüşte de aynı protokol

### G8 — Kullanıcı Arayüzü (+20)
Aşağıdaki bilgiler **tek ekranda erişilebilir** olmalı:
- [ ] Robot durumu (8 enum)
- [ ] Aktif görev (alma_no, bırakma_no, faz)
- [ ] Son okunan QR kod
- [ ] PLC bağlantı durumu (yeşil/kırmızı)
- [ ] PLC mesaj logu (tx/rx)
- [ ] Manuel kontrol joystick + hız barı (yalnız manuel modda)
- [ ] Acil-stop göstergesi
- [ ] Harita + canlı robot konumu
- [ ] Batarya yüzdesi (otomatik şarj için)

### G9 — Otomatik Şarj (+5)
- [ ] Batarya %20 altında → mevcut görev bitince şarj noktasına git
- [ ] Şarj noktasında dock işlemi (görsel veya manyetik temas)
- [ ] %95 olunca tekrar `idle`
