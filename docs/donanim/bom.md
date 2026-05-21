# Donanım Listesi (BOM) — CargoBot v0.1

> Fiyatlar yaklaşık (Mayıs 2026 TL, Robotistan/Direnc/Robotsepeti ortalaması). Yedek %20 stoklayın.

## A — Hesaplama / Kontrol

| # | Parça | Adet | Birim ≈ | Toplam ≈ | Not |
|:-:|---|:-:|--:|--:|---|
| A1 | NVIDIA Jetson Orin Nano 8 GB Dev Kit | 1 | ₺18.000 | ₺18.000 | Görüntü işleme ana SBC |
| A2 | Raspberry Pi 5 8 GB (yedek/GUI tarafı) | 1 | ₺4.500 | ₺4.500 | Operatör tarafı için |
| A3 | NVMe SSD 256 GB (M.2 → Jetson) | 1 | ₺1.500 | ₺1.500 | Hızlı disk |
| A4 | STM32F4 Discovery / Black Pill | 2 | ₺900 | ₺1.800 | Motor kontrol MCU + e-stop |
| A5 | ESP32 DevKit | 2 | ₺250 | ₺500 | Sensör hub / WiFi yedek |
| A6 | USB Hub 4-port (USB 3.0) | 1 | ₺400 | ₺400 | Sensör bağlantıları |
| A7 | Endüstriyel WiFi modülü (USB) | 1 | ₺600 | ₺600 | Saha WiFi'a güçlü bağlantı |

## B — Sensörler

| # | Parça | Adet | Birim ≈ | Toplam ≈ | Not |
|:-:|---|:-:|--:|--:|---|
| B1 | YDLIDAR G4 / RPLIDAR A2M12 | 1 | ₺9.000 | ₺9.000 | 2D LIDAR, ≥12 m |
| B2 | Intel RealSense D435i | 1 | ₺15.000 | ₺15.000 | Renkli + derinlik kamera |
| B3 | Logitech C920 (yedek mono kamera) | 1 | ₺2.000 | ₺2.000 | Çizgi takibi yedek |
| B4 | BNO055 IMU | 1 | ₺900 | ₺900 | Yön bilgisi (fusion) |
| B5 | Optik enkoder (motor başına) | 2 | ₺800 | ₺1.600 | Odometri |
| B6 | Bumper switch (4 köşe) | 4 | ₺50 | ₺200 | Çarpma yedek koruma |
| B7 | Ultrasonik HC-SR04 (forklift) | 2 | ₺50 | ₺100 | Palet yaklaşma |

## C — Tahrik / Motor

| # | Parça | Adet | Birim ≈ | Toplam ≈ | Not |
|:-:|---|:-:|--:|--:|---|
| C1 | 12V DC redüktörlü motor (50 RPM, ≥10 kg.cm) | 2 | ₺1.500 | ₺3.000 | Diferansiyel tahrik |
| C2 | Motor sürücü kart (örn. Cytron MD20A) | 2 | ₺1.200 | ₺2.400 | 20A çift kanal |
| C3 | Caster tekerlek 4" çift | 1 | ₺400 | ₺400 | Arka destek |
| C4 | Tahrik tekerleği 6" lastikli | 2 | ₺600 | ₺1.200 | Çekiş + tutuş |
| C5 | Lineer aktüatör 100 mm 12V | 1 | ₺2.500 | ₺2.500 | Forklift çatal kaldırma |
| C6 | Servo motor MG996R (forklift ince ayar) | 2 | ₺250 | ₺500 | Çatal açısı |

> **Yerlilik notu:** Motor sürücü kartını yerli üretim (örn. Anadolu Motor veya Robotsepeti yerli kartlar) seçmek **+5 yerlilik puanı** sağlar. Kendi PCB tasarımınızı da yerlilik kapsamında sayabilirsiniz.

## D — Güç

| # | Parça | Adet | Birim ≈ | Toplam ≈ | Not |
|:-:|---|:-:|--:|--:|---|
| D1 | LiFePO4 batarya 12.8V 20Ah | 1 | ₺6.000 | ₺6.000 | Güvenli kimya |
| D2 | BMS 14.6V 20A | 1 | ₺500 | ₺500 | Hücre dengeleme |
| D3 | DC-DC çevirici 12V→5V 5A (Pi/Jetson) | 1 | ₺350 | ₺350 | Sabit besleme |
| D4 | DC-DC çevirici 12V→19V (Jetson opsiyonel) | 1 | ₺400 | ₺400 |  |
| D5 | Acil stop butonu (mantar başlı, NC) | 1 | ₺250 | ₺250 | Şartname zorunlu |
| D6 | Anahtar (3 konum: AUTO/OFF/MANUAL) | 1 | ₺120 | ₺120 | Şartname zorunlu |
| D7 | Şarj soketi + dock kontakları (otomatik şarj için) | 1 | ₺500 | ₺500 | +5 puan |
| D8 | Sigorta + sigorta yuvası (20A, 5A) | 4 | ₺50 | ₺200 |  |
| D9 | Kablo seti (silikon 14AWG/22AWG) | — | — | ₺600 |  |
| D10 | Klemens + JST konektör seti | — | — | ₺400 |  |

## E — Şase / Mekanik

| # | Parça | Adet | Birim ≈ | Toplam ≈ | Not |
|:-:|---|:-:|--:|--:|---|
| E1 | Alüminyum sigma profil 30×30 (1 m) | 6 | ₺250 | ₺1.500 | Şase iskelet |
| E2 | T-bağlantı, köşebent, vida seti | — | — | ₺600 |  |
| E3 | Alüminyum levha 3 mm (taban) | 1 | ₺800 | ₺800 | Elektronik tablası |
| E4 | Çelik forklift çatalı (özel kesim) | 2 | ₺1.500 | ₺3.000 | **Özgün tasarım fırsatı** |
| E5 | Lineer ray + araba (forklift kızak) | 1 set | ₺2.000 | ₺2.000 | Hassas yük taşıma |
| E6 | PLA filament (parça üretim) | 2 | ₺500 | ₺1.000 | 3D baskı parçaları |
| E7 | Sensör tutucu printler / lazer kesim | — | — | ₺400 |  |

> **Özgünlük notu:** Forklift mekanizmasının ince tasarımı (örn. çatal dönüş, otomatik palet hizalama görsel besleme) **+5 özgünlük puanı** için en güçlü aday.

## F — Yardımcı / Geliştirme

| # | Parça | Adet | Birim ≈ | Toplam ≈ | Not |
|:-:|---|:-:|--:|--:|---|
| F1 | Mini PLC + röle modül (geliştirme) | 1 | ₺1.500 | ₺1.500 | Yarışma PLC simülatörü |
| F2 | Endüstriyel ethernet switch 5-port | 1 | ₺500 | ₺500 | Geliştirme ağı |
| F3 | QR/ArUco baskı malzemesi (vinyl/lamine) | — | — | ₺300 |  |
| F4 | Renkli şerit (sahaya benzer) | 1 rulo | ₺200 | ₺200 |  |
| F5 | Test mat / zemin malzeme | — | — | ₺800 |  |
| F6 | Multimetre, lehim seti, basit el aletleri | — | — | ₺1.500 |  |

## Toplam Bütçe

| Bölüm | Yaklaşık |
|---|--:|
| A — Hesaplama | ₺27.300 |
| B — Sensörler | ₺28.800 |
| C — Tahrik | ₺10.000 |
| D — Güç | ₺9.320 |
| E — Şase / Mekanik | ₺9.300 |
| F — Yardımcı | ₺4.800 |
| **Ara toplam** | **₺89.520** |
| Yedek/sarf (%20) | ₺17.904 |
| Kargo + ithalat | ₺5.000 |
| **TOPLAM TAHMİNİ** | **₺112.424** |

> **TEKNOFEST maddi destek** PDR sonrasında başvurulabilir — büyük olasılıkla bütçenin önemli bir kısmı karşılanır.

## Yerlilik Hedefi (en az 1 kalem)
- Tercih sırası:
  1. **Yerli üretim motor sürücü kartı** (en yüksek görünürlük)
  2. **Yerli işletim sistemi (Pardus)** — yazılım yerliliği
  3. **Kendi tasarım PCB** (sensör hub, e-stop bus board)
  4. **Yerli LiFePO4 batarya paketi**

## Özgünlük Hedefi (en az 1 kalem)
- Tercih sırası:
  1. **Aktif palet hizalama mekanizması** — kamera + servo ile çatal pozisyon düzeltme
  2. **Sürüm-kuralı RouteDSL** (yarışmaya özel rota tanımlama dili)
  3. **Hibrit QR + ArUco pose fusion algoritması**
  4. **DDD bounded context'li mimari** (yarışmacılar arasında çok nadir görülen seviye)

## Kritik Tedarik Süresi Notları
- Jetson Orin Nano: Türkiye'de stoğu sınırlı; **2 hafta önce sipariş**
- RealSense D435i: Genellikle yurt dışı; **3-4 hafta**
- LiFePO4 batarya: Yerli stok varsa 1 hafta; sertifikalı/güvenli olanı tercih et
