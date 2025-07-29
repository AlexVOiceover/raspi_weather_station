from machine import Pin
import time

# Initialize the onboard LED (usually on pin 25 for Pico, "LED" for Pico W)
try:
    # Try Pico W first (has "LED" identifier)
    led = Pin("LED", Pin.OUT)
    print("Pico W detected")
except:
    # Fall back to regular Pico (pin 25)
    led = Pin(25, Pin.OUT)
    print("Regular Pico detected")

print("Starting blink test...")
print("If you see this message and the LED blinks, your Pico is alive!")

# Blink pattern: fast blinks to show it's working
while True:
    led.on()
    time.sleep(0.5)
    led.off()
    time.sleep(0.5)
    print("Blink!")