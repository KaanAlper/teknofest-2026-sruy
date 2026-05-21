# Geçmiş yıl araştırması

## Yarışmanın seyri

Bu yarışma önceki yıllarda "Sanayide Dijital Teknolojiler" adıyla yapıldı. 2022–2023'te magnetik bant takipli AGV ile lojistik görevler vardı; **Temel** ve **İleri** olmak üzere iki kategori şeklinde işliyordu. 2024'te İleri kategoride QR kod doğrulama, harita çıkarma ve tam otonom rota gerektiği görüldü; 2025'te benzer formatta TEKNOFEST İstanbul'da düzenlendi. 2026'da isim değişti, kategori sayısı tekleşti, senaryo doğrudan **PLC entegre forklift AMR** çizgisine indi. Yani 2026 önceki yılların en zoru ve endüstriyel AMR pratiğine en yakın olanı.

Kaynaklar:
- https://www.teknofest.org/tr/competitions/competition/32
- https://cdn.teknofest.org/media/upload/userFormUpload/Sanayide_Dijital_Teknolojiler_Yarışması_Şartname_2023_v1_TMdZL.pdf
- https://yarismaduyurulari.com/teknofest-2024-sanayide-dijital-teknolojiler-yarismasi/
- https://www.kosgeb.gov.tr/site/tr/genel/detay/9285/teknofest-2025-istanbulda-sanayide-dijital-teknolojiler-yarismasinda-oduller-sahiplerini-buldu

## Önceki yarışmacıların tipik konfigürasyonu

Resmi takım donanım listesi açık paylaşılmıyor; aşağıdaki yığın geçmiş projelerin sosyal medya/haber paylaşımlarından ve sektör pratiğinden derlendi. Bizim için doğrudan referans değil, gözlem.

**Şase:** Alüminyum sigma profil 30×30 veya 40×40. Sürüş genelde diferansiyel (2 tahrik + 2 caster); bazıları mecanum tercih ediyor. Forklift mekanizması çoğunlukla çelik raylı çatal + lineer aktüatör veya scissor lift; servoyla ince ayar.

**Hesaplama:** Üst seviyede Raspberry Pi 4/5 veya NVIDIA Jetson (görüntü için Jetson tercih ediliyor). Alt seviyede STM32F4 veya ESP32. micro-ROS köprüsü yaygın.

**Sensörler:** RPLIDAR A1/A2 veya YDLIDAR X4/G4 ekonomi tarafında, Slamtec S2 üst tarafta. Logitech C920 veya Intel RealSense D435. BNO055/MPU6050 IMU. Quadrature optik enkoder.

**Yazılım:** Ubuntu 22.04 + ROS2 Humble + slam_toolbox + Nav2 + OpenCV. GUI tarafında RViz2 + custom panel kullananlar çok; PySide6/QML ile özel HMI yapan az.

## Geçmiş finalist takımlarda gözlenen başarısızlık noktaları

Sosyal medya yorumlarından çıkarılan tekrarlanan hata türleri:
- 60 dakikalık haritalama süresinin tükenmesi
- WiFi paket düşmesi → PLC timeout → görev iptali
- QR'ı yanlış açıdan okuma
- Çizgi takibinde ışık değişikliği ile başarısızlık
- Forklift çatalında konumlanma hatası → yük düşürme

Bunlar bizim risk matrisinde de kritik eşik üstü taşınıyor (`docs/plan/risk_matrisi.md`).

## Rapor şablon örnekleri

TEKNOFEST'in PDR/TYF şablonları yarışmaya özel, başvuru sonrası web sitesinde açılıyor. Format örneği için aynı vakfın başka yarışmalarının şablonlarına bakılabilir:
- https://github.com/teknofest-suruiha/suruiha/wiki/Ön-Rapor-İsterleri
- https://cdn.teknofest.org/media/upload/diger/4a33e358619ea6d84d8bdd64a5d5a96a5.pdf

> Resmi şablonlar geldiğinde `docs/raporlar/` altındaki iskeletler oraya kopyalanacak; format tutturmak puana doğrudan etki ediyor.
