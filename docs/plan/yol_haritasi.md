# Yol haritası

Final: 30 Eylül – 4 Ekim 2026, Şanlıurfa. Bugünden sona ~19 hafta.

Sprint uzunluğu 1 hafta. Pazartesi planlama, Cuma demo + retro. Demo edilmeyen iş tamamlanmamış sayılır.

## Faz şeması

```
Mayıs           Haziran          Temmuz          Ağustos          Eylül          Ekim
└mimari       └TYF + ilk      └tam stack      └video + final   └saha test     └FİNAL
 proto         haritalama       PDR teslim       optimizasyon     + tüning
```

Kritik takvim sabitleri: 02.06 TYF, 01.07 PDR, 11.08 video, 18.08 finalist açıklama.

## Sprintler

### Sprint 1 (21–25 May) — Temel atma
- Repo, CI, ruff/mypy/pytest, docker compose iskeleti
- Domain skeleton + AsyncEventBus + birim test
- PySide6 "hello cargobot" — mock snapshot ekrana düşsün
- Donanım siparişleri: Jetson, LIDAR, RealSense, motor, batarya (2 hafta teslim)
- Ekip onboarding: README + sartname_ozeti okutulacak

### Sprint 2 (26 May – 1 Haz) — TYF teslim
- TEKNOFEST TYF şablonu indir, içeriği `docs/raporlar/TYF_iskelet.md`'den geçir
- 02.06 17:00'dan en az 24 saat önce yükle
- Şase CAD (sigma profil), motor sürücü breadboard

### Sprint 3 (2–8 Haz) — Şase + sürüş
- 05.06 TYF sonucu — gelirse iyileştirme listesi çıkar
- Şase montaj, motor + tekerlek, batarya + sigorta + e-stop kablolaması
- Jetson Ubuntu + ROS2 Humble
- STM32 firmware: PWM + enkoder
- micro-ROS köprü: `/cmd_vel` → motor, enkoder → `/odom`
- Klavye ile sürüş testi

### Sprint 4 (9–15 Haz) — LIDAR + SLAM
- LIDAR sürücüsü, `/scan` aktif
- IMU + robot_localization ile odometri fusion
- slam_toolbox online_async
- Test alanında ilk haritalama, `.pgm + .yaml` kaydet/yükle
- LIDAR adapter'i `infrastructure/lidar/` altında, `ObstacleDetected` event'ini bus'a yayar
- RouteGraph YAML serialization

### Sprint 5 (16–22 Haz) — Kamera + QR + çizgi
- RealSense aktif
- pyzbar QR, ArUco + solvePnP pose
- HSV/LAB maske + contour ile çizgi merkez ekseni
- Çizgi takip PID, `cmd_vel` üreten ayrı node
- `QrCodeDetected`, `LineDetected`, `LineLost` bus üzerinden akıyor

### Sprint 6 (23–29 Haz) — Nav2 + ilk uçtan uca
- Nav2 stack, costmap (inflation + obstacle), AMCL
- Mission state machine tam
- `pickup_saga` taslağı
- Mock PLC bir atama yollasın → robot ilk waypoint'e gitsin

### Sprint 7 (30 Haz – 6 Tem) — PDR teslim + forklift
- PDR şablonunu doldur, 01.07 17:00 deadline
- Maddi destek formu — KYS'ye gönder
- Forklift mekanizması monte (lineer aktüatör + çatal)
- Manuel pickup testi

### Sprint 8 (7–13 Tem) — PLC adapter + kapı sagası
- 10.07 PDR sonucu
- Modbus + OPC UA adapter'ler (pymodbus + asyncua)
- Yerel PLC simülatörü (pymodbus server)
- `door_saga`: q5'te dur → request → wait → grant → devam
- WebSocket sunucu, GUI PLC log paneli canlı

### Sprint 9 (14–20 Tem) — GUI tam
- Dashboard, Map, PLC Log, Manual, Settings sayfaları
- Manuel kontrol anahtar konumuna göre aç/kapan
- `test_ui_information_completeness` CI fail eşiği
- Kopan bağlantıda otomatik yeniden bağlanma
- E-stop banner

### Sprint 10 (21–27 Tem) — Saha 1.0
- Atölyede basitleştirilmiş saha
- Senaryo skripti: mock PLC pickup → kapı → dropoff → return → home
- Hata akışları: engel, PLC timeout, yanlış QR
- Otomatik şarj sagası
- 5 başarılı ardışık koşum + ros2 bag

### Sprint 11 (28 Tem – 3 Ağu) — Video çekimi
- Storyboard'a göre çekim (docs/raporlar/video_storyboard.md)
- Birden fazla alım, en iyisini seç
- Edit, alt yazı, kurum logosu

### Sprint 12 (4–10 Ağu) — Video teslim + saha 2.0
- 11.08 17:00 KYS'ye link
- Gerçek ölçekli saha, gerçek geliştirme PLC'si
- 25 dk altında bitirme hedefi
- Forklift hassasiyeti — yük düşmemesi

### Sprint 13–14 (11–24 Ağu) — Optimizasyon + tüning
- Saha tekrarı, günde 10+ koşum
- WiFi paket düşmesi simülasyonu
- PLC protokolü gelirse hızlı entegrasyon
- Yedek donanım hazır

### Sprint 15–16 (25 Ağu – 7 Eyl) — Saha hazırlığı
- Şanlıurfa lojistiği, MAC adres bildirimleri (2 gün önce)
- Acil durum drill: WiFi kopması, e-stop, yük düşmesi
- Rol matrisi netleşir: kim haritalama, kim sürüş, kim GUI

### Sprint 17–18 (8–28 Eyl) — Final provası
- Şartname şekillerine birebir saha
- Günde 20 koşum
- Sunum provası

### 30 Eyl – 4 Eki — Şanlıurfa
Saha kurulum → haritalama (60 dk) → yarışma (30 dk) → sunum.

## Özet tablo

| Sprint | Tarih | Çıktı | Risk |
|:-:|---|---|:-:|
| 1 | 21–25 May | İskelet, donanım sipariş | D |
| 2 | 26 May–1 Haz | TYF | O |
| 3 | 2–8 Haz | Şase + sürüş | O |
| 4 | 9–15 Haz | SLAM + harita | Y |
| 5 | 16–22 Haz | Kamera + QR + çizgi | O |
| 6 | 23–29 Haz | Nav2 + saga | O |
| 7 | 30 Haz–6 Tem | PDR + forklift | Y |
| 8 | 7–13 Tem | PLC entegrasyon | Y |
| 9 | 14–20 Tem | GUI tam | O |
| 10 | 21–27 Tem | Saha 1.0 | Y |
| 11 | 28 Tem–3 Ağu | Video çekim | D |
| 12 | 4–10 Ağu | Video teslim + saha 2.0 | O |
| 13–14 | 11–24 Ağu | Tüning | O |
| 15–16 | 25 Ağu–7 Eyl | Lojistik | D |
| 17–18 | 8–28 Eyl | Prova | O |
