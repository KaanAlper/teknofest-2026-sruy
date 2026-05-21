# Teknik stack ve topluluk araştırması — 2026

Bu doküman: TEKNOFEST SRUY 2026 ve dünya AGV/AMR yarışmalarının yazılım yığınlarının derinlemesine analizi. Kararlarımız + alternatifler + kaynak linkleri.

## 0. Yarışma doğrulaması

Resmî sayfa: https://www.teknofest.org/tr/yarismalar/sanayide-robotik-uygulamalar-yarismasi/

- 2021-2025 arası "Sanayide Dijital Teknolojiler" (SDT) adıyla; 2026'da "Sanayide Robotik Uygulamalar" (SRUY) — yeniden adlandırma + forklift odağı netleşti
- Takvim: Son başvuru **31.05.2026**, TYF 02.06, PDR 01.07, HKV 11.08, Final 30 Eyl-4 Eki 2026 Şanlıurfa
- Ödüller: 1.lik 250.000 TL · 2.lik 200.000 TL · 3.lük 150.000 TL
- Değerlendirme: TYF → PDR → HKV → Final. **PDR ve HKV jüriye yazılı/görsel iletildiği için anlatım kalitesi saha kadar önemli** — Foxglove kayıtları, mimari diyagramlar yatırıma değer

## 1. Geçmiş takımlar (2021-2025)

| Yıl | Temel/İleri | Birinci | İkinci | Üçüncü |
|---|---|---|---|---|
| 2021 | Temel | ROBOMOSB | HAFIZ İHO STEAM 4.0 | ÇOROBOT |
| 2022 | Temel/İleri | ROBOMOSB / YİĞİDO | leblebiler / ÇOROBOT-SDT | NİLÜFER ROBOTİK / KOU ROVER |
| 2023 | Temel/İleri | RoboMosb / MarCO | Batarya / İPEK YOLU OTONOM | ALPLEREN / YİĞİDO-AGV |
| 2024 | Temel/İleri | Batarya / KILAVUZ KOU ROVER (M1) | ROBOMOSB / İPEK YOLU (M2) | Afas (M3) / WIND |
| 2025 | Temel/İleri | NİLÜFER ROBOTİK / KILAVUZ KOU ROVER | Stratus / YİĞİDO | Bilim Konya-Quetzal / RACLAB KAPSÜL |

**İzlenmesi gereken takımlar:** KILAVUZ KOU ROVER (Kocaeli Üni, 2 yıl üst üste İleri 1.), YİĞİDO (Sivas Cumhuriyet), İPEK YOLU OTONOM, ROBOMOSB.

**Kritik gözlem:** 2024-2025'te birçok derece "Mansiyon" (M1/M2/M3) olarak verildi → jüri "tam birinci yok" diyebiliyor → **demo başarısızlığı çok ağır cezalı**. Sahada güvenli koşum > spektaküler ama riskli özellikler.

**Github tarama:** Takım repoları kapalı, kaynak ödünç alınamıyor. **PDR/video kalitesi sahaya kadar belirleyici.**

## 2. Dünya AGV/AMR yarışmaları

### RoboCup Logistics League (RCLL) — SRUY'a en yakın eşdeğer
- https://ll.robocup.org/
- Şampiyon: **Carologistics (RWTH Aachen)** — https://github.com/carologistics
- Stack: **Fawkes** (custom C++ middleware, ROS değil) + **CLIPS** kural motoru + **OpenPRS** planlama
- **Bizim için:** Doğrudan kopyalanmaz; ama CLIPS-tarzı kural tabanlı görev orkestrasyonu mantığı iyi → **BehaviorTree.CPP** ile mission tree

### RoboCup@Work — KUKA youBot ile parça toplama
- En aktif: **b-it-bots (Bonn-Rhein-Sieg)** — https://github.com/b-it-bots/mas_industrial_robotics
- ROS Noetic ağırlıklı, ROS2 geçişinde. **smach state machine + perception_pipeline ayrımı** mimari olarak güzel.

### ARIAC (NIST)
- https://github.com/usnistgov/ARIAC
- ROS2 + Gazebo, Python/C++. `ariac2025` branch aktif
- **ariac_plugins** + **ariac_interfaces** mesaj/aksiyon tanımları PDR'da "fabrika otomasyon protokolü" tasarımına şablon
- **Karar:** Denenmeli — kendi sim'imizi kurmadan ARIAC docker ile Nav2 entegrasyonunu deneyimle

## 3. Endüstri standartları

### Open-RMF (Robotics Middleware Framework)
- https://github.com/open-rmf/rmf · Kitap: https://osrf.github.io/ros2multirobotbook/
- Çoklu filo orkestrasyonu, trafik çizelgeleme, **kapı/asansör entegrasyonu**: `rmf_door_msgs`, `rmf_lift_msgs` — şartnamede tam karşılığımız
- Tüm RMF'i kurmaya gerek yok (tek robotluyuz); **mesaj şemasını taklit etmek jüride "endüstri standardı" puanı**

### VDA 5050 v3.0 — Master-control ↔ AGV protokolü
- https://github.com/VDA5050/VDA5050
- MQTT 3.1.1 + JSON. Topic: `interfaceName/majorVersion/manufacturer/serialNumber/topic`
- Mesajlar: `order`, `state`, `connection`, `visualization`, `instantActions`, `factsheet`
- **PLC'nin yerini almaz** ama SRUY'da "fabrika otomasyon sisteminden gelen görev bilgisi" tam olarak VDA 5050 `order` mesajı
- **Karar:** Master-control simülasyonunda VDA 5050 JSON şemasını kullan. Gerçek PLC için Modbus/OPC UA ayrı katman. İki katmanlı mimari PDR'de güçlü.

### NVIDIA Isaac ROS — Jetson Orin Nano için kritik
- https://nvidia-isaac-ros.github.io/
- **isaac_ros_visual_slam (cuVSLAM):** 250 fps Jetson lokalizasyon — 2D LIDAR SLAM'i bypass etmez ama yedek
- **isaac_ros_apriltag:** GPU hızlandırılmış AprilTag, yüksek FPS — **denenmeli** (CPU AprilTag yetersizse)
- **isaac_ros_nitros:** zero-copy GPU mesajlaşma — RealSense + YOLO + AprilTag aynı boruda

## 4. SLAM / Navigasyon kararı

| Çözüm | 2D LIDAR + Diff Drive | Humble desteği | Karar |
|---|---|---|---|
| **slam_toolbox** | ✓✓✓ | Native, aktif | **KULLAN** — mapping mode harita çıkar, localization mode'da koş |
| Cartographer | ✓ | Bakımsız | Atla |
| RTAB-Map | RGBD overkill | Native | Atla — 2D LIDAR ile yeterli |
| LIO-SAM / HDL-Graph | 3D LIDAR | — | Atla — 3D LIDAR yok |

**slam_toolbox parametreleri:**
- `resolution: 0.05`
- `minimum_travel_distance: 0.5`
- `loop_search_maximum_distance: 3.0`
- `scan_buffer_size: 10`

**Nav2 stack:**
- **Planner:** SmacPlannerHybrid (Hybrid-A*) — diferansiyel sürüş için optimum
- **Controller:** **RegulatedPurePursuitController (RPP)** — dar koridor için en sağlam, az tune
  - MPPI modern ama parametre cehennemi; DWB legacy; TEB Nav2'de yok
- **Collision Monitor** (`nav2_collision_monitor`) — bumper/yakın engel için kritik, jüri "güvenlik" puanı verecek
- **BehaviorTree.CPP 4.5+** mission orchestration

## 5. Algı katmanı — değişiklik önerileri

### QR vs ArUco vs AprilTag
- **pyzbar:** Bakımsız, son commit eski → **bırak**
- **zxing-cpp Python binding:** https://github.com/zxing-cpp/zxing-cpp — aktif, hızlı → **KULLAN**
- **qreader:** YOLO destekli, kötü ışıkta iyi → yedek
- **cv2.QRCodeDetector:** Zayıf → atla
- **cv2.aruco:** Pozisyon doğruluğu AprilTag'den geri
- **AprilTag 36h11:** Robotikte fiili standart, pose çok daha sağlam
  - ROS2 node: https://github.com/christianrauch/apriltag_ros
  - Param: `family: 36h11`, `size: 1.0`

**Karar:** QR için **zxing-cpp** (şartname "QR" diyor). Pose doğruluğu kritik noktalarda **AprilTag 36h11**.

### Çizgi takibi
OpenCV HSV mask + contour + PID. YOLO gereksiz, klasik CV daha güvenilir/hızlı.

### Palet tespiti — YOLO
- **YOLO11n** veya **YOLO26n** (Şubat 2026 çıkışlı)
- Jetson Orin Nano: `model.export(format="engine", half=True)` → TensorRT FP16
- INT8 + DLA için JetPack 6.x
- Public dataset: **LOCO** — https://github.com/tum-fml/loco
- Custom 200-500 imaj annotation + transfer learning yeter

## 6. Simülasyon — Gazebo sürüm

ROS 2 ↔ Gazebo uyumluluk:

| ROS 2 | Fortress | Harmonic |
|---|---|---|
| Humble (LTS) | **✅ resmî önerilen** | ⚡ caution (ros_gz köprü ile) |
| Jazzy (LTS) | ❌ | ✅ |

**Bizim durum:** Mevcut image'ımızda **Gazebo Classic 11.10.2** var (Humble'da resmi paket `ros-humble-gazebo-ros-pkgs` ile gelir). URDF'imiz `libgazebo_ros_*.so` Classic plugin'leri kullanıyor.

**Karar:** Şimdilik **Gazebo Classic 11 ile devam** — stabil, tutorial bol, mevcut URDF uyumlu. İleride Fortress'e geçmek opsiyonel; URDF'te plugin sözdizimi değişir (`ign_ros2_control`, `libignition-gazebo-*-system`).

## 7. PLC entegrasyonu — Türkiye fabrika gerçeği

Yaygınlık (büyük → küçük):
- **Siemens S7** (>%50)
- **Schneider Modicon** (Modbus/TCP native)
- **Mitsubishi FX** (yeni model Modbus/TCP)
- **Allen-Bradley** (Ethernet/IP — `pycomm3`)

OPC UA artık tüm yeni Siemens S7-1500, Schneider M580, Beckhoff'da standart.

**pymodbus 4.x:**
- `AsyncModbusTcpClient`, `AsyncModbusSerialClient`
- Default reconnect_delay/retries/timeout yeterli
- API: `read_holding_registers`, `write_register`, `read_coils`, `write_coil`

**asyncua (OPC UA):**
- `async with Client(url=...) as client: await node.read_value()`
- Beckhoff, Siemens S7-1500, Kepware test edilmiş

**Karar:** **Modbus/TCP MVP, asyncua bonus** (iki adaptör + adapter pattern zaten yapıldı). RS-485/RTU atla, Ethernet zaten fabrikada.

## 8. Python robotik 2026

- **rclpy** tek resmî yol, alternatif yok
- **Foxglove SDK** (mcap kayıt), **Rerun SDK** (multimodal logging) — rclpy yerine değil yanına
- **rxpy** — küçük takım için aşırı, asyncio yeter
- **Cosmic Python DDD pattern'ları** — robotikte birebir uygulayan açık kaynak proje **yok**
  - Bizim mimari **özgün**, PDR'de "Domain-Driven Robotics" başlığı açılabilir → jüri için yeni ve etkileyici

**Karar:** Cosmic Python pattern'lerini benimse, Aggregate'leri ince tut (Robot, Mission, Order). Event bus = asyncio.Queue (zaten yapıldı), handler'lar = async coroutine (zaten yapıldı).

## 9. Operatör arayüzü — üç katmanlı strateji

| Katman | Rol |
|---|---|
| **PySide6/QML** | Operatör paneli — görev başlat/durdur, harita seçim, manuel kontrol, durum |
| **Foxglove Studio + foxglove_bridge** | Canlı izleme — yarışma sahasında masaüstüne aç, jüri görsün |
| **Rerun** | Post-mortem kayıt — her run için 5-10 dk `.rrd`, PDR rapor için ekran görüntüsü/video |
| **RViz2** | Yedek geliştirme aracı |

**Karar:** Üç katmanın bir arada olması çok güçlü görünür. Foxglove bridge port 8765 WebSocket — kurması basit.

## 10. Yarışma stratejisi içgörüleri

- **HKV 11.08.2026 deadline** → robot Ağustos başında oynak/sürebilir olmalı. **Donanım entegrasyonunu Mayıs sonu – Haziran ortası bitir.**
- Tekrar derece alan takımlar **yıllar üstü kümülatif öğrenme** avantajı. Sizin için: yeniden kullanılabilir docker image'ları, repo template'leri, CI günden bir gün.
- **Sosyal medya:** LinkedIn #TEKNOFEST2026, X `@Teknofest`, finalist takımların Instagram hesapları. KILAVUZ KOU ROVER LinkedIn'de aktif.
- **PDR'de mutlaka olsun:** Mimari diyagram (DDD katmanları), VDA 5050 mesaj örneği, slam_toolbox + Nav2 stack şeması, PLC iletişim sıra diyagramı, güvenlik (Collision Monitor) ve hata kurtarma stratejisi.

## Karar matrisi

| Alan | KULLAN | DENE | ATLA |
|---|---|---|---|
| SLAM | slam_toolbox (mapping+localization) | Isaac cuVSLAM (yedek) | Cartographer, LIO-SAM |
| Nav | Nav2 (SmacHybrid + RPP + Collision Monitor) | MPPI controller | move_base, custom planner |
| Sim | Gazebo Classic 11 (Humble eşi) | Gazebo Fortress, Webots | Isaac Sim, MuJoCo |
| Fiducial | AprilTag 36h11 (apriltag_ros) | Isaac ROS apriltag (GPU) | pyzbar (eski) |
| QR | zxing-cpp Python | qreader | cv2.QRCodeDetector |
| Palet | YOLO11n + TensorRT FP16 | YOLO INT8 + DLA | YOLOv5/v8 (eski) |
| PLC | pymodbus 4.x AsyncModbusTcpClient | asyncua (ikinci adaptör) | Modbus RTU |
| Master-Control | VDA 5050 v3 MQTT/JSON şeması | Open-RMF kapı/lift mesajları | Özel JSON |
| Mimari | Cosmic Python DDD + asyncio | rxpy | Monolith |
| GUI | PySide6/QML + foxglove_bridge | Rerun (post-mortem) | React/web |
| Mission orkestrasyon | BehaviorTree.CPP 4.5+ | SMACH | Custom state machine |

## Kaynak linkleri

- TEKNOFEST SRUY 2026: https://www.teknofest.org/tr/yarismalar/sanayide-robotik-uygulamalar-yarismasi/
- Nav2: https://docs.nav2.org/
- slam_toolbox: https://github.com/SteveMacenski/slam_toolbox
- Open-RMF: https://github.com/open-rmf/rmf
- Open-RMF kitabı: https://osrf.github.io/ros2multirobotbook/
- VDA 5050: https://github.com/VDA5050/VDA5050
- Isaac ROS: https://nvidia-isaac-ros.github.io/
- Ultralytics + Jetson: https://docs.ultralytics.com/guides/nvidia-jetson/
- pymodbus: https://pymodbus.readthedocs.io/
- asyncua: https://github.com/FreeOpcUa/opcua-asyncio
- apriltag_ros: https://github.com/christianrauch/apriltag_ros
- Carologistics (RCLL): https://github.com/carologistics
- b-it-bots (RoboCup@Work): https://github.com/b-it-bots/mas_industrial_robotics
- ARIAC NIST: https://github.com/usnistgov/ARIAC
- Foxglove bridge: https://github.com/foxglove/ros-foxglove-bridge
- Rerun: https://rerun.io
- Cosmic Python: https://www.cosmicpython.com/book/preface.html
- Gazebo + ROS2: https://gazebosim.org/docs/harmonic/ros_installation
- LOCO palet datası: https://github.com/tum-fml/loco
