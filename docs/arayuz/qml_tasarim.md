# QML arayüz tasarımı

Şartname Tablo-4'te GUI için +20 puan var. Buna karşılık eksik her bilgi −4. Bu yüzden Dashboard'da kritik alanlar tek bakışta görünmeli, alt sayfa açmaya gerek kalmamalı.

## 1. Tasarım İlkeleri

- **Dark theme** + yüksek kontrast (saha ışığı zorlayıcı olabilir)
- **Tek tıkla erişim** — yarışma stresi altında menü gezme zaman kaybı
- **Renkler:**
  - Yeşil = OK / bağlı / hareket
  - Sarı = bekliyor / uyarı (PLC komut bekleme)
  - Kırmızı = hata / e-stop / kayıp
  - Mavi = bilgi / haritalama
- **Yazı tipi:** Inter veya IBM Plex Sans (sayılar tabular)
- **Yenileme oranı:** snapshot 10 Hz, harita 5 Hz, log streaming

## 2. Sayfa Hiyerarşisi

```
ApplicationWindow
├── SideBar (sabit, 60 px ikon kolonu)
│   ├── Dashboard
│   ├── Map
│   ├── PLC Log
│   ├── Manual Control
│   └── Settings
│
├── HeaderBar (40 px, üst, durum şeridi)
│   ├── Robot durumu badge (büyük, animasyonlu)
│   ├── PLC bağlantı LED'i
│   ├── WiFi sinyal göstergesi
│   ├── Mod (AUTO/MANUAL)
│   └── Saat / sayaç
│
├── StackView (ana içerik)
│
└── FooterBar (30 px, alt, log akışı / hata banner)
```

## 3. Dashboard Sayfası (varsayılan)

```
┌────────────────────────────────────────────────────────────────────┐
│ HeaderBar: [● IDLE]  [PLC ●]  [WiFi ▰▰▰▰]  [AUTO]    12:34:56     │
├────────┬──────────────────────────────────────────────┬────────────┤
│        │                                              │            │
│  Side  │   ┌─────────────────────────────────────┐    │  Görev     │
│  bar   │   │                                     │    │  Paneli    │
│        │   │       MAP CANVAS (canlı)            │    │            │
│ [Das]  │   │         (robot ikonu + rota)        │    │ Pickup:    │
│ [Map]  │   │                                     │    │   P2       │
│ [Log]  │   └─────────────────────────────────────┘    │ Dropoff:   │
│ [Man]  │                                              │   D1       │
│ [Set]  │  ┌───────────────────────────────────┐       │ Faz:       │
│        │  │ Son QR: "P2-PALLET-A"             │       │   APPROACH │
│        │  │ Okuma zamanı: 12:34:50            │       │   _LOAD    │
│        │  │ Pose: x=3.21  y=1.43  θ=89.4°    │       │            │
│        │  └───────────────────────────────────┘       │ Süre:      │
│        │                                              │   05:12    │
│        │  ┌──────────────────┐  ┌────────────────┐    │ Hedef:     │
│        │  │ Batarya  87%     │  │  Hız 0.22 m/s  │    │   30:00    │
│        │  │ [████████░░]    │  │  Sapma 2.3 cm  │    │            │
│        │  └──────────────────┘  └────────────────┘    │ [Görev Du] │
│        │                                              │ [Pause]    │
├────────┴──────────────────────────────────────────────┴────────────┤
│ Footer: [PLC ◄ door_grant(q5)]  ...  [ERR: lidar dropped 1 frame] │
└────────────────────────────────────────────────────────────────────┘
```

## 4. Harita Sayfası

- Tam ekran harita canvas (PGM dosyasını Image overlay ile)
- Üzerinde:
  - Rota düğümleri (renk-kodlu: pickup yeşil, dropoff mavi, kapı sarı, bekleme gri)
  - Rota kenarları (çizgi)
  - Canlı robot pose (ok ikonu, yön gösterir)
  - LIDAR scan halkası (canlı, kırmızı noktalar)
  - Engel uyarı dairesi
- Sol alt toolbar:
  - [Yeni Harita] · [Kaydet] · [Yükle] · [Rota Çiz] · [Düğüm Ekle] · [Sil]

## 5. PLC Log Sayfası

İki kolon split:

```
┌─ Sol: Bağlantı bilgisi ──────┬─ Sağ: Mesaj akışı (QListView) ────┐
│ Host:    192.168.1.10:502    │ ► 12:34:50 TX door_request{q5}   │
│ Protocol: Modbus TCP         │ ◄ 12:34:51 RX door_grant{q5}     │
│ Durum:   ● Bağlı             │ ► 12:34:52 TX arrived{p1}        │
│ Latency: 12 ms               │ ► 12:35:01 TX pick_done{p1}      │
│ TX/sec:  3.2                 │ ...                              │
│ Hata:    0                   │                                  │
│                              │ [Otomatik kaydır ☑]              │
│ [Yeniden Bağlan]             │ [Filtre: TX | RX | ALL]          │
│ [Kopart]                     │ [Dışa aktar]                     │
└──────────────────────────────┴──────────────────────────────────┘
```

## 6. Manuel Kontrol Sayfası

- Sadece **anahtar MANUAL konumunda** aktif (yoksa overlay "AUTO modda — anahtarı MANUAL'a alın")
- Sol: 2D joystick (linear/angular hız)
- Sağ:
  - Forklift yukarı/aşağı
  - Aktüatör pozisyon barı
  - Acil dur (yazılım E-stop)
  - Hız limiti slider (0–1 m/s)
- Telemetri: anlık `cmd_vel`, motor akımı

## 7. Settings Sayfası

- Bağlantı: Robot IP, port
- PLC: protokol seç (modbus/opcua/raw), host:port, kayıt eşlemesi
- Konfig dosyası yükle/kaydet
- Loglama seviyesi
- Tema (dark/light)
- Dil (TR/EN)

## 8. QML ↔ Python Köprüsü

### Singleton bağlam:
```python
# src/ui/app_context.py
class AppContext(QObject):
    snapshotChanged = Signal()           # her snapshot güncellemesinde
    plcMessageReceived = Signal('QVariant')
    mapImageChanged = Signal('QUrl')
    
    @Property('QVariant', notify=snapshotChanged)
    def snapshot(self) -> dict:
        return self._snapshot.asdict()
    
    @Slot(str)
    def sendCommand(self, command_json: str): ...
```

QML:
```qml
import CargoBot 1.0

ApplicationWindow {
    visible: true
    width: 1366; height: 768
    title: "CargoBot Operatör Panel"
    
    Component.onCompleted: AppContext.connect()  // WebSocket bağlan
    
    Connections {
        target: AppContext
        function onSnapshotChanged() {
            statusBadge.text = AppContext.snapshot.status
            batteryGauge.value = AppContext.snapshot.battery_pct
        }
    }
    // ...
}
```

### List model (PLC mesajları):
```python
class PlcLogModel(QAbstractListModel):
    DirectionRole = Qt.UserRole + 1
    TimestampRole = Qt.UserRole + 2
    PayloadRole = Qt.UserRole + 3
    
    def roleNames(self): ...
    def rowCount(self, parent=QModelIndex()): ...
    def data(self, index, role): ...
    
    @Slot('QVariant')
    def append(self, message: dict): ...
```

QML:
```qml
ListView {
    model: PlcLogModel
    delegate: PlcMessageItem {
        direction: model.direction
        timestamp: model.timestamp
        payload: model.payload
    }
}
```

## 9. Bağlantı (WebSocket)

```python
# src/ui/viewmodels/connection.py
import asyncio, json, websockets
from PySide6.QtCore import QObject, Signal, Slot, QThread

class WSWorker(QThread):
    snapshotReceived = Signal(dict)
    plcMessageReceived = Signal(dict)
    
    def __init__(self, url):
        super().__init__()
        self.url = url
    
    def run(self):
        asyncio.run(self._main())
    
    async def _main(self):
        async with websockets.connect(self.url) as ws:
            async for msg in ws:
                data = json.loads(msg)
                if data["type"] == "snapshot":
                    self.snapshotReceived.emit(data["payload"])
                elif data["type"] == "plc_message":
                    self.plcMessageReceived.emit(data["payload"])
```

## 10. Karşı Şartname Eksiklik Kontrol Listesi (CI'a koy)

Aşağıdaki her bilgi snapshot'ta **doğrulanır**; eksik olursa CI fail:

- [x] `status` (8 enum'dan biri)
- [x] `mission.pickup`, `mission.dropoff`, `mission.phase`
- [x] `last_qr.id`, `last_qr.timestamp`
- [x] `plc.connected`
- [x] `plc.last_tx`, `plc.last_rx`
- [x] `pose.x`, `pose.y`, `pose.theta`
- [x] `battery_pct`
- [x] `mode` (AUTO/MANUAL)
- [x] `emergency` (bool)

`tests/integration/test_ui_information_completeness.py` snapshot tüm anahtarları içermezse fail eder.

## 11. Wireframe Çıktıları
- `docs/arayuz/wireframes/dashboard.png` — Figma'da çizilecek (ekibe görev)
- `docs/arayuz/wireframes/map.png`
- `docs/arayuz/wireframes/plc_log.png`
- `docs/arayuz/wireframes/manual.png`

## 12. Erişilebilirlik
- Tüm interaktif elemanlar klavye ile erişilebilir (Tab + Enter)
- E-stop tuşu **Space veya ESC** ile tetiklenebilir
- Yüksek kontrast modu (sahada güneş yansıması durumunda)
