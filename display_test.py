from machine import Pin, SPI
import gc9a01
import time

print("Starting display test...")

# Configure GC9A01 display with slower baudrate
spi = SPI(1, baudrate=10000000, sck=Pin(14), mosi=Pin(15))  # Slower speed
display = gc9a01.GC9A01(spi=spi, dc=Pin(16), cs=Pin(13), reset=Pin(17))

print("Display initialized")

# Test 1: Fill screen with solid colors
print("Test 1: Solid colors")
display.fill(gc9a01.RED)
time.sleep(2)

display.fill(gc9a01.GREEN)  
time.sleep(2)

display.fill(gc9a01.BLUE)
time.sleep(2)

display.fill(gc9a01.WHITE)
time.sleep(2)

display.fill(gc9a01.BLACK)
time.sleep(2)

# Test 2: Simple shapes
print("Test 2: Shapes")
display.fill(gc9a01.BLACK)  # Clear
display.fill_rect(50, 50, 100, 100, gc9a01.RED)
display.fill_rect(100, 100, 50, 50, gc9a01.BLUE)
time.sleep(2)

print("Test complete")