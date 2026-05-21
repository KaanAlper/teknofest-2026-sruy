# Test Stratejisi

## 1. Test Piramidi

```
              ▲
             ╱ ╲
            ╱ E2E ╲          ~5  yarışma senaryosu testleri (saha + sim)
           ╱───────╲
          ╱  Integ  ╲        ~30 PLC, ROS2 köprü, GUI ↔ backend
         ╱───────────╲
        ╱    Unit    ╲       ~150+ domain, value object, event handler
       ╱───────────────╲
```

## 2. Birim Test (Unit) — `tests/unit/`

**Hedef:** Domain ve application katmanı %90+ kapsama.

| Modül | Test alanı |
|---|---|
| `domain/mission/aggregate.py` | Tüm state geçişleri, invariant ihlalleri |
| `domain/navigation/path_planner.py` | Path optimizasyon, döngü engelleme |
| `domain/safety/aggregate.py` | E-stop ve mode invariant'ları |
| `domain/fleet_io/messages.py` | Serializasyon / deserializasyon |
| `application/sagas/*` | Event sequencing, hata yolları |
| `infrastructure/bus/async_bus.py` | Publish, subscribe, exception isolation |

**Araçlar:** `pytest`, `pytest-asyncio`, `hypothesis` (property-based)

**Örnek:**
```python
async def test_mission_cannot_transition_from_idle_to_picking():
    mission = Mission.new("p1", "d1")
    with pytest.raises(InvalidPhaseTransition):
        mission.transition(MissionPhase.PICKING)
```

## 3. Entegrasyon Testi — `tests/integration/`

**Hedef:** Adapter'ların domain ile birleştiği noktalar.

| Test | Açıklama |
|---|---|
| `test_modbus_adapter.py` | Yerel pymodbus server'a karşı message journal akışı |
| `test_opcua_adapter.py` | asyncua server'a karşı node read/write |
| `test_ros2_bridge.py` | rclpy node ile domain event publish |
| `test_ui_information_completeness.py` | Snapshot'ta gerekli **tüm** alanların varlığı (şartname zorunluluğu) |
| `test_websocket_bridge.py` | WS sunucusu + istemci JSON round-trip |
| `test_event_bus_load.py` | 10k event/sn altında handler kaybı yok |

**Önemli özel test:**
```python
def test_snapshot_contains_all_mandatory_ui_fields():
    """Şartname §10 — eksik bilgi başı −4 puan. CI'da hiçbir alan eksik olmamalı."""
    snapshot = make_snapshot()
    required = {
        "status", "mission", "last_qr", "plc_connected",
        "plc_last_tx", "plc_last_rx", "pose", "battery_pct",
        "mode", "emergency",
    }
    assert required.issubset(snapshot.keys())
```

## 4. Simülasyon Testi — `tests/sim/`

**Hedef:** Gazebo'da yarışma senaryosunun tamamı.

| Test | Açıklama |
|---|---|
| `test_full_scenario_sim.py` | Gazebo dünyasında pickup → kapı → dropoff → return |
| `test_obstacle_recovery_sim.py` | Engel kaldı/kalkma davranışı |
| `test_battery_low_charge_sim.py` | Otomatik şarj sagası |
| `test_plc_timeout_recovery_sim.py` | PLC bağlantı koptu/geldi |

**Çalıştırma:** `pytest tests/sim/ --gazebo-world worlds/teknofest_saha.world`

> CI'da Gazebo headless çalıştırılır (Docker + xvfb).

## 5. Saha Testi — Manuel

**Cuma demoları + her sprint sahaya çıkış**

Şablon:
- Senaryo adımı
- Beklenen davranış
- Gözlenen davranış
- Sapma / hata
- Sonraki iyileştirme

`docs/test/saha_log/YYYY-MM-DD.md` formatında dosyala.

## 6. Stres ve Dayanıklılık Testi

- 100 ardışık uçtan uca koşum (atölye), istatistik:
  - Başarı oranı (%) hedef ≥95
  - Ortalama süre, dağılım
  - En kötü hata türü
- WiFi paket kayıp simülasyonu (`tc qdisc add netem loss 5%`)
- PLC yeniden başlatma sırasında robot davranışı

## 7. Kabul Testleri (Acceptance) — Şartname Bazlı

`tests/acceptance/` altında her şartname görevi için bir test:

```
tests/acceptance/
├── test_g1_mapping.py
├── test_g2_route_definition.py
├── test_g3_plc_communication.py
├── test_g4_line_following.py
├── test_g5_qr_detection.py
├── test_g6_obstacle_avoidance.py
├── test_g7_door_passage.py
├── test_g8_user_interface.py
├── test_g9_auto_charging.py
└── test_g10_emergency_stop.py
```

Her test: kabul kriterlerini (`docs/sartname/gorevler_puanlama.md`) **assert** eder.

## 8. CI/CD

`.github/workflows/test.yml`:
```yaml
jobs:
  unit:
    runs-on: ubuntu-22.04
    steps:
      - uses: actions/checkout@v4
      - run: uv sync
      - run: uv run pytest tests/unit
  
  integration:
    runs-on: ubuntu-22.04
    services:
      modbus_sim:
        image: oitc/modbus-server
    steps:
      - run: uv run pytest tests/integration
  
  ui_completeness:
    runs-on: ubuntu-22.04
    steps:
      - run: uv run pytest tests/integration/test_ui_information_completeness.py
  
  lint:
    steps:
      - run: uv run ruff check
      - run: uv run mypy src/
```

## 9. Saha Günü Smoke Testleri

Yarışma sabahı (30 dk):
- [ ] Tüm sensörler online (`/scan`, `/camera`, `/odom`)
- [ ] PLC bağlantı kuruldu
- [ ] Manuel sürüş çalışıyor (her yön)
- [ ] E-stop testi (basıldığında motor durdu)
- [ ] GUI tüm bilgileri gösteriyor
- [ ] Batarya %100
- [ ] Yedek bilgisayar açık, snapshot alıyor

## 10. Hata Tahsil Sistemi

Sahada karşılaşılan her hata `docs/test/hata_kayit.md`'ya yazılır:
- Tarih, saha, senaryo
- Hata tanımı
- Root cause
- Sprint'de çözüm görev kaydı
