# Simple OLED Display Test for Workshop Students
# Connect your SSD1306 OLED display:
# VCC -> 3.3V (pin 36)
# GND -> Ground (pin 38)  
# SDA -> Physical pin 6 (GP4)
# SCL -> Physical pin 7 (GP5)

from machine import Pin, I2C
import machine
from ssd1306 import SSD1306_I2C
import time

print("=== OLED Display Test ===")
print("Make sure your display is connected to pins 6 and 7")

# Setup I2C communication
sda = machine.Pin(4)  # Physical pin 6
scl = machine.Pin(5)  # Physical pin 7
i2c = machine.I2C(0, sda=sda, scl=scl, freq=400000)

# Check if display is detected
devices = i2c.scan()
print("I2C devices found:", [hex(d) for d in devices])

if not devices:
    print("❌ No display found! Check your wiring:")
    print("  VCC -> 3.3V")  
    print("  GND -> Ground")
    print("  SDA -> Pin 6")
    print("  SCL -> Pin 7")
else:
    try:
        # Initialize 128x64 OLED display
        oled = SSD1306_I2C(128, 64, i2c)
        print("✅ OLED display connected successfully!")
        
        # Clear display
        oled.fill(0)
        oled.show()
        
        # Show test message
        oled.text("Workshop Test", 10, 10)
        oled.text("Display Works!", 10, 25)
        oled.text("Ready for", 10, 40)
        oled.text("Your Project!", 10, 50)
        
        # Draw a simple border
        oled.rect(0, 0, 128, 64, 1)
        
        oled.show()
        print("✅ Test message displayed!")
        print("If you see text on your display, everything is working!")
        
        # Wait 5 seconds then clear
        time.sleep(5)
        oled.fill(0)
        oled.show()
        print("Test complete!")
        
    except Exception as e:
        print(f"❌ Display test failed: {e}")
        print("Try disconnecting and reconnecting USB cable, then run again")