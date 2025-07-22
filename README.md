# Raspberry Pi Pico W Weather Station

A modular, professional weather monitoring project using the Raspberry Pi Pico W with OLED display, DHT22 sensor, and web interface.

## Features

- 🌡️ **Real-time monitoring** - Temperature, humidity, and WiFi signal strength
- 📺 **OLED display** - Local weather readings on 128x64 SSD1306 display
- 🌐 **Web interface** - Remote monitoring via HTTP server
- 📡 **WiFi connectivity** - Automatic connection with status feedback
- 💡 **LED indicators** - Visual status for startup, connection, and errors
- 🔧 **Modular architecture** - Clean, maintainable code structure
- 🎓 **Workshop ready** - Perfect for educational environments

## Hardware Requirements

- **Raspberry Pi Pico W** - Main microcontroller
- **DHT22 sensor** - Temperature and humidity measurement
- **SSD1306 OLED display** - 128x64 I2C display (common in Arduino kits)
- **Connecting wires** - For sensor and display connections
- **Breadboard** (optional) - For prototyping connections

## Wiring Diagram

```
Raspberry Pi Pico W Connections:

DHT22 Sensor:
├── VCC → 3.3V (Pin 36)
├── GND → Ground (Pin 38)
└── DATA → GP2 (Pin 4)

SSD1306 OLED Display (I2C):
├── VCC → 3.3V (Pin 36)
├── GND → Ground (Pin 38)
├── SCL → GP5 (Pin 7)
└── SDA → GP4 (Pin 6)

Built-in Components:
└── LED → Built-in (automatic)

```

## Quick Setup

### 1. Hardware Connection
Connect components according to the wiring diagram above.

### 2. Software Setup
```bash
# 1. Copy all files to your Pico W
# 2. Create or edit config.py:
SSID = "YourWiFiName"
PASSWORD = "YourWiFiPassword"

# 3. Test OLED display (optional):
# Run: oled_test.py

# 4. Start weather station:
# Run: main.py
```

### 3. Access Your Weather Station
- **Local Display**: Weather readings appear on OLED automatically
- **Web Interface**: Navigate to the IP address shown on display
- **Serial Output**: Monitor status via MicroPython terminal

## Project Structure

```
📁 raspico2/
├── 📄 main.py              # Main application (orchestrates everything)
├── 📄 display_utils.py     # OLED display management & screens
├── 📄 wifi_manager.py      # WiFi connection & network handling
├── 📄 led_controller.py    # LED status indication patterns
├── 📄 web_server.py        # HTTP server for remote monitoring
├── 📄 ssd1306.py          # SSD1306 OLED display driver
├── 📄 oled_test.py        # Simple display test for workshops
├── 📄 config.py           # WiFi credentials (create this file)
└── 📄 README.md           # This documentation
```

## Workshop Usage

### For Students - Testing Display
```python
# Run this first to test your OLED connection:
exec(open('oled_test.py').read())
```

### For Instructors - Key Learning Points
1. **Modular Programming** - Each file has a single responsibility
2. **Hardware Integration** - I2C, GPIO, WiFi protocols
3. **Error Handling** - Connection failures, sensor errors
4. **User Interface** - Both local (OLED) and remote (web) interfaces
5. **Real-time Systems** - Continuous monitoring and updates

## Troubleshooting

### OLED Display Issues
- ❌ **"No I2C devices found"** → Check wiring, ensure SDA/SCL correct
- ❌ **"EIO Error"** → Try disconnecting/reconnecting USB cable
- ❌ **Blank display** → Verify 3.3V power connection

### WiFi Connection Issues  
- ❌ **Status 2** → Wrong password or network security type
- ❌ **Status -3** → Network not found, check SSID spelling
- ❌ **No connection** → Check `config.py` file exists and is correct

### Sensor Issues
- ❌ **"Error reading sensor"** → Check DHT22 wiring to GP2
- ❌ **Constant values** → Sensor may be faulty or poorly connected

## Technical Specifications

- **Operating Voltage**: 3.3V (powered via USB or external)
- **WiFi**: 802.11 b/g/n (2.4GHz)
- **Display**: 128x64 monochrome OLED (I2C)
- **Sensor Range**: Temperature -40°C to +80°C, Humidity 0-100%RH
- **Update Frequency**: 5 seconds for sensor readings
- **Web Server**: HTTP on port 80
- **Memory Usage**: ~50KB RAM, optimized for MicroPython

## Advanced Customization

### Adding New Sensors
Edit `main.py` and create new sensor classes in separate files following the existing pattern.

### Custom Display Screens
Modify `display_utils.py` to add new screens or layouts.

### Web Interface Enhancement
Update `web_server.py` to add new endpoints or improve HTML interface.

---

**Created for educational workshops** • **MicroPython** • **Open Source**