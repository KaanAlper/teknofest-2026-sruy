# Referans Projeler ve Kaynak Kütüphane

> Geliştirme sırasında "tekerleği yeniden icat etmemek" için sık başvurulacak açık kaynak projeler ve dokümanlar.

## 1. Açık Kaynak AGV / AMR / Forklift Projeleri

| Proje | Açıklama | Link |
|---|---|---|
| **linorobot2** | Diferansiyel/mecanum ROS2 AMR şablonu — ESP32 firmware, Nav2 + SLAM hazır config | https://github.com/linorobot/linorobot2 |
| **Axioma_robot** | Endüstriyel lojistik AGV; Nav2 + SLAM + AMCL ROS2 örneği | https://github.com/MrDavidAlv/Axioma_robot |
| **aeksiri/forklift** | Gazebo'da CitiTruck forklift modeli ve kontrol arayüzü | https://github.com/aeksiri/forklift |
| **open-rmf/rmf** | Çoklu robot orkestrasyon (gelecekte filo yönetimi için) | https://github.com/open-rmf/rmf |
| **uos_diffbot** | Diferansiyel sürüş Gazebo+ROS2 örneği | https://github.com/uos/uos_diffbot |

## 2. SLAM & Navigasyon

| Kaynak | Konu |
|---|---|
| Nav2 + slam_toolbox tutorial | https://docs.nav2.org/tutorials/docs/navigation2_with_slam.html |
| slam_toolbox repo | https://github.com/SteveMacenski/slam_toolbox |
| Robotics Backend — Nav2 SLAM | https://roboticsbackend.com/ros2-nav2-generate-a-map-with-slam_toolbox/ |
| Automatic Addison — Nav2 stack | https://automaticaddison.com/navigation-and-slam-using-the-ros-2-navigation-stack/ |
| Husarion SLAM tutorial | https://husarion.com/tutorials/ros2-tutorials/8-slam/ |

## 3. PLC Haberleşmesi

| Kütüphane | Protokol | Link |
|---|---|---|
| **pymodbus** | Modbus TCP/RTU (asyncio destekli) | https://github.com/pymodbus-dev/pymodbus |
| **asyncua** | OPC UA (asyncio) | https://github.com/FreeOpcUa/opcua-asyncio |
| **pycomm3** | Allen-Bradley Ethernet/IP | https://github.com/ottowayi/pycomm3 |
| **python-snap7** | Siemens S7 | https://github.com/gijzelaerr/python-snap7 |

**Yardımcı yazılar:**
- https://controlbyte.tech/blog/python-modbus-plc-communication/
- https://blog.jonasneubert.com/2019/11/02/using-pymodbus-to-communicate-with-a-plc/
- https://github.com/simeonthefirst/modbustcp-opcua (Modbus ↔ OPC UA köprüsü)

> **Karar:** PLC protokolü TEKNOFEST tarafından sonradan duyurulacak. **PlcGateway adapter** soyutlaması ile **pymodbus** ve **asyncua** birden uygulanmalı; çalıştırma anında env değişkeni veya config dosyasıyla seçilebilmelidir.

## 4. Görüntü İşleme

| Konu | Kaynak |
|---|---|
| OpenCV ArUco | https://docs.opencv.org/4.x/d5/dae/tutorial_aruco_detection.html |
| ArUco pose estimation örnek | https://github.com/GSNCodes/ArUCo-Markers-Pose-Estimation-Generation-Python |
| Automatic Addison ArUco | https://automaticaddison.com/how-to-perform-pose-estimation-using-an-aruco-marker/ |
| QR ile yönelim | https://temugeb.github.io/python/computer_vision/2021/06/15/QR-Code_Orientation.html |
| pyzbar (QR okuma) | https://github.com/NaturalHistoryMuseum/pyzbar |
| Çizgi takibi OpenCV | https://learnopencv.com/lane-detection-using-opencv/ |
| YOLOv8 (engel tipi sınıflama, ops.) | https://github.com/ultralytics/ultralytics |

> **Strateji:** Şartname net olarak **"QR kod okuma + kameraya göre pozisyon hesaplama"** dediği için **QR ID + ArUco pose** **hibrit** yaklaşımı kullan (QR'la ID, ArUco ile mm-doğruluk).

## 5. PyQt6 / PySide6 + QML

| Kaynak | Açıklama |
|---|---|
| **trin94/PySide6-project-template** | Modern QtQuick proje iskeleti | https://github.com/trin94/PySide6-project-template |
| **qmlease** | Python-QML köprü ergonomisi (decorator tabanlı) | https://github.com/likianta/qmlease |
| **PySide6-FluentUI-QML** | Modern Fluent görünüm | https://github.com/zhuzichu520/PySide6-FluentUI-QML |
| pythonguis examples | https://github.com/pythonguis/pythonguis-examples |
| PySide6 resmi tutorial | https://www.pythonguis.com/pyside6-tutorial/ |
| Qt for Python QML kılavuzu | https://doc.qt.io/qtforpython-6/tutorials/qmlapp/qmlapplication.html |

**Önemli desen:**
- ROS2/asyncio **ayrı thread** veya **ayrı süreç** olarak çalıştırılır
- `QObject` köprü sınıfı `Signal/Slot` ile QML'e veri akıtır
- QML tarafında `Connections {}` ile binding yapılır
- Büyük listeler için `QAbstractListModel` (ör. PLC mesaj logu)

## 6. ROS2 + PySide6 Köprüsü

| Kaynak | Açıklama |
|---|---|
| `rclpy` resmi | https://docs.ros.org/en/humble/Concepts/About-Internal-Interfaces.html |
| Foxglove WebSocket köprüsü | https://github.com/foxglove/ws-protocol |
| rclpy + QThread örnek | https://answers.ros.org/question/372954/ |

> **Karar:** Robot tarafında ROS2 düğümleri çalışır. GUI bilgisayarında PySide6 uygulaması **WebSocket köprüsü** (Foxglove protokolü veya custom JSON) üzerinden ROS2 topic'lerine erişir. Bu kısım bounded context olarak `interface/qml_bridge` altına soyutlanır.

## 7. Test & Sim

| Araç | Kullanım |
|---|---|
| **Gazebo Garden / Ignition** | Senaryonun full sim'i (saha, palet, kapı) |
| **Foxglove Studio** | Canlı topic görüntüleme, kayıt oynatma |
| **pytest + pytest-asyncio** | Unit + integration |
| **ros2 bag** | Saha verisi kaydı + replay |
| **Locust** ya da **vegeta** | PLC simülatörüne yük testi |

## 8. Mimari & Tasarım

| Konu | Kaynak |
|---|---|
| DDD (Eric Evans, Vaughn Vernon özetleri) | https://www.domainlanguage.com/ddd/ |
| Python DDD örnek (Cosmic Python) | https://www.cosmicpython.com/book/preface.html |
| Event-driven Python (FastStream, Faust) | https://faust-streaming.github.io/faust/ |
| C4 model | https://c4model.com/ |

## 9. Yerlilik için Türk Ekosistem

- **Yerli motor sürücü:** Anadolu Motor, Robotsepeti, Direnc.net üzerinden Türk üreticiler
- **Yerli STM32 alternatifleri:** ASELSAN tasarımları (sınırlı), Robotistan kart serileri
- **Yerli yazılım:** Pardus tabanlı işletim sistemi (Ubuntu yerine düşünülebilir)
- **Yerli LIDAR:** Hala kısıtlı; alternatif olarak Türk takım tasarımı ToF dizi sensörü (özgünlük + yerlilik birleştirir)

> +5/+5 puan için **bir yerli komponent + bir özgün mekanik tasarım** hedeflenmeli.
