# Senaryo Sekans Diyagramları

> Şartname senaryosundaki kritik akışların adım-adım davranışı. ASCII formatında — Mermaid/PlantUML çevirisi sonradan yapılır.

## S1 — Sistem Açılışı ve PLC El Sıkışması

```
GUI            App           Mission       Safety        FleetIO         PLC
 │              │              │              │              │             │
 │  start ────► │              │              │              │             │
 │              │── ConnectPlc ───────────────────────────► │             │
 │              │              │              │              │── TCP ────► │
 │              │              │              │              │◄── ACK ──── │
 │              │              │              │              │── handshake►│
 │              │              │              │              │◄── ready ── │
 │              │◄─ PlcConnected (event) ───────────────────│             │
 │◄── snapshot.plc_connected=true ───────────────────────────             │
 │              │── Initialize ►│              │              │             │
 │              │              │── status:IDLE►│              │             │
 │◄── snapshot.status=IDLE ──────────────────────────────────             │
```

---

## S2 — Haritalama Modu (Saha Öncesi 60 dk)

```
GUI                  App                  Navigation              SLAM(ROS2)
 │                    │                       │                      │
 │── BuildMap ──────► │                       │                      │
 │                    │── start_slam ───────► │                      │
 │                    │                       │── launch ──────────► │
 │                    │◄── MapBuildingStarted │                      │
 │                    │                       │                      │
 │  (operatör manuel sürer; LIDAR scan'leri SLAM tarafından işlenir)│
 │                    │                       │◄── map_grid ────────│
 │                    │                       │◄── pose ────────────│
 │◄── canlı harita preview (10 Hz) ──────────│                      │
 │                    │                       │                      │
 │── SaveMap("saha1")►│                       │                      │
 │                    │── save ─────────────► │                      │
 │                    │                       │── save_yaml + pgm ──►│
 │                    │◄── MapBuilt(saha1) ───│                      │
 │◄── snapshot.map="saha1" ───────────────────                       │
```

---

## S3 — Rota Tanımlama

```
GUI                     App                 Navigation
 │                        │                     │
 │── DefineRoute(graph) ► │                     │
 │                        │── persist ────────► │
 │                        │                     │── validate (yön,id) ─┐
 │                        │                     │◄────────────────────┘
 │                        │◄── RouteDefined ────│
 │◄── snapshot.route_ready=true ──────────────────
```

Graph payload:
```yaml
nodes:
  - {id: home, type: idle, x: 0.0, y: 0.0, theta: 0.0}
  - {id: p1, type: pickup, x: 3.2, y: 1.4, theta: 90.0}
  - {id: q5, type: door_request, x: 5.0, y: 3.0, theta: 0.0}
  - {id: d1, type: dropoff, x: 8.0, y: 5.0, theta: 180.0}
edges:
  - {from: home, to: p1, cost: 4.2}
  - {from: p1, to: q5, cost: 5.7}
  - {from: q5, to: d1, cost: 3.4}
```

---

## S4 — Tam Yarışma Senaryosu

```
PLC          FleetIO       Mission       Navigation     Perception    Safety
 │              │             │              │              │            │
 │ PickAssign──►│             │              │              │            │
 │              │── event ───►│              │              │            │
 │              │             │── plan ────► │              │            │
 │              │             │              │── path ──────┐            │
 │              │             │◄── PathReady │              │            │
 │              │             │              │              │            │
 │              │             │── move(home→p1) ────►       │            │
 │              │             │              │              │            │
 │              │             │              │ ◄── WaypointReached(q-pre-p1)
 │              │             │              │              │            │
 │              │             │              │      ◄── QrCodeDetected(p1)
 │              │             │              │      ◄── LineDetected   │
 │              │             │── ApproachLoad ►              │         │
 │              │             │   (PID line follow + slow)    │         │
 │              │             │              ◄── WaypointReached(p1)   │
 │              │             │── PickLoad ──►                            │
 │              │             │   (forklift up, 2 sn bekle)              │
 │              │             │◄── LoadPicked                            │
 │              │◄── event ─────────────────────                          │
 │◄── pickConfirmed─│         │              │              │            │
 │              │             │              │              │            │
 │              │             │── move(p1→q5) ─►            │            │
 │              │             │              ◄── WaypointReached(q5)    │
 │              │             │── RequestDoorOpen ──►        │            │
 │              │── DoorReq──►│              │              │            │
 │◄────────────│             │              │              │            │
 │              │             │              │              │            │
 │ doorGrant──►│             │              │              │            │
 │              │── event ───►│              │              │            │
 │              │             │── resume ────►│              │            │
 │              │             │── move(q5→d1) ►              │            │
 │              │             │              ◄── QrCodeDetected(d1)     │
 │              │             │── ApproachDrop ►              │           │
 │              │             │── DropLoad ──►                            │
 │              │             │◄── LoadDropped                            │
 │              │◄── event ─────────────────                              │
 │◄── dropConfirmed │         │              │              │            │
 │              │             │── return ────►│              │            │
 │              │             │   (dönüşte tekrar kapı diyaloğu)         │
 │              │             │── reach home │              │            │
 │              │             │── MissionCompleted ►                      │
 │              │◄── event ───│              │              │            │
 │◄── completed ─│             │              │              │            │
```

---

## S5 — Engelle Karşılaşma

```
LIDAR ── scan ── Perception ── ObstacleDetected ──► Navigation
                                                       │
                                                       ▼ (Nav2 local planner durur)
                                                  velocity=0
                                                       │
                                Navigation ── NavigationStopped(reason=obstacle) ──► Mission
                                                       │
                                Mission ── status=WAITING_OBSTACLE ──► UI
                                                       │
LIDAR ── (engel kalktı) ── Perception ── ObstacleCleared ──► Navigation
                                                       │
                                                  velocity=resume
                                                       │
                                Navigation ── NavigationResumed ──► Mission
                                                       │
                                Mission ── status=MOVING_* (eski) ──► UI
```

---

## S6 — Acil Stop (Donanım Buton)

```
HW E-stop ── GPIO interrupt ── Safety: EngageEStop()
                                    │
                                    ├── publish EmergencyStopActivated
                                    │
                  Tüm context'ler ────► komut akışlarını dondur
                                    │
                                    ├── Motor driver: velocity=0
                                    └── UI: status=EMERGENCY_STOP (kırmızı banner)

Operatör butonu sıfırlar ── Safety: ReleaseEStop()
                                    │
                                    └── publish EmergencyStopReleased
                                                  │
                                                  └── Mission: status=IDLE (yeniden başlat)
```

---

## S7 — Otomatik Şarj (+5)

```
TelemetryRecorder ── BatteryLevelChanged(19%) ──► (eşik altı)
                              │
                              └── publish BatteryLow(19)
                                          │
                  Mission dinler ──► aktif görev varsa:
                                       - yük taşıyorsa: bırakma noktasına git, bırak, sonra
                                       - yüksüz: doğrudan şarj noktasına
                                          │
                                          ▼
                                  Navigation: NavigateTo(dock_station)
                                          │
                                          ▼
                                  ChargeService: dock + start charge
                                  publish ChargingStarted
                                          │
                                          ▼ (batarya %95)
                                  publish ChargingCompleted
                                  Mission: status=IDLE
```

---

## S8 — Manuel Mod Anahtarı

```
HW Switch ── GPIO ── Safety: SwitchMode(MANUAL)
                              │
                              └── publish ModeSwitched(MANUAL)
                                          │
                                          ▼
              UI ── joystick aktif ── ManualDriveCommand
                              │
                              ▼
                  Safety: izin verir (mode==MANUAL) ─► Navigation/motor driver: velocity uygula
                              │
                              ▼
                  AUTO modda gelen ManualDriveCommand REDDEDİLİR (loglanır)
```
