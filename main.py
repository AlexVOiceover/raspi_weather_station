import network, socket
from machine import Pin, I2C
import dht
import time
import ssd1306

# Configure built-in LED
led = Pin("LED", Pin.OUT)


def blink_led(times, delay=0.2):
    """Blink LED for status indication"""
    for _ in range(times):
        led.on()
        time.sleep(delay)
        led.off()
        time.sleep(delay)


def led_error_pattern():
    """Fast blinking for errors"""
    for _ in range(10):
        led.on()
        time.sleep(0.1)
        led.off()
        time.sleep(0.1)


# Configura sensor DHT22 en GP2
sensor = dht.DHT22(Pin(2))

# Configure OLED display (I2C) - Instructables tutorial pins
i2c = I2C(0, sda=Pin(4), scl=Pin(5), freq=400000)
display = ssd1306.SSD1306_I2C(128, 64, i2c)


def format_sensor_value(value, unit):
    """Format sensor value with unit"""
    return f"{value:.1f}{unit}"

def show_startup_message():
    """Show initial startup message"""
    display.fill(0)  # Clear display
    display.text("PICO WEATHER", 15, 2)
    display.text("Station", 35, 20)
    display.text("Starting up...", 15, 35)
    display.show()

def show_wifi_connecting(ssid, attempt, max_attempts):
    """Show WiFi connection status with progress bar"""
    display.fill(0)  # Clear display
    
    # Title
    display.text("PICO WEATHER", 15, 2)
    
    # Connection status
    display.text("Connecting to:", 5, 20)
    # Truncate SSID if too long
    short_ssid = ssid[:12] if len(ssid) > 12 else ssid
    display.text(short_ssid, 5, 30)
    
    # Faster progress bar - use fewer total attempts for calculation
    attempts_passed = max_attempts - attempt
    progress = attempts_passed / 20  # Use 20 instead of 60 for faster progress
    bar_width = int(min(progress, 1.0) * 100)  # Cap at 100%
    display.rect(10, 45, 102, 8, 1)  # Border
    if bar_width > 0:
        display.fill_rect(11, 46, bar_width, 6, 1)  # Progress
    
    display.show()



def update_display(temp, hum, wifi_rssi, prev_temp, prev_hum, prev_rssi):
    """Update the OLED display with current readings"""

    # Check if any value changed
    changed = prev_temp != temp or prev_hum != hum or prev_rssi != wifi_rssi

    if changed:
        display.fill(0)  # Clear display

        # Title
        display.text("PICO WEATHER", 15, 2)

        # Temperature
        temp_str = format_sensor_value(temp, "C")
        display.text(f"Temp: {temp_str}", 0, 16)

        # Humidity
        hum_str = format_sensor_value(hum, "%")
        display.text(f"Hum:  {hum_str}", 0, 26)

        # WiFi status
        if wlan.isconnected():
            display.text(f"WiFi: {wifi_rssi}dBm", 0, 36)
        else:
            display.text("WiFi: Disconnected", 0, 36)

        # IP Address (if connected) - split across two lines if needed
        if wlan.isconnected():
            ip = wlan.ifconfig()[0].strip()  # Remove any whitespace
            if len(ip) > 12:  # If IP is too long, split it
                display.text("IP:", 0, 46)
                display.text(ip, 0, 55)
            else:
                display.text(f"IP:{ip}", 0, 46)  # No space after colon

        display.show()


# Show initial startup message on display
show_startup_message()

# LED startup indication
blink_led(3, 0.5)  # 3 slow blinks = starting up

# Configuración Wi-Fi
try:
    from config import SSID, PASSWORD

    ssid = SSID
    password = PASSWORD
except ImportError:
    # Fallback if config.py not found
    ssid = "adriananet"
    password = "pepinos!y2Centollas"
wlan = network.WLAN(network.STA_IF)
wlan.active(True)

print("WiFi activo:", wlan.active())
print("Redes disponibles:")
networks = wlan.scan()
for net in networks:
    print("  ", net[0].decode("utf-8"))

print("Conectando a:", ssid)
wlan.disconnect()  # Disconnect first
time.sleep(1)
wlan.connect(ssid, password)

print("Conectando a Wi-Fi...", end="")
max_wait = 60
while max_wait > 0:
    # Show connection status on OLED with animation
    show_wifi_connecting(ssid, max_wait, 60)
    
    status = wlan.status()
    if status == 3:  # Connected and got IP
        break
    elif status < 0:  # Connection failed
        print(f"\nError de conexión: {status}")
        led_error_pattern()  # Show error immediately
        break
    max_wait -= 1
    time.sleep(0.5)
    print(".", end="")
    # Blink once every 10 attempts to show it's trying
    if max_wait % 10 == 0:
        blink_led(1, 0.1)

if wlan.isconnected():
    print("\nConectado:", wlan.ifconfig())
    blink_led(2, 0.3)  # 2 medium blinks = WiFi connected
else:
    print("\nFallo conexión Wi-Fi")
    print("Status:", wlan.status())
    print("Error: Revisar SSID y contraseña")
    led_error_pattern()  # Error pattern for WiFi failure
    # Don't start server without WiFi
    import sys

    sys.exit()

# Inicia servidor HTTP con manejo de errores
try:
    addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(1)
    print("Servidor HTTP en http://%s:80" % wlan.ifconfig()[0])
    led.on()  # Solid LED = server running successfully
except Exception as e:
    print("Error iniciando servidor:", e)
    led_error_pattern()  # Error pattern for server failure
    import sys

    sys.exit()

# Basic HTML template
html = """<!DOCTYPE html>
<html>
  <head><title>Pico W DHT22</title></head>
  <body><h1>Temperatura y Humedad</h1>
    <p>Temp: {temp:.1f} &deg;C<br>Hum: {hum:.1f} %</p>
  </body>
</html>
"""

# Variables for continuous display updates
last_update = 0
temp = hum = 0.0
# Previous values to avoid unnecessary redraws
prev_temp = prev_hum = prev_rssi = None

while True:
    try:
        # Update sensor readings and display every 5 seconds
        current_time = time.ticks_ms()
        if time.ticks_diff(current_time, last_update) > 5000:  # 5 seconds
            try:
                sensor.measure()
                temp = sensor.temperature()
                hum = sensor.humidity()
                # Get WiFi signal strength (RSSI)
                wifi_rssi = wlan.status("rssi") if wlan.isconnected() else -100

                # Update display only if values changed
                update_display(temp, hum, wifi_rssi, prev_temp, prev_hum, prev_rssi)

                # Check if any value actually changed for logging
                changed = prev_temp != temp or prev_hum != hum or prev_rssi != wifi_rssi
                if changed:
                    print(
                        f"Display updated: temp={temp:.1f}°C, hum={hum:.1f}%, rssi={wifi_rssi}dBm"
                    )
                else:
                    print("Values unchanged - no display update needed")

                # Update previous values
                prev_temp, prev_hum, prev_rssi = temp, hum, wifi_rssi
                last_update = current_time

            except Exception as e:
                print("Error reading sensor:", e)
                # Brief LED off for sensor error
                led.off()
                time.sleep(0.05)
                led.on()

        # Check for web requests (non-blocking)
        s.settimeout(0.1)  # 100ms timeout
        try:
            cl, addr = s.accept()
            print("Web request from", addr)

            # Read the HTTP request
            request = cl.recv(1024)
            request_str = request.decode("utf-8")

            # Parse request path
            request_line = request_str.split("\r\n")[0]
            path = (
                request_line.split(" ")[1] if len(request_line.split(" ")) > 1 else "/"
            )

            if path == "/favicon.ico":
                # Return 404 for favicon
                error_response = "404 Not Found"
                headers = "HTTP/1.1 404 Not Found\r\n"
                headers += "Connection: close\r\n"
                headers += f"Content-Length: {len(error_response)}\r\n\r\n"
                cl.send(headers.encode("utf-8"))
                cl.send(error_response.encode("utf-8"))
            else:
                # Serve main page with current sensor values
                response = html.format(temp=temp, hum=hum)

                # Send response with proper headers
                headers = "HTTP/1.1 200 OK\r\n"
                headers += "Content-Type: text/html; charset=utf-8\r\n"
                headers += "Access-Control-Allow-Origin: *\r\n"
                headers += "Connection: close\r\n"
                headers += f"Content-Length: {len(response)}\r\n\r\n"

                cl.send(headers.encode("utf-8"))
                cl.send(response.encode("utf-8"))

            cl.close()

        except OSError:
            # No incoming connections, continue
            pass

    except Exception as e:
        print("Error in main loop:", e)
        time.sleep(1)
