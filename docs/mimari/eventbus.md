# EventBus ve Modüller Arası Bağlantı

Sistem tek bir asyncio publish/subscribe veriyolu üstüne kurulu. Her modül yalnız iki şey yapıyor:

1. **Kendi event'ini kendi `events.py`'sinde tanımlar.**
2. Bilgiyi başka modüllerin de bilmesi gerekiyorsa **bus üzerinden publish eder**. Dinleyen taraf `subscribe` olur. Doğrudan import edip fonksiyon çağırmak yok.

## Klasör

```
domain/mission/events.py        # MissionStarted, MissionPhaseChanged, ...
domain/navigation/events.py     # WaypointReached, NavigationStopped, ...
domain/perception/events.py     # QrCodeDetected, ObstacleDetected, ...
domain/safety/events.py         # EmergencyStopActivated, ...
domain/fleet_io/events.py       # PickAssignmentReceived, DoorGrantReceived, ...

infrastructure/bus/async_bus.py # AsyncEventBus

application/handlers/*.py       # her bounded context'in handler factory'leri
application/wiring.py           # << kim hangi event'i dinliyor — tek liste
application/bootstrap.py        # App.build: bus + deps composition root
```

## Yayınlama (publisher)

Saf domain agregaları bus'ı bilmiyor; tıpkı bir kuyruğa atar gibi `collect_events()` ile event biriktiriyor. Handler agregayı çağırıp event'leri toplar ve bus'a iletir:

```python
# domain/mission/aggregate.py — bus'ı bilmez
class Mission:
    def transition(self, to_phase):
        ...
        self._pending.append(MissionPhaseChanged(...))

    def collect_events(self):
        events, self._pending = self._pending, []
        return events

# application/handlers/mission_handlers.py
async def _flush(bus, m):
    await bus.publish_many(m.collect_events())
```

Bu ayrım önemli: domain saf Python, test edilmesi kolay, framework'e bağımlı değil. Bus sadece "kabloyu" oynuyor.

Infrastructure adapter'ları (örn. PLC, LIDAR) doğrudan bus'a publish edebilir — kendi sürücü kodu içinde event objesi oluşturup yayar:

```python
# infrastructure/plc/modbus_adapter.py — gelecekte
async def _on_door_grant_register_read(self):
    await self._bus.publish(DoorGrantReceived(aggregate_id="plc", node_id="q5"))
```

## Abone olma (subscriber)

İlgilenen modül bus'tan event tipine subscribe olur:

```python
bus.subscribe(QrCodeDetected, mission_handlers.on_qr_detected(bus))
```

Subscribe edenler `application/wiring.py`'da **tek liste halinde** durur. C++'taki connection manager'ın görevini bu dosya yapıyor. Sınıf değil çünkü Python'da gerek yok; modül seviyesinde fonksiyon yeterli ve okurken `wire()` gövdesinden bakarak hangi event'in kimi tetiklediği tek bakışta anlaşılır.

Decorator tabanlı otomatik kayıt (örn. `@on(QrCodeDetected)`) tercih edilmedi çünkü gizli sihir debug ederken hayatı zorlaştırıyor — özellikle yarışma sahası altında.

## İzin verilen + yasak olan

| ✅ | ❌ |
|---|---|
| `bus.subscribe(QrCodeDetected, handler)` | `from domain.mission import Mission` (domain'ler arası import) |
| Aggregate event biriktirir, handler publish eder | Aggregate doğrudan `bus.publish(...)` |
| Infrastructure adapter doğrudan event publish eder | Infrastructure → infrastructure import |
| Yeni event eklerken kendi context'in `events.py`'sine ekle | Tüm event'leri tek `events.py` dosyasında topla |

## Subclass davranışı

`subscribe(DomainEvent, handler)` tüm event'leri yakalar — telemetry/audit için kullanışlı. `subscribe(MissionPhaseChanged, handler)` sadece o tip için tetiklenir. Bus `issubclass` kontrolüyle çalışır.

## Hata izolasyonu

Bir handler exception fırlatırsa diğerleri etkilenmez — log'a düşer. Bu sayede tek bir bozuk handler tüm akışı kilitlemez.

## Test

```python
from application.bootstrap import App
from application.wiring import wire

app = App.build(plc=MockPlc(), motor=MockMotor())
wire(app.bus, app.deps)

await app.bus.publish(PickAssignmentReceived(aggregate_id="plc", pickup_node="P1", dropoff_node="D1"))
```

`tests/integration/test_eventbus_flow.py` bunu uçtan uca koşturur.
