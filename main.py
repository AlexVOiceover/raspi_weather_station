# FAC Weather Station - Refactored Main File
from machine import Pin, I2C
import dht
import time
import ssd1306
import sys

# Import our modular components
from display_utils import DisplayManager
from wifi_manager import WiFiManager
from led_controller import LEDController
from web_server import WeatherWebServer

# Hardware Configuration
sensor = dht.DHT22(Pin(2))
i2c = I2C(0, sda=Pin(4), scl=Pin(5), freq=400000)
oled_display = ssd1306.SSD1306_I2C(128, 64, i2c)

# Initialize managers
led = LEDController()
display = DisplayManager(oled_display)

# Show startup message and LED sequence
display.show_startup_message()
led.startup_sequence()

# Load WiFi configuration
try:
    from config import SSID, PASSWORD

    ssid, password = SSID, PASSWORD
except ImportError:
    print("Error importing configuration - config.py not found")
    print("Please create config.py with SSID and PASSWORD")
    sys.exit()

# Initialize WiFi with display feedback
wifi = WiFiManager(ssid, password, display, led)
wifi.scan_networks()

# Connect to WiFi
if not wifi.connect():
    print("Error: Check SSID and password")
    time.sleep(5)  # Give time to see the error on display
    sys.exit()

# Start web server
try:
    web_server = WeatherWebServer(wifi, led)
    web_server.start()
    led.on()  # Solid LED = server running
except Exception as e:
    print("Error starting server:", e)
    led.error_pattern()
    sys.exit()

# Main monitoring loop
print("Weather station running...")
last_update = 0
temp = hum = 0.0
prev_temp = prev_hum = prev_rssi = None

while True:
    try:
        current_time = time.ticks_ms()

        # Update sensor readings every 5 seconds
        if time.ticks_diff(current_time, last_update) > 5000:
            try:
                sensor.measure()
                temp = sensor.temperature()
                hum = sensor.humidity()
                wifi_rssi = wifi.get_rssi()

                # Update display only if values changed
                changed = prev_temp != temp or prev_hum != hum or prev_rssi != wifi_rssi
                if changed:
                    display.show_weather_data(temp, hum, wifi_rssi, wifi.wlan)
                    print(
                        f"Updated: temp={temp:.1f}°C, hum={hum:.1f}%, rssi={wifi_rssi}dBm"
                    )

                prev_temp, prev_hum, prev_rssi = temp, hum, wifi_rssi
                last_update = current_time

            except Exception as e:
                print("Error reading sensor:", e)
                led.off()
                time.sleep(0.05)
                led.on()

        # Handle web requests
        web_server.handle_request(temp, hum)

        # Small delay to prevent busy-waiting
        time.sleep(0.1)

    except KeyboardInterrupt:
        print("Stopping server...")
        web_server.stop()
        led.off()
        sys.exit()
    except Exception as e:
        print("Error in main loop:", e)
        time.sleep(1)
