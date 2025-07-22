# Display utility functions for OLED
from ssd1306 import SSD1306_I2C


class DisplayManager:
    def __init__(self, display):
        self.display = display

    def show_startup_message(self):
        """Show initial startup message"""
        self.display.fill(0)
        self.display.text("PICO WEATHER", 15, 2)
        self.display.text("Starting up...", 15, 25)
        self.display.show()

    def show_wifi_connecting(self, ssid, attempt, max_attempts):
        """Show WiFi connection status with progress bar"""
        self.display.fill(0)

        # Title
        self.display.text("PICO WEATHER", 15, 2)

        # Connection status
        self.display.text("Connecting to:", 5, 20)
        # Truncate SSID if too long
        short_ssid = ssid[:12] if len(ssid) > 12 else ssid
        self.display.text(short_ssid, 5, 30)

        # Progress bar
        attempts_passed = max_attempts - attempt
        progress = attempts_passed / 20
        bar_width = int(min(progress, 1.0) * 100)
        self.display.rect(10, 45, 102, 8, 1)  # Border
        if bar_width > 0:
            self.display.fill_rect(11, 46, bar_width, 6, 1)  # Progress

        self.display.show()

    def show_weather_data(self, temp, hum, wifi_rssi, wlan):
        """Display weather station data"""
        self.display.fill(0)

        # Title
        self.display.text("PICO WEATHER", 15, 2)

        # Temperature
        temp_str = f"{temp:.1f}C"
        self.display.text(f"Temp: {temp_str}", 0, 16)

        # Humidity
        hum_str = f"{hum:.1f}%"
        self.display.text(f"Hum:  {hum_str}", 0, 26)

        # WiFi status
        if wlan.isconnected():
            self.display.text(f"WiFi: {wifi_rssi}dBm", 0, 36)
        else:
            self.display.text("WiFi: Disconnected", 0, 36)

        # IP Address
        if wlan.isconnected():
            ip = wlan.ifconfig()[0].strip()
            self.display.text(f"IP:{ip}", 0, 46)

        self.display.show()

    def show_wifi_error(self, ssid, status_code):
        """Show WiFi connection error"""
        self.display.fill(0)

        # Title
        self.display.text("PICO WEATHER", 15, 2)

        # Error message
        self.display.text("WiFi Failed!", 20, 20)
        self.display.text(f"Network: {ssid[:10]}", 5, 32)
        self.display.text(f"Status: {status_code}", 5, 42)
        self.display.text("Check config!", 15, 52)

        self.display.show()
