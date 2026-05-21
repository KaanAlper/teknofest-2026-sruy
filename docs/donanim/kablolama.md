# Güç ve Sinyal Kablolama — CargoBot

## Güç Dağıtım Şeması

```
                           ┌──────────────────────┐
                           │  LiFePO4 12.8V 20Ah │
                           └──────────┬───────────┘
                                      │ (BMS arkası)
                                      │
                           ┌──────────▼─────────┐
                           │  Ana sigorta 20A   │
                           └──────────┬─────────┘
                                      │
                ┌─────────────────────┼─────────────────────┐
                │                     │                     │
        ┌───────▼────────┐    ┌───────▼────────┐    ┌──────▼─────────┐
        │ E-stop röle    │    │ DC-DC 12→5V 5A │    │ Motor sürücü   │
        │ (NC, hat keser)│    │ (Pi/STM/IMU)   │    │ kart × 2       │
        └───────┬────────┘    └────────────────┘    └────────────────┘
                │
        ┌───────▼────────┐    ┌────────────────┐
        │ DC-DC 12→19V   │    │ DC-DC 12→6V 5A │
        │ (Jetson)       │    │ (Servolar)     │
        └────────────────┘    └────────────────┘
```

## E-Stop Kuralları

- **Mantar buton (NC)** seri olarak motor güç hattının kalbinde
- **Anahtar (3 konum)**: AUTO / OFF / MANUAL — anahtar OFF iken motor gücü kesik
- **Yazılım E-stop**: STM32 → motor sürücüsü EN pinine LOW (yazılım, donanımı **geçemez**)
- Donanım > Yazılım önceliği: Buton/anahtar kesince, yazılım veto edemez.

## Sinyal Ağı

```
Jetson Orin Nano (Ubuntu 22.04 + ROS2 Humble)
 ├─ USB3 ── LIDAR (YDLIDAR)
 ├─ USB3 ── RealSense D435i
 ├─ USB ── ESP32 (sensör hub: IMU, bumper, batarya monitör)
 ├─ USB ── STM32 (motor sürücü, enkoder okuma, e-stop bus)
 ├─ Ethernet ── (geliştirme PC)
 └─ WiFi ── Saha ağı

STM32 (motor + güvenlik)
 ├─ PWM × 4 ── Motor sürücü A/B kanal × 2
 ├─ ENC × 2 ── Optik enkoderler
 ├─ GPIO ── E-stop algılama (buton durumu)
 ├─ GPIO ── Anahtar konumu (AUTO/MANUAL)
 ├─ GPIO ── Forklift servo (PWM)
 └─ UART ── Jetson

ESP32 (sensör hub)
 ├─ I2C ── BNO055 IMU
 ├─ I2C ── INA219 akım/voltaj sensörü (batarya monitör)
 ├─ GPIO ── 4× bumper switch
 ├─ Trigger ── 2× HC-SR04
 └─ USB-Serial ── Jetson (micro-ROS köprüsü)
```

## Topraklama
- Tek nokta topraklama (`star ground`) — güç ve sinyal toprağı sigortadan sonra tek noktada birleşir
- Motor sürücü EMI için akım hatları kısa, sinyal hatları akım hatlarından **en az 5 cm uzakta**
- Motor kablolarına ferrit boncuk

## Yerlilik PCB Tasarımı

`hardware/schemas/sensor_hub_yerli.kicad_pcb` (planlanmış):
- ESP32-S3 + INA219 + 4 bumper girişi + I2C breakout
- Türkiye'de PCB üretimi (örn. PCBway TR partner veya Şimşek Elektronik)
- BOM içinde "yerli üretim" olarak belgelenir → +5 puan
