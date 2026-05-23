# CargoBot — TEKNOFEST 2026 SRUY · ROS 2 Humble + Gazebo Simülasyonu

Sanayide Robotik Uygulamalar Yarışması (SRUY) için **otonom forklift mobil robot**
simülasyonu. Şartnamedeki tüm görevler ROS 2 Humble + Gazebo Classic üzerinde
çalışacak şekilde modellenmiştir.

> Bu workspace, [`KaanAlper/teknofest-2026-sruy`](https://github.com/KaanAlper/teknofest-2026-sruy)
> (CargoBot) projesinin **simülasyon ayağıdır**. Repo mimariyi (DDD + asyncio +
> Nav2/slam_toolbox) tanımlar; bu workspace o görevleri Gazebo'da somutlaştırır.

## Şartname görevleri → bu projedeki karşılığı

| # | Şartname görevi | Karşılığı |
|---|-----------------|-----------|
| 1 | 2D lazerle haritalama | `slam_toolbox` (`cargobot_navigation/slam.launch.py`) |
| 2 | Rota tanımlama | Nav2 global planner + hedef noktalar (`mission_manager`) |
| 3 | Fabrika otomasyon (PLC) ile haberleşme | `plc_simulator` ↔ `mission_manager` (WiFi/Modbus taklidi) |
| 4 | Görüntü işleme ile çizgi takibi | `line_follower` (HSV maske + P kontrol) |
| 5 | QR/ArUco okuma + konum hesaplama | `qr_detector` (solvePnP / estimatePose) |
| 6 | Engelde güvenli durma | `safety_stop` + Nav2 costmap |
| 7-8 | Rota sapması / konum-yön toleransı | Nav2 `xy_goal_tolerance=0.075`, `yaw=0.087` |
| 9 | Kontrollü kapıdan geçiş | PLC el sıkışma + Gazebo sürgülü kapı |
| 10 | Kullanıcı arayüzü + durum makinesi | `dashboard` + `mission_manager` FSM |
| - | Acil stop | `/emergency_stop` → `cmd_vel_mux` tüm motorları keser |
| Ekstra | Otomatik şarj | FSM'e `LOW_BATTERY` durumu eklenerek genişletilebilir |

## Paketler

- **cargobot_description** — URDF/xacro robot (diff-drive + 2D lidar + kamera + fork) ve Gazebo eklentileri
- **cargobot_gazebo** — Fabrika dünyası (`factory.world`) ve spawn launch
- **cargobot_navigation** — `slam_toolbox` + Nav2 konfigürasyonu
- **cargobot_perception** — `qr_detector`, `line_follower`, `safety_stop`
- **cargobot_mission** — `mission_manager` (FSM), `plc_simulator`, `cmd_vel_mux`, `dashboard`
- **cargobot_bringup** — Tam simülasyon launch'ı

## Gereksinimler

- Ubuntu 22.04 + **ROS 2 Humble**
- Gazebo Classic (gazebo11) + `gazebo_ros_pkgs`
- Nav2, slam_toolbox, OpenCV, cv_bridge

```bash
sudo apt update && sudo apt install -y \
  ros-humble-desktop ros-humble-gazebo-ros-pkgs \
  ros-humble-navigation2 ros-humble-nav2-bringup \
  ros-humble-slam-toolbox ros-humble-nav2-simple-commander \
  ros-humble-robot-state-publisher ros-humble-joint-state-publisher-gui \
  ros-humble-xacro ros-humble-cv-bridge \
  ros-humble-nav2-regulated-pure-pursuit-controller \
  python3-opencv
```

## Derleme

```bash
cd cargobot_ws
source /opt/ros/humble/setup.bash
colcon build --symlink-install
source install/setup.bash
```

## Çalıştırma

### 1) Haritalama (Görev-1)
```bash
ros2 launch cargobot_bringup simulation.launch.py slam:=true
# Ayrı terminal: teleop ile sahayı gez
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r cmd_vel:=/cmd_vel_teleop
# Manuel moda al:
ros2 topic pub --once /manual_mode std_msgs/Bool '{data: true}'
# Harita kaydet:
ros2 run nav2_map_server map_saver_cli -f src/cargobot_navigation/maps/factory_map
```

### 2) Tam senaryo (Nav2 + PLC + QR + çizgi + kapı)
```bash
ros2 launch cargobot_bringup simulation.launch.py slam:=false
# Kontrol paneli (ayrı terminal):
ros2 run cargobot_mission dashboard
```
`mission_manager` otomatik olarak: PLC'ye bağlanır → görev alır → alma noktasına
gider → çizgi/QR ile hassas konumlanır → yükü alır → kapıda PLC el sıkışması →
bırakma noktası → dönüşte tekrar kapı → bekleme noktası.

### Acil stop testi (video için zorunlu)
```bash
ros2 topic pub --once /emergency_stop std_msgs/Bool '{data: true}'   # tüm motorlar durur
ros2 topic pub --once /emergency_stop std_msgs/Bool '{data: false}'  # devam
```

## Mimari (topic akışı)

```
Gazebo(diff_drive) --/scan,/odom,/camera--> [slam/nav2, perception]
                                                   |
  PLC sim <--/plc/*--> mission_manager(FSM) --/cmd_vel(nav2)--+
                                                   |          |
  line_follower --/cmd_vel_line------------------> cmd_vel_mux --/cmd_vel_out--> wheels
  safety_stop  --/safety/stop--------------------> (estop/safety = HARD STOP)
  dashboard <----/robot_state,/plc/*,/perception/*
```

## Gerçek yarışmaya geçiş notları
- PLC haberleşmesi: `plc_simulator` yerine gerçek **Modbus TCP / OPC-UA** (pymodbus, asyncua).
- Arayüz: terminal `dashboard` yerine repodaki **PySide6 + QML** arayüz.
- Donanım: `gazebo_ros_diff_drive` yerine gerçek motor sürücü + `ros2_control`.
- Otomatik şarj (+5 puan): FSM'e batarya izleme ve şarj istasyonu hedefi eklenir.
