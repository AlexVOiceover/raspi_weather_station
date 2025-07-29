# Raspberry Pi Pico 2 W Power Supply Wiring Diagram

## Components Needed

**Power Management:**
- AMS1117-3.3 voltage regulator module
- 2x Schottky diodes (BAT54, 1N5819, or similar)
- 2S LiPo battery (7.4V, 1000-2000mAh recommended)
- JST connector for battery (optional)

**Capacitors (if not on AMS1117 module):**
- 10µF capacitor (input)
- 22µF capacitor (output)

## Step-by-Step Wiring Instructions

### Connection Table

| From Component | From Pin/Wire | To Component | To Pin/Wire | Wire Color | Notes |
|----------------|---------------|--------------|-------------|------------|-------|
| **2S LiPo Battery** | RED (+) | **Diode D1** | Anode | Red | Battery positive |
| **2S LiPo Battery** | BLACK (-) | **Common GND** | - | Black | Battery negative |
| **USB Connector** | VCC (+5V) | **Diode D2** | Anode | Red | USB positive |
| **USB Connector** | GND | **Common GND** | - | Black | USB negative |
| **Diode D1** | Cathode | **Junction Point** | - | Red | From battery |
| **Diode D2** | Cathode | **Junction Point** | - | Red | From USB |
| **Junction Point** | - | **AMS1117** | VIN | Red | Power input |
| **Common GND** | - | **AMS1117** | GND | Black | Ground |
| **AMS1117** | VOUT | **Pico 2 W** | Pin 36 (3V3) | Red | 3.3V output |
| **Common GND** | - | **Pico 2 W** | Pin 38 (GND) | Black | Ground |

### Visual Layout

```
[2S LiPo]     [USB Port]
    |             |
   RED           VCC
    |             |
    └─[D1]   [D2]─┘    D1, D2 = Schottky Diodes
         \   /          (Anodes toward sources)
          \ /
      [Junction Point]
           |
        [AMS1117]
      VIN ─┤├─ VOUT
          GND
           |
      [Common GND]
           |
     [Pico 2 W Pins]
     Pin 36 (3V3) ←── VOUT
     Pin 38 (GND) ←── GND
```

## Connection Details

### Power Input Side:
1. **2S LiPo (+)** → **Schottky Diode Anode** → **Common Power Point**
2. **USB VCC (+5V)** → **Schottky Diode Anode** → **Common Power Point**
3. **Both GND** → **Common Ground**

### Voltage Regulation:
4. **Common Power Point** → **AMS1117 VIN**
5. **Common Ground** → **AMS1117 GND**
6. **AMS1117 VOUT** → **Pico 2 W Pin 36 (3V3)**

### Pico 2 W Power:
7. **3.3V from AMS1117** → **Pico 2 W Pin 36 (3V3)**
8. **Common Ground** → **Pico 2 W Pin 38 (GND)**

## Diode Selection

**Recommended Schottky Diodes:**
- **BAT54** (30V, 200mA, SOD-523 package)
- **1N5819** (40V, 1A, DO-41 package) - Easier to solder
- **SS14** (40V, 1A, SMA package)

**Purpose of Diodes:**
- Prevents reverse current flow
- Automatically selects higher voltage source
- Protects both USB and battery from damage

## Important Notes

⚠️ **Safety Warnings:**
- Always connect GND first, power last
- Double-check polarity before connecting battery
- Use fuse/protection on battery positive line (optional but recommended)

✅ **Operation:**
- USB plugged in: Runs from USB (battery disconnected by diode)
- USB unplugged: Runs from battery through AMS1117
- Automatic switching, no manual intervention needed

🔧 **Testing:**
- Measure 3.3V at Pico Pin 36 before connecting other components
- Current draw should be ~20-80mA for Pico 2 W alone
- Battery voltage should not appear at USB connector

## Pin Reference

**Raspberry Pi Pico 2 W Power Pins:**
- Pin 36 (3V3) - 3.3V Power Input
- Pin 38 (GND) - Ground
- Pin 39 (VSYS) - System voltage (not used in this design)
- Pin 40 (VBUS) - USB voltage (not used in this design)