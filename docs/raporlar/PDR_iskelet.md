# Proje Detay Raporu — içerik iskeleti

Resmi PDR şablonu TEKNOFEST web sitesinden alınacak. Bu dosya şablon gelene kadar bölüm bölüm içerik hazırlığı.

Son teslim: **01 Temmuz 2026, 17:00**.

## 1. Yönetici özeti
Proje vizyonu, TYF'den bu yana ilerleme özeti, beklenen performans hedefleri.

## 2. Analiz

**Problem tanımı** — TYF'deki tanım + bu süreçte ortaya çıkan ek bulgular.

**Paydaşlar** — TEKNOFEST jürisi, saha hakem heyeti, yarışma operatörü ekibimiz, son kullanıcı tarafında imalat sanayi.

**Kullanıcı senaryosu** — Yarışma senaryosu adım adım, `docs/mimari/sekanslar.md` S4'ten alıntı.

## 3. Tasarım

**Sistem mimarisi:** DDD bounded context'ler, event bus omurgası, iki süreçli mimari (robot + operatör PC). Detay: `docs/mimari/sistem_mimarisi.md`, `docs/mimari/eventbus.md`.

**Donanım:** Şase CAD görselleri, forklift mekanizması detay çizimleri, güç dağıtım şeması, e-stop devresi, sensör yerleşimi.

**Yazılım modülleri:** Klasör ağacı + bağımlılık yönleri (`docs/mimari/dizin_haritasi.md`), kritik sınıf diyagramları, sequence diyagramları.

**Algoritmalar:**
- SLAM seçimi: slam_toolbox (online async); Cartographer alternatif olarak değerlendirilip elendi (Humble + entegrasyon kolaylığı).
- Yol planlama: rota grafı (Dijkstra) üzerine Nav2 yerel planlayıcı.
- Çizgi takibi: HSV maske + contour + PID; ışık değişiminde LAB color space yedeği.
- QR + ArUco hibrit pose: QR ile node ID, ArUco ile mm doğruluğunda pose düzeltme.
- Otomatik şarj sagası: batarya eşik altı → mevcut görevi tamamla → dock'a yönel.

## 4. Geliştirme

**Ortam:** Git + GitHub Actions CI, Docker compose (PLC sim + cargobot + Gazebo), uv ile bağımlılık yönetimi.

**Standartlar:** Black, ruff, mypy strict, pytest. Test-first; her bounded context için unit + integration testleri.

**İlerleme kanıtları:** Sprint 1-7 çıktıları, atölye test videoları, GitHub repo aktivite özeti, kod kapsama raporu.

## 5. Test

`docs/test/test_stratejisi.md` özet. Birim test kapsama hedefi domain için %90+. Entegrasyon test sonuçları, saha denemesi özetleri, performans ölçüm tabloları.

## 6. Uygulama / entegrasyon

ROS2 köprü, PLC adapter, GUI bağlantı sırası. Robot systemd service, GUI bilgisayar, ağ ayarı. Şanlıurfa lojistik planı, MAC bildirimi, yedek donanım planı.

## 7. Proje yönetimi

**Bütçe detayı** — BOM özet + tedarikçi listesi + maddi destek başvurusu.

**Program** — Sprint geriye dönük + ileriye plan.

**Risk** — `docs/plan/risk_matrisi.md` son hali.

**Kapsam** — Şu an dahil/hariç tutulan özellikler. Stretch goal'lar (otomatik şarj, yerlilik PCB).

## 8. Yerlilik ve özgünlük detayı

**Yerli bileşenler:** Liste + üretici + sertifika; BOM içinde yerlilik oranı.

**Özgün tasarımlar:** Aktif palet hizalama mekanizması teknik açıklama, DDD/event-driven mimari, hibrit QR + ArUco algoritması matematiği.

## 9. Sonuç ve ileri plan

G1-G10 görevlerinin durumu, kalan riskler, sonraki 6 hafta önceliği.

## 10. Ekler

- Şematikler (PDF)
- CAD render'ları
- Kod örnekleri
- Saha test video linkleri (YouTube unlisted)
- Açık kaynak lisans listesi

> Sayfa numarası, başlık hiyerarşisi, içindekiler, kurum/takım logosu, kenar boşlukları TEKNOFEST'in PDR şablonuna birebir uyacak.
