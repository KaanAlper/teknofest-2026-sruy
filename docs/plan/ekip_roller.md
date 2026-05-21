# Ekip Rolleri ve Çalışma Düzeni

> Takım: en az 3, en fazla 15 kişi (şartname). Önerilen optimal: **6–8 kişi**.

## Önerilen Roller

| Rol | Sayı | Ana Sorumluluk |
|---|:-:|---|
| **Takım Kaptanı** | 1 | Proje yönetimi, TEKNOFEST iletişim, ekip koordinasyon |
| **Yazılım Lideri (Domain)** | 1 | DDD mimari, çekirdek Python kod, event bus, sagalar |
| **Robotik Mühendisi** | 1 | ROS2, Nav2, SLAM, motor sürücü, ROS2 ↔ domain köprü |
| **Görüntü İşleme Uzmanı** | 1 | OpenCV, QR/ArUco, çizgi takibi, kamera kalibrasyon |
| **Frontend / QML Geliştirici** | 1 | PySide6 + QML arayüz, WebSocket bağlantı |
| **Donanım / Mekanik** | 1–2 | Şase CAD, montaj, kablolama, forklift mekanizması, e-stop |
| **Test / Saha** | 1 | Saha kurulumu, otomatik test senaryoları, video çekim |
| **Danışman** (opsiyonel ünideki) | 1 | Akademik yön, kritik gözden geçirme |

> 6 kişi minimum sürdürülebilir. Aynı kişi birden fazla rol alabilir (örn. Domain Lideri + QML).

## Yedek Rol Matrisi

| Birincil rol kişi yoksa | Yedek |
|---|---|
| Domain Lideri | Robotik Mühendisi |
| Robotik Mühendisi | Domain Lideri |
| Görüntü | Robotik veya Domain |
| QML | Domain (eski temel Python yeterli) |
| Mekanik | Donanım |
| Test/Saha | Takım Kaptanı |

> En az **2 kişi sahaya gidebilir** olmalı (şartname parkurda max 2 kişi).

## Çalışma Ritmi

| Etkinlik | Sıklık | Süre |
|---|---|---|
| Pazartesi planlama | Haftalık | 30 dk |
| Günlük standup | Hafta içi her gün | 10 dk |
| Cuma demo + retro | Haftalık | 60 dk |
| Sprint review (orta-ay) | İki haftada bir | 90 dk |
| Risk matrisi gözden geçirme | Haftalık (Cuma) | 15 dk |
| Saha pratiği | Haziran sonundan itibaren haftada 2 gün | — |

## Karar Verme

- **Teknik kararlar:** İlgili rol sahibi karar verir, ekibe duyurur. İtiraz olursa Kaptan + Yazılım Lideri arabuluculuk.
- **Mimari kararlar:** Yazılım Lideri yazar, mini-RFC olarak `docs/mimari/decisions/` altına koyar, 48 saat itiraz penceresi.
- **Bütçe / dış iletişim:** Kaptan tek sorumlu.
- **Acil saha kararı (yarışma günü):** Kaptan + saha lideri çiftli karar.

## Onboarding Akışı (Yeni Üye)

1. `README.md` → projeyi anla
2. `docs/sartname/sartname_ozeti.md` → yarışmayı anla
3. `docs/mimari/sistem_mimarisi.md` → mimariyi anla
4. `docs/mimari/bounded_contexts.md` → kendi context'ini bul
5. `docs/plan/yol_haritasi.md` → mevcut sprint'i öğren
6. İlk PR: küçük bir bugfix veya test ekleme

## İletişim Kanalları

- **Acil + günlük:** Discord/Slack server, `#general` `#yazilim` `#donanim` `#saha`
- **Karar + uzun mesaj:** GitHub Issues / Discussions
- **Saha günü:** Telefon + walkie talkie

## Performans Beklentisi

- En az **8 sa/hafta** taahhüt (öğrencilerle uyumlu)
- Kritik haftalarda (PDR, video, final) **15-20 sa/hafta**
- Cuma demosuna gelmemek = sprint başarısız sayılır
