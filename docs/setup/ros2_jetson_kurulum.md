# Jetson + ROS2 Humble kurulum

NVIDIA Jetson Orin Nano üzerinde ROS2 Humble + CargoBot çekirdeği için temiz kurulum adımları. Yaklaşık 2-3 saatlik bir iş.

## 1. JetPack 6 (Ubuntu 22.04)

Jetson SD kart veya eMMC'ye JetPack 6 image'i yaz. JetPack 6 zaten Ubuntu 22.04 LTS getiriyor ki bu ROS2 Humble için doğru sürüm.

- https://developer.nvidia.com/embedded/jetpack — Orin Nano "JetPack 6.0" image
- balenaEtcher veya `sudo dd` ile microSD'ye yaz
- İlk boot: dil, klavye, user/şifre, network

## 2. Sistem güncelle

```bash
sudo apt update
sudo apt full-upgrade -y
sudo reboot
```

## 3. ROS2 Humble

ROS2 resmi apt repo ekle:

```bash
sudo apt install -y software-properties-common curl gnupg lsb-release
sudo add-apt-repository universe

sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
  -o /usr/share/keyrings/ros-archive-keyring.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] \
http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | \
  sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null

sudo apt update
sudo apt install -y ros-humble-desktop python3-rosdep python3-colcon-common-extensions
sudo rosdep init
rosdep update
```

`~/.bashrc`'a:
```bash
source /opt/ros/humble/setup.bash
export ROS_DOMAIN_ID=42
```

## 4. Navigasyon ve SLAM paketleri

```bash
sudo apt install -y \
  ros-humble-slam-toolbox \
  ros-humble-nav2-bringup \
  ros-humble-navigation2 \
  ros-humble-robot-localization \
  ros-humble-cv-bridge \
  ros-humble-image-transport \
  ros-humble-tf2-tools \
  ros-humble-tf-transformations
```

## 5. Sensör sürücüleri

### YDLIDAR (örnek)
```bash
sudo apt install -y ros-humble-ydlidar-ros2-driver
# veya GitHub'dan kaynak: https://github.com/YDLIDAR/ydlidar_ros2_driver
```

### RPLIDAR
```bash
sudo apt install -y ros-humble-rplidar-ros
```

### Intel RealSense D435i
```bash
sudo apt install -y ros-humble-realsense2-camera ros-humble-realsense2-description
```

### micro-ROS (STM32/ESP32 köprüsü)
```bash
sudo apt install -y ros-humble-micro-ros-msgs
# Agent kurulumu:
git clone -b humble https://github.com/micro-ROS/micro_ros_setup.git ~/microros_ws/src/micro_ros_setup
cd ~/microros_ws
rosdep update && rosdep install --from-paths src --ignore-src -y
colcon build
source install/local_setup.bash
ros2 run micro_ros_setup create_agent_ws.sh
ros2 run micro_ros_setup build_agent.sh
```

## 6. CargoBot Python ortamı

```bash
sudo apt install -y python3-pip python3-venv
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc

git clone https://github.com/KaanAlper/teknofest-2026-sruy.git ~/cargobot
cd ~/cargobot
uv sync --all-extras
```

## 7. ROS2 + CargoBot birlikte

```bash
# Terminal 1 — LIDAR sürücüsü
ros2 launch ydlidar_ros2_driver ydlidar_launch.py

# Terminal 2 — SLAM
ros2 launch slam_toolbox online_async_launch.py

# Terminal 3 — Nav2 (harita kaydedildikten sonra)
ros2 launch nav2_bringup bringup_launch.py map:=$HOME/maps/saha.yaml

# Terminal 4 — CargoBot çekirdek
cd ~/cargobot
uv run python src/main.py --headless
# veya GUI ile:
uv run python src/main.py
```

## 8. systemd servisi (yarışma günü otomatik açılış)

`/etc/systemd/system/cargobot.service`:
```ini
[Unit]
Description=CargoBot core
After=network.target

[Service]
Type=simple
User=cargobot
WorkingDirectory=/home/cargobot/cargobot
ExecStart=/home/cargobot/.local/bin/uv run python src/main.py --headless
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable cargobot
sudo systemctl start cargobot
sudo journalctl -fu cargobot      # canlı log
```

## 9. Ağ ayarları

Yarışma sahasındaki "YARISMA AGI" WiFi'ya bağlanmak için cihazın MAC adresini önceden yetkililere bildir:
```bash
ip link show wlan0 | awk '/ether/ {print $2}'
```

PLC ile aynı network'te:
```bash
ping <plc_ip>
```

## 10. ROS2 doğrulama

```bash
ros2 topic list
ros2 topic echo /scan
ros2 topic echo /odom
ros2 run rqt_graph rqt_graph
```

`rqt_graph` ile düğümlerin/topic'lerin bağlı olduğunu görsel olarak doğrula.

## Sorun giderme

| Sorun | Çözüm |
|---|---|
| `rclpy not found` | `source /opt/ros/humble/setup.bash` çalıştırıldı mı? |
| `cv_bridge` hatası | `sudo apt install ros-humble-cv-bridge` |
| `/scan` boş | LIDAR USB izni (`sudo chmod 666 /dev/ttyUSB0`) |
| Nav2 lokalize olamıyor | Önce `/initialpose` ver: rqt_gui ile |
| WiFi paket düşüyor | `iwconfig wlan0` çıkışı, RSSI -65'in altında ise antenna eklemek |
