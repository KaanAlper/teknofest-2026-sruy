# Hareket-kabiliyet videosu — storyboard

Süre 2–5 dk, ≥720p, mp4 ≤50 MB, YouTube'a herkese açık. Son teslim 11 Ağustos 2026, 17:00.

Şartnamenin video için aradığı şeyler — videoda hepsinin görünür olması lazım:

1. Bilgisayardan komutla hareket
2. Çizgi takibi
3. Engelde durma
4. Senaryo icabı sağa/sola dönüş
5. Haritalama
6. GUI'nin gösterimi
7. Acil durdurma butonunun çalıştığı (tüm motorların durduğu, sistemin kapandığı)
8. Ortam sesleri duyuluyor olmalı

## Sahne planı

| Süre | Sahne | Notlar |
|---|---|---|
| 00:00–00:15 | Intro | Logo + takım adı + yarışma adı; atölyede robot tam görünüm pan |
| 00:15–00:40 | Tanıtım | Voice-over: ne yapıyor; donanım yakın çekimi (LIDAR, kamera, forklift, e-stop, anahtar) |
| 00:40–01:10 | Haritalama | "Haritala" tıklanır, robot manuel sürülür, SLAM render canlı; hızlandırılmış 4× |
| 01:10–01:40 | Komut + çizgi | GUI'den hedef gönderilir, robot çizgiye girer, kamera-overlay çizgi tespitini gösterir |
| 01:40–02:10 | Yük alma + dönüş | Forklift çatalı palet altına girer, kaldırır; ters yönde hareket, sağa döner |
| 02:10–02:40 | PLC kapı diyaloğu | GUI PLC log paneli: tx door_request → rx door_grant; robot geçer, yükü bırakır |
| 02:40–03:10 | Engelde durma | Önüne kutu konulur, robot 50 cm önce durur; kutu kaldırılır, devam eder |
| 03:10–03:30 | Acil stop | Robot hareket halindeyken e-stop basılır, motorlar durur, GUI'de banner |
| 03:30–03:50 | GUI turu | Dashboard, Map, PLC Log, Manual sayfalarının tek tek gösterimi |
| 03:50–04:30 | Bonus | Otomatik şarj (batarya %20 → dock'a yönelme), yerli motor sürücü yakın çekim, palet hizalama mekanizması |
| 04:30–05:00 | Outro | Ekip grup fotoğrafı; "TEKNOFEST Şanlıurfa, 30 Eyl – 4 Eki" yazı; GitHub linki |

## Çekim notları

- Tripod şart. Hareketli sahnelerde gimbal/stabilizer.
- Doğal ışık veya iki LED panel; gölgesiz.
- Telefon mikrofonu yetersiz, lavalier kullan.
- Her sahne için 3 alım çek, en iyisini al.

## Montaj

DaVinci Resolve veya CapCut. Aşırı geçiş efektinden kaçın — cut + light fade. Voice-over altında müzik −18 dB. Türkçe alt yazı.

## Son kontrol listesi

- [ ] Toplam süre 2:00–5:00
- [ ] Dosya boyutu ≤ 50 MB
- [ ] Çözünürlük ≥ 720p
- [ ] H.264 codec, mp4
- [ ] 8 zorunlu maddenin hepsi görünür
- [ ] Acil stop sahnesi net (motorlar duruyor)
- [ ] Ses duyuluyor
- [ ] Türkçe alt yazı
- [ ] YouTube'a herkese açık yüklendi
- [ ] Link KYS'de 11.08 17:00'dan önce kayıtlı
- [ ] Link üç ekip üyesinde yedek
