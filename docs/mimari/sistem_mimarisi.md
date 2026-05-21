# Sistem mimarisi

DDD bounded context + event-driven. Domain framework bilmiyor, sadece saf Python; her şey adapter olarak `infrastructure/` altında. Context'ler birbirleriyle event bus üzerinden konuşuyor — doğrudan import yok. Detaylı pub/sub kuralları için `eventbus.md`.

Robot durumu tek noktada tutulur: Mission context state machine. UI bunu okur, başka kimse yazmaz.

asyncio tek event loop; bloklayan IO (LIDAR sürücüsü vb.) executor thread'lere atılır. PLC protokolü / LIDAR markası / kamera değiştirilebilir — testlerde mock adapter ile aynı kod yolu koşar.

## 2. Yüksek Seviye Bileşen Şeması (C4 — Level 1)

```
┌───────────────────────────────────────────────────────────────────┐
│                       Yarışma Sahası                              │
│                                                                   │
│   ┌──────────┐      WiFi      ┌─────────────────────────────┐    │
│   │   PLC    │ ◄──────────► │   CargoBot Operatör PC     │    │
│   │ (Kapı)   │  Modbus TCP   │   (PySide6 + QML)          │    │
│   └──────────┘   / OPC UA    └────────────┬────────────────┘    │
│                                            │                     │
│                                  ROS2 / WS bridge                │
│                                            │                     │
│                          ┌─────────────────▼────────────────┐    │
│                          │     CargoBot Robot (Jetson)      │    │
│                          │   ┌──────────────────────────┐  │    │
│                          │   │  cargobot/domain (DDD)   │  │    │
│                          │   │  cargobot/application    │  │    │
│                          │   │  cargobot/infrastructure │  │    │
│                          │   └──────────────────────────┘  │    │
│                          │       │      │      │           │    │
│                          │   LIDAR  Kamera  Motorlar       │    │
│                          └──────────────────────────────────┘    │
└───────────────────────────────────────────────────────────────────┘
```

## 3. Çalışma Süreçleri

İki ana proses var, gevşek bağlı:

### Proses A — Robot (Jetson Orin Nano / Pi 5 üzerinde)
- **ROS2 node'ları:** lidar driver, camera driver, motor driver, slam_toolbox, nav2 stack
- **CargoBot çekirdeği (Python asyncio uygulaması):**
  - `domain/*` — saf modeller, agregalar, domain events
  - `application/*` — komut işleyiciler, sagas
  - `infrastructure/*` — ROS2 adapter, PLC adapter, depo
  - `interface/api` — WebSocket sunucusu (operatör PC ile konuşur)

### Proses B — Operatör PC (PySide6 + QML uygulaması)
- WebSocket istemcisi
- QML view + viewmodel (Qt sinyalleri ile binding)
- Harita render (canvas/Image overlay)
- Manuel joystick → komut akışı

> **Geliştirme aşamasında her ikisi de tek PC'de çalışabilir.**

## 4. Mantıksal Katmanlar

```
┌──────────────────────────────────────────────────┐
│         Interface (CLI / WS API / QML)           │  ← I/O ucu
├──────────────────────────────────────────────────┤
│       Application (use cases, sagas)             │  ← orkestrasyon
├──────────────────────────────────────────────────┤
│  Domain (entities, aggregates, value objects,    │  ← saf iş kuralı
│          domain events, services)                │
├──────────────────────────────────────────────────┤
│   Infrastructure (PLC, LIDAR, kamera, motor,     │  ← donanım/IO
│        ROS2 köprü, persistence, event bus)       │
└──────────────────────────────────────────────────┘
```

**Bağımlılık yönü:** Üstten alta — Interface ⇢ Application ⇢ Domain ⇠ Infrastructure (DIP).

## 5. Event Bus

Tek bir in-process **event bus** (asyncio Queue tabanlı, `aiopubsub` veya custom). Her bounded context:
- **Yayınlar:** kendi domain event'lerini (örn. `QrCodeDetected`)
- **Dinler:** ilgilendiği diğer context event'lerini (örn. `MissionContext` `QrCodeDetected`'i dinler)

**Avantaj:** Test edilirken event bus mock değiştirilir; gerçek koşumda Redis/MQTT'ye geçebilir.

**Bus implementasyonu:** `cargobot.infrastructure.bus.AsyncEventBus`
- `publish(event: DomainEvent)`
- `subscribe(event_type, handler)`
- `unsubscribe(handler)`

## 6. Komut & Event Akışı Örneği (Yük Alma Senaryosu)

```
PLC                Application            Mission Domain      Navigation       Perception
 │                     │                       │                  │                │
 │── PickRequest ───►  │                       │                  │                │
 │                     │── StartMission ────►  │                  │                │
 │                     │                       │── MissionStarted (event) ────────►│
 │                     │                       │                  │                │
 │                     │                       │── PathRequested ►│                │
 │                     │                       │                  │── path ───►    │
 │                     │                       │◄── PathReady ────│                │
 │                     │                       │                  │                │
 │                     │                       │── MoveTo ───────►│                │
 │                     │                       │                  │                │
 │                     │                       │                  │   (yakın)      │
 │                     │                       │◄── QrCodeDetected ───────────────│
 │                     │                       │                                   │
 │                     │                       │── ApproachLoad ─►│                │
 │                     │                       │   (çizgi takibi)│                │
 │                     │                       │◄── LoadPicked ───│                │
 │                     │                       │                                   │
 │◄── PickConfirmed ───│                       │                                   │
```

## 7. Teknoloji Seçimleri

| Katman | Teknoloji | Gerekçe |
|---|---|---|
| Dil | Python 3.12 | Ekosistem + hız (uvloop ile yeterli) |
| Concurrency | asyncio + uvloop | Olay döngüsü tek kaynak |
| Robotik | ROS2 Humble (sürücüler, SLAM, Nav2) | Hazır stack, sıfırdan yazmak için süre yok |
| GUI | PySide6 + QML | Şartname kullanıcı arayüzü puanı için |
| Bridge | WebSocket (JSON) veya gRPC | Süreçler arası |
| Test | pytest, pytest-asyncio | Standart |
| Sim | Gazebo Garden | Şartname senaryosunun replikası |
| Format | Black + Ruff + mypy | Disiplin |
| Paket | uv (PEP 621 pyproject.toml) | Hızlı bağımlılık çözümleyici |

## 8. Konfigürasyon

`config/` altında YAML dosyaları:
- `robot.yaml` — fiziksel parametreler (tekerlek çapı, baz genişlik, kamera kalibrasyon)
- `field.yaml` — saha bilgileri (rota grafı, QR ID → konum)
- `plc.yaml` — `protocol: modbus_tcp | opc_ua | raw_tcp`, host, port, register/node ID'leri
- `slam.yaml` — slam_toolbox parametreleri
- `nav2.yaml` — Nav2 stack tuning
- `safety.yaml` — emergency stop, max hız, güvenli mesafe

Konfigürasyon doğrulaması **Pydantic v2** ile.

## 9. Loglama & Telemetri

- **Log:** `structlog` + JSON çıktı, dosya rotation
- **Telemetri:** Tüm domain event'ler ek olarak telemetri dosyasına yazılır (replay için)
- **Metrik:** Prometheus exporter (opsiyonel, geliştirme için)
- **Saha kaydı:** `ros2 bag` ile tüm topic kaydı (post-mortem)

## 10. Dağıtım

- **Geliştirme:** docker compose (PLC sim + Gazebo + cargobot)
- **Robot:** systemd service (`cargobot.service`)
- **GUI:** PyInstaller ile self-contained exe (operatör PC için)

Detay:
- [EventBus ve modüller arası bağlantı](eventbus.md)
- [Bounded context kataloğu](bounded_contexts.md)
- [Domain event kataloğu](event_katalogu.md)
- [Sekans diyagramları](sekanslar.md)
- [Dizin haritası](dizin_haritasi.md)
