# Raspberry Pi Pico 2 W Power Supply Wiring Diagram

## Components Needed

**Power Management:**
- AMS1117-3.3 voltage regulator module
- 2x BAT42 Schottky diodes (30V, 200mA max)
- 2S LiPo battery (7.4V, 1000-2000mAh recommended)
- JST connector for battery (optional)

**Note on Capacitors:**
- Most AMS1117 breakout boards include required capacitors pre-installed
- If using bare AMS1117 IC: 10µF input, 22µF output capacitors needed

## Step-by-Step Wiring Instructions

### Connection Table

| From Component | From Pin/Wire | To Component | To Pin/Wire | Wire Color | Notes |
|----------------|---------------|--------------|-------------|------------|-------|
| **2S LiPo Battery** | RED (+) | **Diode D1** | Anode | Red | Battery positive |
| **2S LiPo Battery** | BLACK (-) | **Common GND** | - | Black | Battery negative |
| **Pico 2 W** | Pin 40 (VBUS) | **Diode D2** | Anode | Red | USB 5V from built-in connector |
| **Pico 2 W** | Pin 38 (GND) | **Common GND** | - | Black | USB/System ground |
| **Diode D1** | Cathode | **Junction Point** | - | Red | From battery |
| **Diode D2** | Cathode | **Junction Point** | - | Red | From USB |
| **Junction Point** | - | **AMS1117** | VIN | Red | Power input |
| **Common GND** | - | **AMS1117** | GND | Black | Ground |
| **AMS1117** | VOUT | **Pico 2 W** | Pin 36 (3V3) | Red | 3.3V output |
| **Common GND** | - | **Pico 2 W** | Pin 38 (GND) | Black | Ground |

### Visual Layout

```
[2S LiPo]     [Pico 2 W Built-in USB]
    |             |
   RED         Pin 40 (VBUS)
    |             |
    └─[D1]   [D2]─┘    D1, D2 = BAT42 Schottky Diodes
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
2. **Pico 2 W Pin 40 (VBUS)** → **Schottky Diode Anode** → **Common Power Point**
3. **Battery GND & Pico Pin 38** → **Common Ground**

### Voltage Regulation:
4. **Common Power Point** → **AMS1117 VIN**
5. **Common Ground** → **AMS1117 GND**
6. **AMS1117 VOUT** → **Pico 2 W Pin 36 (3V3)**

### Pico 2 W Power:
7. **3.3V from AMS1117** → **Pico 2 W Pin 36 (3V3)**
8. **Common Ground** → **Pico 2 W Pin 38 (GND)**

## Diode Selection

**Required Schottky Diodes:**
- **BAT42** (30V, 200mA max, DO-35 package)
- Use BAT42 for both D1 (LiPo line) and D2 (USB VBUS line)

**Purpose of Diodes:**
- Prevents reverse current flow
- Automatically selects higher voltage source
- Protects both USB and battery from damage

## Important Notes

⚠️ **Current Limitation Warning:**
- The BAT42 diode supports only ~200 mA max current
- This setup is suitable for powering the Raspberry Pi Pico 2 W and low-power peripherals only
- Total system current must stay under ~180 mA
- Avoid powering high-draw devices like large displays or motors without upgrading the diode
- Monitor diode temperature on first use to ensure safe operation

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
- Pin 40 (VBUS) - USB voltage input (5V when USB connected)

**Test Points (Bottom of Board):**
- TP1 - Ground (USB differential signal ground)
- TP2 - USB Data Minus (DM) 
- TP3 - USB Data Plus (DP)
- Note: TP1-3 are for USB data signals, not power