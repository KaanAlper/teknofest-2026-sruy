# Lokal simülasyon ortamı

Robot teslim alınmadan önce yarışma kodunu tam koşturabilmek için Docker compose üstünde Gazebo + ROS2 Humble + slam_toolbox + Nav2 + Modbus PLC sim'i çalıştırırız. CargoBot Python çekirdeği bu stack'e gerçekteki gibi bağlanır.

## Önkoşullar (CachyOS / Arch)

```bash
sudo pacman -S docker docker-buildx docker-compose
sudo usermod -aG docker $USER
newgrp docker
sudo systemctl enable --now docker
docker compose version          # doğrulama
```

Ubuntu/Debian'da:
```bash
sudo apt install docker.io docker-compose-plugin
sudo usermod -aG docker $USER
newgrp docker
```

X11 erişimi (Gazebo penceresi için):
```bash
xhost +local:docker
```

## URDF üret

Xacro → URDF dönüşümü (ros2 humble image içinde):
```bash
docker run --rm -v $PWD:/workspace osrf/ros:humble-desktop-full \
  bash -c "source /opt/ros/humble/setup.bash && \
    xacro /workspace/hardware/urdf/cargobot.urdf.xacro > /workspace/hardware/urdf/cargobot.urdf"
```

## Ayağa kaldır

```bash
docker compose up
```

Sırayla:
- `cargobot-plc-sim` — Modbus TCP server (port 5020)
- `cargobot-ros2` — Gazebo + slam_toolbox + Nav2; saha world + cargobot URDF spawn
- `cargobot-core` — CargoBot Python süreci `--profile=sim` modunda

Beklenen davranış:
- Gazebo penceresi açılır, robotu sahada görürsün
- RViz2 ile `rqt`'ten `/scan`, `/odom`, `/map` topic'lerini görebilirsin
- CargoBot konsolunda PLC bağlantısı + ROS2 köprüleri başlar
- Operatör arayüzünü ayrı bir terminalde aç:
  ```bash
  CARGOBOT_PROFILE=mock uv run python src/main.py
  # veya ws ile sim'e bağlan (ws server hazır olunca):
  uv run python src/main.py --remote ws://localhost:8765/telemetry
  ```

## Profil seçimi

CargoBot çekirdeği davranışını çevre değişkeniyle belirler:

| `CARGOBOT_PROFILE` | Adapter set | Senaryo |
|---|---|---|
| `mock` (default) | MockPlc, MockMotor | Donanım yok — demo akış log/GUI'ye düşer |
| `sim` | ModbusPlc(localhost:5020), Ros2CmdVel | Docker compose sim — gerçek topic'ler |
| `real` | ModbusPlc(saha PLC IP'si), Ros2CmdVel | Jetson + gerçek robot, yarışma sahası |

`PLC_HOST` ve `PLC_PORT` env değişkenleri ile override edilir.

## Bir görev gönder (sim altında PLC'ye)

Modbus simulator'a register yaz:
```bash
docker exec cargobot-plc-sim python3 -c "
from pymodbus.client import ModbusTcpClient
c = ModbusTcpClient('localhost', port=5020)
c.connect()
c.write_register(100, 1)   # pickup_node = p1
c.write_register(101, 2)   # dropoff_node = d2
"
```

CargoBot ModbusPlc poll loop'unda bu değişikliği yakalar, `PickAssignmentReceived` event'i bus'a düşer, mission saga başlar.

## Sorun giderme

| Sorun | Çözüm |
|---|---|
| `permission denied` Docker | `sudo usermod -aG docker $USER && newgrp docker` |
| Gazebo penceresi açılmıyor | `xhost +local:docker`; `DISPLAY` env değişkeni |
| `cannot connect to display` | SSH sessions için `xauth` ek ayar; lokal kullan |
| `/scan` topic boş | Robot URDF'ı spawn olmamış; gazebo loglarına bak |
| Nav2 plan çıkaramıyor | Önce harita kaydet (`ros2 run nav2_map_server map_saver_cli`), sonra `map:=...` ile aç |
| ROS2 image indirme yavaş | `docker pull osrf/ros:humble-desktop-full` arka planda bir kez çek |
| CargoBot core bağlanamıyor | `docker compose logs cargobot-core` ile detay |

## Headless mod (CI / sunucuda)

GUI yok, sadece test:
```bash
CARGOBOT_PROFILE=sim docker compose up cargobot-plc-sim cargobot-ros2 -d
CARGOBOT_PROFILE=sim uv run python src/main.py --headless
```

## URDF görsel doğrulama (Gazebo'sız)

```bash
docker run --rm -it -v $PWD:/workspace osrf/ros:humble-desktop-full \
  bash -c "source /opt/ros/humble/setup.bash && \
    ros2 launch urdf_tutorial display.launch.py model:=/workspace/hardware/urdf/cargobot.urdf"
```
