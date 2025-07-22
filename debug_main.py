# Debug version to isolate the issue
print("Starting debug...")

try:
    from machine import Pin, I2C
    print("✓ Machine imports OK")
except Exception as e:
    print("✗ Machine import failed:", e)

try:
    import dht
    print("✓ DHT import OK")
except Exception as e:
    print("✗ DHT import failed:", e)

try:
    import time
    print("✓ Time import OK")
except Exception as e:
    print("✗ Time import failed:", e)

try:
    import ssd1306
    print("✓ SSD1306 import OK")
except Exception as e:
    print("✗ SSD1306 import failed:", e)

try:
    import sys
    print("✓ Sys import OK")
except Exception as e:
    print("✗ Sys import failed:", e)

print("Testing module imports...")

try:
    from display_utils import DisplayManager
    print("✓ DisplayManager import OK")
except Exception as e:
    print("✗ DisplayManager import failed:", e)

try:
    from wifi_manager import WiFiManager
    print("✓ WiFiManager import OK")
except Exception as e:
    print("✗ WiFiManager import failed:", e)

try:
    from led_controller import LEDController
    print("✓ LEDController import OK")
except Exception as e:
    print("✗ LEDController import failed:", e)

try:
    from web_server import WeatherWebServer
    print("✓ WeatherWebServer import OK")
except Exception as e:
    print("✗ WeatherWebServer import failed:", e)

print("Testing hardware initialization...")

try:
    sensor = dht.DHT22(Pin(2))
    print("✓ DHT22 sensor OK")
except Exception as e:
    print("✗ DHT22 sensor failed:", e)

try:
    i2c = I2C(0, sda=Pin(4), scl=Pin(5), freq=400000)
    print("✓ I2C init OK")
except Exception as e:
    print("✗ I2C init failed:", e)

try:
    oled_display = ssd1306.SSD1306_I2C(128, 64, i2c)
    print("✓ OLED display OK")
except Exception as e:
    print("✗ OLED display failed:", e)

print("Testing managers...")

try:
    led = LEDController()
    print("✓ LED controller OK")
except Exception as e:
    print("✗ LED controller failed:", e)

try:
    display = DisplayManager(oled_display)
    print("✓ Display manager OK")
except Exception as e:
    print("✗ Display manager failed:", e)

try:
    display.show_startup_message()
    print("✓ Startup message OK")
except Exception as e:
    print("✗ Startup message failed:", e)

print("Debug complete!")