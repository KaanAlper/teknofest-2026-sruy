# Risk Matrisi

> Risklerin **olasılık × etki** çarpımı üzerinden önceliklendirilmesi ve **azaltıcı eylem** planlaması.

## Olasılık / Etki Skalası

- Olasılık: 1=Çok Düşük, 2=Düşük, 3=Orta, 4=Yüksek, 5=Çok Yüksek
- Etki: 1=İhmal edilebilir, 2=Düşük, 3=Orta, 4=Yüksek, 5=Kritik (yarışma kaybı)
- Skor = O × E (>12 = kritik)

## Risk Kayıt Defteri

| ID | Risk | O | E | Skor | Sahip | Azaltıcı Eylem |
|:-:|---|:-:|:-:|:-:|---|---|
| **R1** | PLC protokol detayı geç gelir, entegrasyon zaman almaz | 4 | 5 | **20** | Yazılım | Modbus + OPC UA + raw TCP **üç adapter** önceden hazır; switching env değişkeniyle |
| **R2** | Yarışma alanında WiFi paket düşmesi → PLC timeout | 4 | 4 | **16** | Yazılım | Heartbeat + yeniden bağlanma + 30 sn buffer; saha 2.0 sahnesinde test |
| **R3** | Forklift yük 2'den fazla düşme → diskalifiye | 3 | 5 | **15** | Mekanik | Çatal hassasiyeti + görsel hizalama + alt limit switch + saha tekrarı |
| **R4** | Haritalama 60 dk içinde tamamlanmaz | 3 | 5 | **15** | Algı | Önceden saha planı çalış; manuel sürüş yetkin; slam_toolbox parametre tüne |
| **R5** | Jetson/donanım tedariki gecikir | 3 | 4 | **12** | PM | 2 hafta önce sipariş; Raspberry Pi 5 yedek; Türkiye stoğu olan satıcı |
| **R6** | E-stop testi başarısız → güvenlik puanı kaybı | 2 | 5 | **10** | Donanım | Buton mekanik test; yazılım E-stop + donanım E-stop bağımsız; demo videoda göster |
| **R7** | Sahada ışık değişimi → çizgi takibi başarısız | 4 | 3 | **12** | Algı | HSV yerine LAB color space; adaptive threshold; ArUco hibrit |
| **R8** | QR yanlış açıdan okunamaz | 3 | 3 | **9** | Algı | ArUco yedek; çoklu kare birleştirme; daha yüksek çözünürlük |
| **R9** | Ekip içi iletişim kopukluğu / üye ayrılması | 3 | 4 | **12** | PM | Haftalık standup + Cuma demo; herkesin yedek rolü; dokümantasyon disiplin |
| **R10** | Batarya bitmesi yarışma esnasında | 2 | 5 | **10** | Donanım | Otomatik şarj (+5 puan da kazanır); yedek paket; başlangıç %100 |
| **R11** | ROS2 + PySide6 köprü stabilite sorunu | 3 | 3 | **9** | Yazılım | Köprü erken kurulup uzun süre koşturulur; WebSocket alternatifi |
| **R12** | Sahada başka WiFi parazit | 4 | 3 | **12** | Donanım | 5 GHz öncelikli; harici USB WiFi modülü; MAC filtreleme yedek |
| **R13** | TYF/PDR raporu kabul edilmez | 2 | 5 | **10** | Yazma | Şablonu birebir takip; örnek raporlardan kalite kontrol; teslimi 24 saat erken yap |
| **R14** | Şanlıurfa kargolama hasarı | 2 | 5 | **10** | Lojistik | Sağlam ahşap kasa; flight case; sigorta; el bagajı kritik parçalar |
| **R15** | Yarışma günü hastalık (ekip kişisi) | 2 | 3 | **6** | PM | Yedek rol; en az 4 kişi sahaya gider |
| **R16** | Acil durdurma anahtarı yanlış kullanım | 2 | 4 | **8** | Operasyon | Saha denemesinde drilli; rol matrisi net |
| **R17** | Yerlilik/Özgünlük puanı alınamaz | 3 | 2 | **6** | Mekanik+Yazılım | Yerli motor sürücü + özgün forklift mekanizması + DDD mimari belgeleri |
| **R18** | Maddi destek başvuru reddedilir | 3 | 3 | **9** | PM | Bütçenin %30'unu sponsorluk/kişisel kaynaktan planla |

## Kritik Eşik Üstü (>12) — Haftalık İzleme

| ID | Mevcut Durum | Sonraki Adım |
|:-:|---|---|
| R1 | 3 adapter şablon hazır (sprint 8) | Sprint 7'de yerel PLC sim üzerinde mock test |
| R2 | Yeniden bağlanma kodu yok | Sprint 8 PLC adapter ile birlikte ekle |
| R3 | Mekanik tasarım taslakta | Sprint 7'de aktüatör monte sonrası saha drilli |
| R4 | SLAM henüz kurulmadı | Sprint 4'te ilk saha denemesi |
| R5 | Sipariş bekleniyor | Sprint 1'de **acil** sipariş; takip Cuma |
| R7 | Çizgi takibi yok | Sprint 5'te farklı ışık koşullarında test |
| R9 | Ekip yeni kuruluyor | Sprint 1'de roller netleşmeli, CLAUDE.md gibi onboarding |
| R12 | WiFi test edilmedi | Sprint 8'de USB WiFi sipariş |

## Risk Gözden Geçirme Ritmi
- **Cuma** demosunda her sprint risklerin yeniden puanlanması
- **Ayda 1** komple matrisi güncelle, yeni riskleri ekle
- **Skor düşmediyse** azaltıcı eylem yeterli olmamış demektir, agresif önlem
