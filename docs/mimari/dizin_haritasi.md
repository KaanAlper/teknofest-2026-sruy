# Kod dizin haritası

`src/` altında her paket düz duruyor (Clonify yapısı gibi). Tek bir `cargobot/` kök paketi yok — import'lar doğrudan `domain.X`, `eventbus.X`, `application.X` şeklinde.

```
src/
├── main.py                      # robot entry-point
│
├── eventbus/                    # << sistemin omurgası, top-level paket
│   └── async_bus.py             # AsyncEventBus
│
├── domain/                      # saf — framework yok, IO yok
│   │
│   ├── _shared/
│   │   ├── events.py            # DomainEvent base, correlation context
│   │   ├── value_objects.py     # Pose, Velocity, NodeId, Mode
│   │   └── exceptions.py
│   │
│   ├── mission/                 # bounded context 1
│   │   ├── aggregate.py
│   │   ├── states.py            # MissionPhase + geçiş tablosu
│   │   └── events.py
│   │
│   ├── navigation/              # 2
│   │   ├── aggregate.py         # RouteGraph (Dijkstra)
│   │   ├── value_objects.py     # Waypoint, Edge, Path, MapMetadata
│   │   └── events.py
│   │
│   ├── perception/              # 3
│   │   ├── detectors.py         # QrDetector, LineDetector, ObstacleDetector port'ları
│   │   └── events.py
│   │
│   ├── safety/                  # 4
│   │   ├── aggregate.py         # SafetyState
│   │   └── events.py
│   │
│   ├── fleet_io/                # 5
│   │   ├── gateway.py           # PlcGateway port
│   │   ├── messages.py
│   │   └── events.py
│   │
│   └── telemetry/               # 6
│       └── snapshot.py          # RobotSnapshot read-model
│
├── application/                 # use case / orkestrasyon
│   ├── commands.py
│   ├── handlers/                # her handler bir factory: closure ile deps + bus alır
│   │   ├── mission_handlers.py
│   │   ├── navigation_handlers.py
│   │   ├── safety_handlers.py
│   │   └── fleet_handlers.py
│   ├── wiring.py                # << kim hangi event'i dinler — tek liste
│   └── bootstrap.py             # App.build composition root
│
├── infrastructure/              # adapter'lar (IO, framework, donanım)
│   ├── plc/
│   │   ├── mock_adapter.py
│   │   ├── modbus_adapter.py    # (plan: pymodbus)
│   │   └── opcua_adapter.py     # (plan: asyncua)
│   ├── lidar/                   # ROS2 /scan subscriber
│   ├── camera/                  # OpenCV + pyzbar + ArUco
│   ├── motor/
│   │   └── mock_motor.py
│   └── storage/                 # map_store, route_store, telemetry_store
│
├── interface/                   # dış dünyaya uçlar
│   ├── api/                     # WebSocket sunucusu
│   ├── cli/
│   └── qml_bridge/
│
└── ui/                          # PySide6 + QML uygulaması
    ├── main.py                  # QGuiApplication entry-point
    ├── app_context.py           # QML singleton köprü (WS istemcisi)
    ├── viewmodels/
    ├── qml/
    │   ├── main.qml
    │   ├── pages/
    │   ├── components/
    │   └── assets/
    └── resources/
```

## Bağımlılık sözleşmesi

| Katman | Bağımlı olabileceği |
|---|---|
| `domain/*` | sadece `domain/_shared`, standart kütüphane. Dış paket yok. |
| `application/*` | `domain/*`, `eventbus` |
| `infrastructure/*` | `domain/*` (sadece port arayüzü), `eventbus`, dış paketler |
| `interface/*` | `application/*`, `domain/*` (read-model) |
| `ui/*` | sadece `interface/api` (WebSocket sözleşmesi); domain'i doğrudan import etmez |
| `eventbus` | hiçbir şeye — base sınıf `domain/_shared/events.py`'den okur ama tip içe almak için, döngüsel değil |

`domain` `infrastructure`'ı asla import etmez — DIP. Port'lar domain tarafında tanımlı, adapter'lar onları implemente eder.
