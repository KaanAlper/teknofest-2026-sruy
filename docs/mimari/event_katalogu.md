# Domain Event Kataloğu

> Tüm event'ler **geçmiş zaman**la isimlendirilir (`-ed` / `-d` / `-Detected`). Her event immutable; `@dataclass(frozen=True)`.

## Ortak Şema

```python
@dataclass(frozen=True)
class DomainEvent:
    event_id: UUID
    occurred_at: datetime
    aggregate_id: str
    correlation_id: Optional[UUID] = None  # bir sagaya bağlı event'ler için
```

## 1. Mission Events

| Event | Payload | Tetikleyen | Dinleyenler |
|---|---|---|---|
| `MissionAssigned` | pickup_node, dropoff_node | Fleet I/O | Mission, Telemetry |
| `MissionStarted` | mission_id, pickup, dropoff | Mission | Navigation, UI |
| `MissionPhaseChanged` | mission_id, from, to | Mission | UI, Telemetry |
| `LoadPicked` | mission_id, node, qr_id | Mission | Navigation, UI, Fleet I/O |
| `LoadDropped` | mission_id, node | Mission | Fleet I/O, UI |
| `MissionCompleted` | mission_id, duration | Mission | Fleet I/O, Telemetry |
| `MissionAborted` | mission_id, reason | Mission | All |
| `MissionGenericError` | mission_id, code, detail | Mission | UI, Telemetry |

### MissionPhase Geçişleri
```
RECEIVED ──► PLANNING ──► MOVING_TO_PICKUP ──► APPROACHING_LOAD ──► PICKING
   │                                                                    │
   │                                                                    ▼
   │              MOVING_TO_DROPOFF ◄── AT_DOOR ◄── MOVING_TO_DOOR ◄──┘
   │                     │
   │                     ▼
   │              APPROACHING_DROP ──► DROPPING ──► RETURNING_TO_DOOR
   │                                                       │
   │                                                       ▼
   └─────────────────────────────────────────────► RETURNING_HOME ──► COMPLETED
```

---

## 2. Navigation Events

| Event | Payload |
|---|---|
| `MapBuilt` | map_name, dimensions, resolution |
| `RouteDefined` | graph_summary (#nodes, #edges) |
| `PathReady` | mission_id, waypoints[] |
| `WaypointReached` | mission_id, waypoint_id |
| `PathDeviationDetected` | meters_off |
| `RobotPoseUpdated` | x, y, theta, frame |
| `NavigationFailed` | reason |
| `NavigationStopped` | reason (`obstacle` / `estop` / `command`) |
| `NavigationResumed` | — |

---

## 3. Perception Events

| Event | Payload |
|---|---|
| `QrCodeDetected` | qr_id, pose_camera, confidence |
| `ArucoMarkerDetected` | marker_id, pose_6dof |
| `LineDetected` | centerline_offset_px, slope_deg |
| `LineLost` | last_offset |
| `ObstacleDetected` | distance_m, angle_rad |
| `ObstacleCleared` | — |

---

## 4. Safety Events

| Event | Payload |
|---|---|
| `EmergencyStopActivated` | source (`button` / `software` / `lidar_safety`) |
| `EmergencyStopReleased` | — |
| `ModeSwitched` | mode (`AUTO` / `MANUAL`) |
| `SafetyViolationDetected` | kind, value, limit |

---

## 5. Fleet I/O Events

| Event | Payload |
|---|---|
| `PlcConnected` | host, port, protocol |
| `PlcDisconnected` | reason |
| `PickAssignmentReceived` | pickup, dropoff (Mission'a dönüşür) |
| `DoorGrantReceived` | node_id |
| `PlcMessageSent` | raw, parsed |
| `PlcMessageReceived` | raw, parsed |
| `PlcTimeout` | last_request |

---

## 6. Telemetry / System

| Event | Payload |
|---|---|
| `BatteryLevelChanged` | percent |
| `BatteryLow` | percent (eşik altı, otomatik şarj tetikler) |
| `ChargingStarted` | station_id |
| `ChargingCompleted` | end_pct |
| `SystemStarted` | version |
| `SystemShuttingDown` | reason |

---

## 7. UI'den Gelen Komutlar (Event Değil — Command)

> Komutlar **emir kipindeki** isimle, **şimdiki zaman**:

| Command | Hedef Context |
|---|---|
| `BuildMapCommand` | Navigation |
| `SaveMapCommand(name)` | Navigation |
| `DefineRouteCommand(graph)` | Navigation |
| `ManualDriveCommand(linear, angular)` | Safety → Navigation |
| `EngageEStopCommand` | Safety |
| `ReleaseEStopCommand` | Safety |
| `ConnectPlcCommand` | Fleet I/O |
| `StartChargingCommand` | Telemetry/Charge |

---

## Event Bus Sözleşmesi

```python
class AsyncEventBus:
    async def publish(self, event: DomainEvent) -> None: ...
    def subscribe(
        self,
        event_type: Type[DomainEvent],
        handler: Callable[[DomainEvent], Awaitable[None]],
    ) -> SubscriptionToken: ...
    def unsubscribe(self, token: SubscriptionToken) -> None: ...
```

**Garantiler:**
- Aynı event tek bir publish'te birden fazla handler'a paralel dağıtılır
- Handler exception'ları diğer handler'ları durdurmaz, telemetry'ye yazılır
- Event sıralaması publish çağrı sırasıyla aynı; sıkı sıralama garantisi **yok** (handler'lar async)

## Korelasyon

Bir kullanıcı/PLC isteği bir `correlation_id` üretir; o istekten doğan tüm event'ler aynı id'yi taşır. Debug'ı feci derecede kolaylaştırır.

```python
async def start_mission_use_case(cmd: StartMissionCommand):
    cid = uuid4()
    with correlation_context(cid):
        await bus.publish(MissionAssigned(..., correlation_id=cid))
        # ...
```
