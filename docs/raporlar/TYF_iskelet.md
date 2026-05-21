# Teknik Yeterlilik Formu — içerik iskeleti

Resmi TYF şablonu TEKNOFEST web sitesinden başvuru sonrası iniyor. Burası şablon gelene kadar bölüm bölüm içerik hazırlamak için. Şablonun başlık hiyerarşisi ne olursa olsun bizim hazırladığımız içerik bu sırayla ulaşılabilir olmalı.

Son teslim: **02 Haziran 2026, 17:00**.

## 1. Takım bilgileri
Takım adı, kaptan, üyeler + eğitim seviyeleri, varsa danışman, iletişim sorumlusu, T3KYS başvuru numarası.

## 2. Problemin tanımı
İmalat sanayinde iç lojistik ihtiyacı; manuel forklift operasyonlarının dezavantajları (iş kazası, esnek olmayan operasyon, vardiya bağımlılığı). Yarışma senaryosunun bu probleme doğrudan karşılığı: PLC kontrollü kapılı ortamda, rastgele atanan alma/bırakma noktalarına otonom hareket eden forklift.

## 3. Sektörel veriler
TÜİK, KOSGEB, Statista ve Allied Market Research kaynaklarından AGV/AMR pazar verisi ve Türkiye'deki dijital dönüşüm trendleri. Yerli AMR çözümlerinin sayıca azlığı → pazar boşluğu argümanı.

## 4. Çözüm yöntemi
Otonom forklift mobil robot. 2D LIDAR SLAM ile haritalama, hibrit navigasyon (rota grafı + Nav2 yerel planlayıcı), kameradan QR + ArUco + çizgi takibi, PLC ile Modbus TCP veya OPC UA üzerinden el sıkışma. Kod tabanında DDD bounded context'ler ve event bus omurgası.

## 5. Ön sistem tasarımı

**Mimari:** Detayı `docs/mimari/sistem_mimarisi.md`. Robot tarafında Jetson Orin Nano üstünde Python asyncio çekirdek + ROS2 düğümleri; operatör PC'de PySide6 + QML; aralarında WebSocket köprüsü.

**Donanım:** Detayı `docs/donanim/bom.md`. Kısaca: Jetson + STM32 + ESP32, LIDAR (YDLIDAR/RPLIDAR), RealSense D435i, LiFePO4 12.8 V 20 Ah, sigma profil şase, lineer aktüatörlü forklift.

**Yazılım yığını:** Python 3.12, ROS2 Humble, slam_toolbox, Nav2, OpenCV, PySide6 + QML, pymodbus / asyncua.

**Bounded contextler:** mission, navigation, perception, safety, fleet_io, telemetry. Detay: `docs/mimari/bounded_contexts.md`.

## 6. Bütçe

Detay: `docs/donanim/bom.md`.

| Bölüm | TL |
|---|--:|
| Hesaplama | 27.300 |
| Sensörler | 28.800 |
| Tahrik | 10.000 |
| Güç | 9.320 |
| Şase | 9.300 |
| Yardımcı | 4.800 |
| Yedek + lojistik | 22.904 |
| **Toplam** | **112.424** |

## 7. Program çizelgesi
`docs/plan/yol_haritasi.md` — sprint sprint kırılım. TYF için Mayıs–Ekim arası özet Gantt yeterli.

## 8. Risk ve karşı önlemler
`docs/plan/risk_matrisi.md` ilk 8 satır TYF formuna girer (kritik eşik üstündekiler).

## 9. Yerlilik ve özgünlük
- **Yerlilik:** Yerli üretim motor sürücü kartı (Robotsepeti yerli kartlar) veya kendi tasarım sensör hub PCB. Pardus OS opsiyonel.
- **Özgünlük:** Aktif palet hizalama mekanizması (kamera + servo), DDD/event-driven mimari, hibrit QR + ArUco pose.

## 10. Performans hedefleri

| Kriter | Hedef |
|---|---|
| Haritalama süresi | < 30 dk |
| Görev tamamlama | < 25 dk |
| Rota sapması | < 5 cm (limit 10) |
| Bölge toleransı | < 5 cm / < 3° |
| QR okuma başarısı | > 95% |
| Engel cevap süresi | < 500 ms |
| PLC mesaj RTT | < 100 ms |

## 11. Karar
Ön tasarım kararlarına dayanarak ileri tasarım fazına geçilmesi uygundur. PDR fazında mekanik CAD, PCB şematikleri ve yazılım modül diyagramları tam olarak hazırlanır.
