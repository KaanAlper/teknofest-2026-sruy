# 2026 SRUY Şartname Özeti

> Kaynak: `docs/sartname/2026_SRUY_TR.txt` (PDF'den dönüştürülmüş, 23 sayfa, v1.0 — 05.05.2026)

## 1. Yarışmanın Amacı
TEKNOFEST **Sanayide Robotik Uygulamalar Yarışması (SRUY)**: fabrika içi lojistikte veya depoda yollarda hareket eden, belirli yükleri noktadan noktaya taşıyan **otonom forklift mobil robot** geliştirmek. Yerli ve milli üretimin teşvik edildiği, dijitalleşme odaklı bir yarışma.

## 2. Katılım Koşulları
- Lise + üniversite öğrencileri ve mezunlar (mezuniyetten en fazla 3 yıl)
- Takım: **3–15 kişi** + en fazla 1 danışman
- Üniversite seviyesinde danışman zorunlu değil
- Bir kişi yalnızca tek bir takımda yer alabilir
- Aynı proje sadece bir yarışmaya/kategoriye başvurabilir
- Başvuru: **20 Mayıs 2026** — `www.t3kys.com` / `www.teknofest.org`

## 3. Yarışma Kategorisi
**Tek kategori.** Forklift otonom mobil robot, palet üzerindeki sembolik yükü (max **5 kg**) tanımlanmış rotalardan takip ederek alma → bırakma noktasına taşır.

## 4. Yarışma Takvimi

| Tarih | Aşama |
|---|---|
| 20 May 2026 | Son başvuru |
| 02 Haz 2026 — 17:00 | Teknik Yeterlilik Formu (TYF) son teslim |
| 05 Haz 2026 | TYF sonuçları |
| 01 Tem 2026 — 17:00 | Proje Detay Raporu (PDR) son teslim |
| 10 Tem 2026 | PDR sonuçları |
| 11 Ağu 2026 — 17:00 | Hareket-Kabiliyet Videosu son teslim |
| 18 Ağu 2026 | Finalist açıklama |
| Ağu–Eyl 2026 | Yarışma finalleri |
| 30 Eyl – 4 Eki 2026 | TEKNOFEST Şanlıurfa |

## 5. Wifi Ağı Düzeni
- İki ayrı yerel ağ (internet **yok**): `YARISMA DENEME AGI` (deneme) ve `YARISMA AGI` (yarışma).
- Her ağa **iki cihaz** bağlanabilir: forklift robot + takip/monitör bilgisayarı.
- MAC adres filtreleme ile erişim kontrolü. MAC'ler yarışmadan 2 gün önce bildirilmeli.
- Deneme süresi takım başına **30 dk** (rezervasyonlu).

## 6. Fiziksel Kısıtlar
- **Yük:** sembolik, max 5 kg, palet üzerinde
- **Robot ölçüleri:** Şekil-3'te tanımlı maksimum (PDF görseli — netleştirilmeli)
- **Rota sapması:** max **±10 cm**
- **Hedef bölge toleransı:** konum **±7.5 cm**, yön **±5°**
- **Acil stop:** zorunlu (manyetik veya döndürmeli)

## 7. Süre ve Senaryo Akışı
1. Saha öncesi **60 dk** haritalama + rota tanımlama hakkı
2. Robot başlangıç alanında bekler, WiFi'ye bağlanır
3. PLC'den rastgele 1 alma noktası + 1 bırakma noktası gelir
4. Robot rotayı kendisi optimize eder, yük alma noktasına gider
5. Yük alma/bırakma noktalarından 1.5 m önce **renkli şerit + QR kod** vardır → görüntü işleme ile hassas pozisyon
6. Yük alındıktan sonra ters yönde (yük arkada) hareket
7. q5 QR kod noktasında durur, PLC'ye kapı isteği gönderir
8. PLC "geç" der → robot devam eder, yükü bırakır, PLC'ye bildirir
9. Dönüşte de kapı diyaloğunu tekrarlar, bekleme noktasına döner
10. **30 dk** içinde tamamlanması beklenir, **45 dk** üst limit

## 8. Görev Kataloğu (3.1.1)
| # | Görev | Notlar |
|---|---|---|
| 1 | Haritalama | 2D lazer alan tarayıcı (LIDAR) ile |
| 2 | Rota tanımlama | Arayüz üzerinden |
| 3 | PLC haberleşme | Protokol takımlara sonradan iletilecek |
| 4 | Görüntü ile çizgi takibi | Yük noktasından 1.5 m önce renkli şerit |
| 5 | QR kod okuma + pose hesabı | Kameraya göre konum çıkar |
| 6 | Engelden güvenli durma | Engel kalkınca devam et |
| 7 | Rota sapması ≤ 10 cm | Aşılırsa ceza |
| 8 | Bölge toleransı | ±7.5 cm / ±5° |
| 9 | PLC kontrollü kapı geçişi | İstek/izin protokolü |
| 10 | Kullanıcı arayüzü | Durum, görev, QR, PLC mesajları, manuel kontrol |

## 9. Arayüz Zorunlu Bilgileri
Aşağıdaki bilgilerin GUI'de **tamamı** görünmek zorunda (eksik her bilgi −4 puan):
- Robot durumu: `idle / işleniyor / yüksüz hareket / yüklü hareket / PLC komut bekleniyor / dönüş / hata / acil-stop`
- Görev durum bilgisi
- Okunan QR kod bilgisi
- PLC haberleşme durumu + alınıp verilen mesajlar
- Manuel uzaktan kontrol (yalnız **anahtar "manuel" konumdayken** aktif)

## 10. Puanlama (Final, %70)

| Kriter | Puan |
|---|---|
| Sunum | +10 |
| Haritalama | +30 |
| Rota hazırlama | +20 |
| Fabrika otomasyon haberleşme | +20 |
| Görüntü ile çizgi takibi | +10 |
| QR kod okuma | +10 |
| Çarpışma engelleme | +10 |
| Kontrollü kapı geçişi | +20 |
| Kullanıcı arayüzü (tüm bilgilerle) | +20 |
| Tanımlı görevi tamamlama | +30 |
| Erken bitirme (her dk) | +1 |
| Yerlilik | +5 |
| Özgünlük | +5 |
| **Otomatik şarj kabiliyeti** | +5 |
| Rota sapması | −5 (max 2 kez) |
| Bölge toleransı dışı | −5 (max 2 kez) |
| GUI'de eksik her bilgi | −4 |
| Geç bitirme (her dk) | −1 |

> Ceza puanları **her biri en fazla 2 kez** uygulanır. Örn. yük 2 defadan fazla düşürülürse parkur **başarısız**.

## 11. Rapor & Video Puanlaması (%30)
- **Proje Detay Raporu (PDR):** %15
- **Hareket – Kabiliyet Videosu:** %15
  - YouTube'a "herkese açık" yüklenecek (max 50 MB, 720p, 2-3 dk min, 5 dk max)
  - İçermesi gerekenler: bilgisayardan komut → hareket, çizgi takibi, engelde durma, sağa/sola dönüş, haritalandırma, GUI gösterimi, e-stop testi

## 12. Saha Kuralları
- Parkurda **en fazla 2 takım üyesi**
- Danışman **parkur ve kontrol masasında yasak**
- Yeşil bayrak = aşama tamam, kırmızı bayrak = hata
- Müdahale yasağı; kontrol paneline izleme dışında dokunma yok

## 13. Ödüller
| Derece | Takım | Danışman |
|---|---|---|
| Birinci | ₺250.000 | ₺20.000 |
| İkinci | ₺200.000 | ₺15.000 |
| Üçüncü | ₺150.000 | ₺12.000 |

Ek prestij ödülleri: **En Özgün Tasarım**, **En İyi Sunum**.

## 14. Kritik "Dikkat" Notları
1. **Haritalama + rotalama tamamlanamayan takım sonraki adıma geçemez** → fail-fast.
2. PLC protokolü ön aşamayı geçen takımlara **sonra** iletilecek (büyük olasılıkla Modbus TCP veya OPC UA — esnek soyutlama tutulmalı).
3. Şekil-2/3/4/5 PDF görselleri PDF'den metin olarak çıkmadı. **Şartname görsellerini ayrı taramak gerek** (rota şekli, ölçü detayları).
4. **MAC filtreleme** → cihazların MAC adreslerini son haftada netleştir, yedek bilgisayar al.
5. Otomatik şarj +5 puan — sürede sıkıntı yoksa **muhakkak yapılmalı**.
6. Yerlilik & Özgünlük her biri +5 → yerli motor sürücü kartı, özgün forklift mekanizması iyi fırsat.
