# LED control utilities
import time
from machine import Pin

class LEDController:
    def __init__(self, pin="LED"):
        self.led = Pin(pin, Pin.OUT)
    
    def blink(self, times, delay=0.2):
        """Blink LED for status indication"""
        for _ in range(times):
            self.led.on()
            time.sleep(delay)
            self.led.off()
            time.sleep(delay)
    
    def error_pattern(self):
        """Fast blinking pattern for errors"""
        for _ in range(10):
            self.led.on()
            time.sleep(0.1)
            self.led.off()
            time.sleep(0.1)
    
    def on(self):
        """Turn LED on"""
        self.led.on()
    
    def off(self):
        """Turn LED off"""
        self.led.off()
    
    def startup_sequence(self):
        """LED startup indication"""
        self.blink(3, 0.5)