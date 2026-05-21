# Bounded Context Kataloğu

CargoBot domain'i altı bounded context'e ayrılır. Her context kendi modelini, dilini ve event'lerini taşır.

## Context Haritası

```
                   ┌─────────────────────┐
                   │   Mission Context   │  (orkestratör)
                   └──┬───────────────┬──┘
        emits/listens │               │ commands
                      ▼               ▼
        ┌──────────────────┐   ┌─────────────────┐
        │ Navigation Ctx   │   │  Perception Ctx │
        └──────────────────┘   └─────────────────┘
                      ▲               ▲
                      │               │
                      └───────┬───────┘
                              ▼
                   ┌──────────────────────┐
                   │  Safety Context      │ (override hakkı)
                   └──────────────────────┘
                              │
                              ▼
                   ┌──────────────────────┐
                   │  Fleet I/O Context   │ (dış dünya - PLC)
                   └──────────────────────┘
                              │
                              ▼
                   ┌──────────────────────┐
                   │  Telemetry Context   │ (her şeyi dinler)
                   └──────────────────────┘
```

## 1. Mission Context (`domain/mission/`)

**Amaç:** Yarışma senaryosunun durum makinesi; hangi göreve ne zaman başlanır, faz geçişleri.

### Agregalar
- `Mission` — bir alma-bırakma görevinin yaşam döngüsü
- `MissionPlan` — tüm görev için adım listesi (segmentler)

### Value Objects
- `MissionId`, `PickupNode`, `DropoffNode`, `MissionPhase` (enum)
- `RobotStatus` — şartnamenin 8 durumundan biri:
  - `IDLE`, `MISSION_RECEIVED`, `MOVING_UNLOADED`, `MOVING_LOADED`,
    `WAITING_PLC`, `RETURNING_HOME`, `ERROR`, `EMERGENCY_STOP`

### Komutlar (Application'dan gelir)
- `StartMission(pickup, dropoff)`
- `AbortMission(reason)`
- `ResumeMission()`

### Yayınladığı Event'ler
- `MissionStarted`, `MissionPhaseChanged`, `MissionCompleted`, `MissionAborted`, `LoadPicked`, `LoadDropped`, `MissionGenericError`

### Dinlediği Event'ler
- `QrCodeDetected` → faz geçişi
- `WaypointReached` → bir sonraki segmente geç
- `EmergencyStopActivated` → faz dondur

---

## 2. Navigation Context (`domain/navigation/`)

**Amaç:** Harita üzerindeki rota planlama, takip ve düşük seviye sürüş emirleri.

### Agregalar
- `RouteGraph` — düğüm/kenar yapısı (alma, bırakma, bekleme, kapı, vb.)
- `Pose` (value object) — `(x, y, theta)`

### Value Objects
- `Waypoint`, `PathSegment`, `Velocity`, `MapMetadata`

### Servisler
- `RoutePlanner` — A*/Dijkstra üstüne ek (Nav2 ile fiili kullanır ama bu domain'de soyutlanır)
- `PathFollower` — rota üzerindeki sapmayı ölçer

### Komutlar
- `BuildMap()`, `SaveMap(name)`, `LoadMap(name)`
- `DefineRoute(graph)`
- `NavigateTo(node_id)`
- `Stop()`, `Resume()`

### Yayınladığı Event'ler
- `MapBuilt`, `RouteDefined`, `PathReady(path)`, `WaypointReached`, `PathDeviationDetected(meters)`, `NavigationFailed(reason)`, `RobotPoseUpdated`

### Dinlediği Event'ler
- `ObstacleDetected` → durakla
- `EmergencyStopActivated` → komut akışını kes

---

## 3. Perception Context (`domain/perception/`)

**Amaç:** Kameradan QR, ArUco, çizgi tespiti; LIDAR'dan engel tespiti.

### Agregalar
- `PerceptionScene` — anlık sahnedeki tespitler

### Value Objects
- `QrDetection(id, pose_camera, confidence)`
- `LineFeature(centerline, slope)`
- `Obstacle(distance, angle, classification)`

### Servisler
- `QrDetector` — pyzbar + ArUco kombinasyonu
- `LineFollowerVision` — HSV + contour tabanlı şerit tespiti
- `ObstacleDetector` — LIDAR scan üzerinde polar kuşak filtresi

### Yayınladığı Event'ler
- `QrCodeDetected(qr_id, pose)`
- `LineDetected(centerline_offset)`
- `LineLost()`
- `ObstacleDetected(distance, angle)`
- `ObstacleCleared()`

### Dış Bağımlılıklar
- `CameraDriver` (infrastructure adapter)
- `LidarDriver` (infrastructure adapter)

---

## 4. Safety Context (`domain/safety/`)

**Amaç:** E-stop, manuel/otomatik mod, hız/sapma limitleri, güvenli durdurma. **Diğer her context'in üstünde veto hakkı vardır.**

### Agregalar
- `SafetyState` — mode (`AUTO` | `MANUAL`), e-stop aktif mi, son ihlal

### Komutlar
- `EngageEStop()`, `ReleaseEStop()`
- `SwitchMode(mode)` — anahtarın fiziksel konumundan tetiklenir

### Yayınladığı Event'ler
- `EmergencyStopActivated`, `EmergencyStopReleased`
- `ModeSwitched(mode)`
- `SafetyViolationDetected(kind)` — örn. hız aşımı, sapma aşımı

### Kurallar (Invariant)
- `MANUAL` modda otonom hareket komutları **bloklanır**.
- E-stop aktifken tüm hareket komutları reddedilir.
- Anahtar fiziksel konumu (donanım giriş) tek doğrudur; yazılım override edemez.

---

## 5. Fleet I/O Context (`domain/fleet_io/`)

**Amaç:** Fabrika otomasyon sistemi (PLC) ile haberleşme; protokol-bağımsız domain modeli.

### Agregalar
- `PlcSession` — bağlantı yaşam döngüsü
- `MessageJournal` — gönderilen/alınan tüm mesajların kaydı (GUI'de gösterilecek)

### Value Objects
- `PlcMessage(direction, payload, timestamp)`
- `DoorRequest`, `DoorGrant`, `PickAssignment`, `MissionComplete`

### Komutlar
- `Connect()`, `Disconnect()`
- `RequestDoorOpen(node_id)`
- `NotifyArrived(node_id)`, `NotifyLoadDropped()`, `NotifyAtHome()`

### Yayınladığı Event'ler
- `PlcConnected`, `PlcDisconnected`
- `PickAssignmentReceived(pickup, dropoff)`
- `DoorGrantReceived(node_id)`
- `PlcMessageSent`, `PlcMessageReceived`

### Adapter
- `PlcGateway` (port) — `infrastructure/plc/` altında **modbus_tcp**, **opc_ua**, **raw_tcp** üç adapter

---

## 6. Telemetry Context (`domain/telemetry/`)

**Amaç:** Tüm event'leri dinleyip log/metric/UI'ye ileten read-only context.

### Servisler
- `TelemetryRecorder` — tüm event'leri JSONL'a kaydeder
- `StatusProjector` — agrega read-model: GUI için tek `RobotSnapshot` üretir

### Value Objects
- `RobotSnapshot` — şu anki durum, görev, son QR, PLC durumu, batarya, pose

### Read Model
GUI tarafına push edilen tek doğru tablo:
```python
@dataclass
class RobotSnapshot:
    status: RobotStatus
    mission: Optional[MissionView]
    last_qr: Optional[str]
    plc_connected: bool
    plc_last_message: Optional[str]
    pose: Pose
    battery_pct: float
    mode: Mode
    emergency: bool
    map_name: Optional[str]
```

---

## Context-Context Etkileşim Kuralları

1. **Asla doğrudan import yok.** Bir context başka birinin entity'sini import etmez.
2. **Sadece event üzerinden konuşulur.** Veya **anti-corruption layer** üzerinden DTO ile.
3. **Komutlar yalnızca application katmanından gelir.**
4. **Telemetry read-only** — hiçbir context'e komut göndermez, yalnız okur.
5. **Safety override hakkına sahiptir** — `EmergencyStopActivated` event'ini herkes dinlemek **zorundadır**.

## Klasör Karşılığı

```
src/cargobot/domain/
├── mission/         # bounded context 1
│   ├── aggregate.py
│   ├── events.py
│   ├── value_objects.py
│   └── services.py
├── navigation/      # 2
├── perception/      # 3
├── safety/          # 4
├── fleet_io/        # 5
└── telemetry/       # 6
```
