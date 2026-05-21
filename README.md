# CargoBot

TEKNOFEST 2026 Sanayide Robotik Uygulamalar Yarışması (SRUY) için otonom forklift mobil robot. Fabrika içi lojistikte palet üzerindeki yükü, rota grafından geçerek alma noktasından bırakma noktasına taşır; fabrika PLC'si ile WiFi üzerinden haberleşir; kapı kontrolünü PLC ile el sıkışarak yönetir.

## Hızlı başlangıç

Sıfırdan çalıştırmak için gerekli her şey:

**Önkoşullar:**
- Docker + `docker compose` v2 (Arch/CachyOS: `sudo pacman -S docker docker-buildx && sudo systemctl enable --now docker && sudo usermod -aG docker $USER && newgrp docker`)
- Python ≥3.11 + [uv](https://docs.astral.sh/uv/) (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- ROS2 Humble ve Gazebo **gerek yok** — Docker image'ında geliyor. Robot teslim alınınca Jetson'a kurulur (bkz. [`docs/setup/ros2_jetson_kurulum.md`](docs/setup/ros2_jetson_kurulum.md))

**Kurulum:**
```bash
git clone https://github.com/KaanAlper/teknofest-2026-sruy.git CargoBot && cd CargoBot

# Python bağımlılıkları
uv sync --all-extras
# veya pip ile: pip install -r requirements.txt

# Sim image build (ilk seferde 5-10 dk, ~5.4 GB)
docker compose build ros2
```

**Çalıştırma:**

| Komut | Ne yapar |
|---|---|
| `uv run python src/main.py` | GUI açar, mock akış konsola düşer (donanım yok) |
| `uv run python src/main.py --headless` | GUI'siz, sadece log |
| `docker compose up -d ros2` | Gazebo sim + slam_toolbox + Nav2 (headless). 15-20 sn sonra robot sahada |
| `CARGOBOT_PROFILE=sim uv run python src/main.py --headless` | CargoBot çekirdeği sim'e bağlanır |
| `docker compose up` | Tüm stack: PLC sim + Gazebo + cargobot çekirdek |

**Sim çalışıyor mu?** Test:
```bash
docker exec -e ROS_DOMAIN_ID=42 cargobot-ros2 bash -c \
  "source /opt/ros/humble/setup.bash && ros2 topic hz /scan"
# Beklenen: ~50 Hz
```

**Sim'i görsel izlemek (Gazebo penceresi):**
```bash
xhost +local:docker
docker exec -e DISPLAY=$DISPLAY cargobot-ros2 bash -c \
  "source /opt/ros/humble/setup.bash && gzclient"
```

Detaylı sim rehberi: [`docs/setup/sim_kurulum.md`](docs/setup/sim_kurulum.md)

## Teknoloji

- Python 3.12, asyncio
- PySide6 + QML — operatör arayüzü
- ROS2 Humble — sürücüler, SLAM, Nav2
- slam_toolbox + Nav2
- OpenCV — QR/ArUco/çizgi takibi
- pymodbus / asyncua — PLC adapter'leri
- Mimari: DDD bounded context + tip tabanlı asyncio event bus

## Klasör

```
docs/    şartname, mimari, plan, raporlar, görsel tasarım
src/
  domain/         bounded contextler (mission, navigation, perception, safety, fleet_io, telemetry)
  application/    handler factory'leri + wiring + bootstrap
  eventbus/       AsyncEventBus — sistemin omurgası, top-level paket
  infrastructure/ PLC, LIDAR, kamera, motor, storage adapter'leri
  interface/      CLI / WS API / QML bridge
  ui/             PySide6 + QML operatör arayüzü
  main.py         robot entry-point
hardware/  BOM, şematik, CAD
sim/       Gazebo dünyaları
tests/     unit + integration + sim
```

## Mimari özet

Sistem 6 bounded context'e bölünmüş: mission, navigation, perception, safety, fleet_io, telemetry. Her context kendi event'lerini `events.py` içinde tanımlar ve dış dünyaya **sadece bus üzerinden** açılır. Doğrudan import yasak. Bağlantı şeması `application/wiring.py` içinde tek listede durur — C++'taki connection manager'ın işini bu dosya görür. Detay: `docs/mimari/eventbus.md`.

Domain saf Python (framework bilmiyor); donanım/PLC/UI hep adapter olarak `infrastructure/` altında. UI ayrı bir süreç olarak WebSocket üzerinden bağlanır.

## Yarışma takvimi

| Tarih | Aşama |
|---|---|
| 20 May 2026 | Son başvuru |
| 02 Haz 2026 17:00 | Teknik Yeterlilik Formu |
| 01 Tem 2026 17:00 | Proje Detay Raporu |
| 11 Ağu 2026 17:00 | Hareket-Kabiliyet Videosu |
| 18 Ağu 2026 | Finalist listesi |
| 30 Eyl – 4 Eki 2026 | Final, Şanlıurfa |

Puanlama: rapor %15, video %15, saha %70. Saha üstünde en yüksek tek kalem 30 puanla **görev tamamlama** ve **haritalama**. GUI'de gerekli bilgilerden eksik olan her biri −4 puana mal oluyor; CI'da snapshot bütünlüğü test ediliyor (`tests/integration/test_ui_information_completeness.py`).

## Çalıştırma

```
uv sync --all-extras
uv run cargobot          # robot tarafı (şu an mock PLC + mock motor ile)
uv run cargobot-gui      # PySide6 operatör arayüzü
uv run pytest tests/unit
```

## Belge indeksi

- `docs/sartname/sartname_ozeti.md`
- `docs/sartname/gorevler_puanlama.md`
- `docs/mimari/sistem_mimarisi.md`
- `docs/mimari/eventbus.md`
- `docs/mimari/bounded_contexts.md`
- `docs/mimari/event_katalogu.md`
- `docs/mimari/sekanslar.md`
- `docs/mimari/dizin_haritasi.md`
- `docs/donanim/bom.md`
- `docs/donanim/kablolama.md`
- `docs/arayuz/qml_tasarim.md`
- `docs/plan/yol_haritasi.md`
- `docs/plan/risk_matrisi.md`
- `docs/plan/ekip_roller.md`
- `docs/test/test_stratejisi.md`
- `docs/raporlar/TYF_iskelet.md`
- `docs/raporlar/PDR_iskelet.md`
- `docs/raporlar/video_storyboard.md`
- `docs/arastirma/gecmis_yillar.md`
- `docs/arastirma/referans_projeler.md`
