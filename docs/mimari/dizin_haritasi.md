# Kod Dizin Haritası

```
src/cargobot/
│
├── __init__.py
├── main.py                          # asyncio entry-point (robot tarafı)
├── config.py                        # Pydantic config modelleri
│
├── domain/                          # Saf domain — framework yok, IO yok
│   │
│   ├── _shared/
│   │   ├── events.py                # DomainEvent base, correlation context
│   │   ├── value_objects.py         # Pose, Velocity, NodeId, vb.
│   │   └── exceptions.py
│   │
│   ├── mission/
│   │   ├── __init__.py
│   │   ├── aggregate.py             # Mission, MissionPlan
│   │   ├── states.py                # MissionPhase enum + geçiş tablosu
│   │   ├── events.py                # MissionStarted, LoadPicked, ...
│   │   └── policies.py              # event reaction politikaları
│   │
│   ├── navigation/
│   │   ├── __init__.py
│   │   ├── aggregate.py             # RouteGraph
│   │   ├── path_planner.py          # PathPlanner servisi (port)
│   │   ├── path_follower.py
│   │   ├── events.py
│   │   └── value_objects.py
│   │
│   ├── perception/
│   │   ├── __init__.py
│   │   ├── detectors.py             # QrDetector, LineDetector, ObstacleDetector portları
│   │   ├── scene.py
│   │   └── events.py
│   │
│   ├── safety/
│   │   ├── __init__.py
│   │   ├── aggregate.py             # SafetyState
│   │   ├── policies.py              # invariant kontrolleri
│   │   └── events.py
│   │
│   ├── fleet_io/
│   │   ├── __init__.py
│   │   ├── session.py               # PlcSession aggregate
│   │   ├── messages.py              # Domain mesaj tipleri (protokol-bağımsız)
│   │   ├── gateway.py               # PlcGateway abstract port
│   │   └── events.py
│   │
│   └── telemetry/
│       ├── __init__.py
│       ├── snapshot.py              # RobotSnapshot read-model
│       ├── projector.py             # event'lerden snapshot üreten projeksiyon
│       └── recorder.py
│
├── application/                     # Use case / orkestrasyon
│   ├── __init__.py
│   ├── commands.py                  # StartMissionCommand, vb.
│   ├── handlers/                    # her handler bir factory: closure ile deps + bus alır
│   │   ├── mission_handlers.py
│   │   ├── navigation_handlers.py
│   │   ├── safety_handlers.py
│   │   └── fleet_handlers.py
│   ├── wiring.py                    # << kim hangi event'i dinler — tek liste
│   └── bootstrap.py                 # App.build: bus + deps composition root
│
├── infrastructure/                  # Adapter'lar (IO, framework, donanım)
│   │
│   ├── bus/
│   │   ├── __init__.py
│   │   └── async_bus.py             # AsyncEventBus implementasyonu
│   │
│   ├── plc/
│   │   ├── __init__.py
│   │   ├── modbus_adapter.py        # pymodbus
│   │   ├── opcua_adapter.py         # asyncua
│   │   ├── raw_tcp_adapter.py
│   │   └── mock_adapter.py          # test/sim için
│   │
│   ├── lidar/
│   │   ├── ros2_subscriber.py       # /scan -> Perception
│   │   └── mock_lidar.py
│   │
│   ├── camera/
│   │   ├── opencv_camera.py
│   │   ├── ros2_image_sub.py
│   │   ├── qr_detector.py           # pyzbar wrapper
│   │   ├── aruco_detector.py
│   │   └── line_detector.py
│   │
│   ├── motor/
│   │   ├── ros2_cmd_vel.py
│   │   ├── serial_driver.py         # ESP32/STM32 ile UART
│   │   └── forklift_servo.py
│   │
│   ├── storage/
│   │   ├── map_store.py             # pgm/yaml dosyaları
│   │   ├── route_store.py
│   │   └── telemetry_store.py       # jsonl
│   │
│   └── ros2/
│       ├── __init__.py
│       ├── node.py                  # tek ROS2 düğümü (rclpy)
│       └── bridges.py               # Domain event ↔ ROS2 topic eşlemeleri
│
└── interface/                       # Dış dünyaya ucu
    ├── cli/
    │   └── cli.py                   # `cargobot --build-map`, vb.
    ├── api/
    │   ├── ws_server.py             # WebSocket sunucusu (GUI bağlanır)
    │   ├── ws_codec.py              # JSON serializer
    │   └── rest_app.py              # opsiyonel REST
    └── qml_bridge/
        └── notes.md                 # GUI ile sözleşme dökümanı


src/ui/                              # PySide6 + QML uygulaması
│
├── __init__.py
├── main.py                          # QGuiApplication entry-point (GUI tarafı)
├── app_context.py                   # QML için singleton context
│
├── viewmodels/
│   ├── robot_viewmodel.py           # QObject — snapshot binding
│   ├── mission_viewmodel.py
│   ├── plc_log_model.py             # QAbstractListModel
│   ├── map_viewmodel.py
│   ├── joystick_viewmodel.py
│   └── connection.py                # WebSocket istemcisi
│
├── qml/
│   ├── main.qml
│   ├── pages/
│   │   ├── DashboardPage.qml
│   │   ├── MapPage.qml
│   │   ├── PlcLogPage.qml
│   │   ├── ManualControlPage.qml
│   │   └── SettingsPage.qml
│   ├── components/
│   │   ├── StatusBadge.qml
│   │   ├── KeyValueRow.qml
│   │   ├── BatteryGauge.qml
│   │   ├── EmergencyBanner.qml
│   │   ├── Joystick.qml
│   │   ├── MapCanvas.qml
│   │   └── PlcMessageItem.qml
│   └── assets/
│       ├── icons/
│       └── fonts/
│
└── resources/
    ├── resources.qrc                # Qt resource file
    └── theme.json
```

## Modül-Modül Bağımlılık Sözleşmesi

| Katman | Bağımlı olabileceği |
|---|---|
| `domain/*` | sadece `domain/_shared`, standart kütüphane, **dış paket yok** |
| `application/*` | `domain/*` |
| `infrastructure/*` | `domain/*` (sadece port arayüzü için), dış paketler |
| `interface/*` | `application/*`, `domain/*` read-model |
| `ui/*` | sadece `interface/api` (WebSocket sözleşmesi), domain'i direkt **import etmez** |

> Çift yönlü değil — `domain` `infrastructure`'ı asla import etmez. DIP (Dependency Inversion).
