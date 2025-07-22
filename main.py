import network, socket
from machine import Pin, SPI
import dht
import time
import gc9a01

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

# Configure GC9A01 display
spi = SPI(1, baudrate=10000000, sck=Pin(14), mosi=Pin(15))  # Slower baudrate
display = gc9a01.GC9A01(spi=spi, dc=Pin(16), cs=Pin(13), reset=Pin(17))

def draw_digit(x, y, digit, color):
    """Draw a simple 7-segment style digit using rectangles"""
    # Define 7-segment patterns for digits 0-9
    segments = {
        0: [1,1,1,1,1,1,0],  # top, top-right, bottom-right, bottom, bottom-left, top-left, middle
        1: [0,1,1,0,0,0,0],
        2: [1,1,0,1,1,0,1],
        3: [1,1,1,1,0,0,1],
        4: [0,1,1,0,0,1,1],
        5: [1,0,1,1,0,1,1],
        6: [1,0,1,1,1,1,1],
        7: [1,1,1,0,0,0,0],
        8: [1,1,1,1,1,1,1],
        9: [1,1,1,1,0,1,1]
    }
    
    if digit in segments:
        segs = segments[digit]
        # Draw segments as rectangles
        if segs[0]: display.fill_rect(x+2, y, 16, 3, color)      # top
        if segs[1]: display.fill_rect(x+17, y+2, 3, 16, color)   # top-right
        if segs[2]: display.fill_rect(x+17, y+18, 3, 16, color)  # bottom-right
        if segs[3]: display.fill_rect(x+2, y+33, 16, 3, color)   # bottom
        if segs[4]: display.fill_rect(x, y+18, 3, 16, color)     # bottom-left
        if segs[5]: display.fill_rect(x, y+2, 3, 16, color)      # top-left
        if segs[6]: display.fill_rect(x+2, y+16, 16, 3, color)   # middle

def draw_number(x, y, number, color):
    """Draw a number using digital-style digits"""
    num_str = f"{number:.1f}"
    pos_x = x
    for char in num_str:
        if char == '.':
            display.fill_rect(pos_x + 5, y + 30, 3, 3, color)  # decimal point
            pos_x += 10
        elif char.isdigit():
            draw_digit(pos_x, y, int(char), color)
            pos_x += 25
        else:
            pos_x += 10  # space for other characters

def draw_unit_c(x, y, color):
    """Draw °C unit symbol"""
    # Degree symbol (small circle)
    display.fill_rect(x, y, 8, 8, color)
    display.fill_rect(x+2, y+2, 4, 4, gc9a01.BLACK)
    # C letter
    display.fill_rect(x+12, y, 15, 3, color)      # top
    display.fill_rect(x+12, y+3, 3, 10, color)    # left side
    display.fill_rect(x+12, y+13, 15, 3, color)   # bottom

def draw_unit_percent(x, y, color):
    """Draw % unit symbol"""
    # Top left circle
    display.fill_rect(x, y, 6, 6, color)
    display.fill_rect(x+2, y+2, 2, 2, gc9a01.BLACK)
    # Bottom right circle
    display.fill_rect(x+18, y+10, 6, 6, color)
    display.fill_rect(x+20, y+12, 2, 2, gc9a01.BLACK)
    # Diagonal line from top-right to bottom-left
    for i in range(16):
        display.fill_rect(x+6+i, y+15-i, 2, 2, color)

def draw_unit_dbm(x, y, rssi, color):
    """Draw WiFi signal strength in dBm"""
    rssi_str = f"{rssi}"
    pos_x = x
    # Draw the number
    for char in rssi_str:
        if char.isdigit():
            draw_digit(pos_x, y, int(char), color)
            pos_x += 20
        elif char == '-':
            display.fill_rect(pos_x+5, y+16, 10, 3, color)  # minus sign
            pos_x += 20
    
    # Add spacing and align units vertically with other units
    pos_x += 10  # Space between number and unit
    unit_y = y + 5  # Align with °C and % units
    
    # Draw "dBm" units
    # d
    display.fill_rect(pos_x, unit_y, 3, 16, color)
    display.fill_rect(pos_x+3, unit_y, 8, 3, color)
    display.fill_rect(pos_x+3, unit_y+13, 8, 3, color)
    display.fill_rect(pos_x+11, unit_y+3, 3, 10, color)
    pos_x += 18
    
    # B
    display.fill_rect(pos_x, unit_y, 3, 16, color)
    display.fill_rect(pos_x+3, unit_y, 8, 3, color)
    display.fill_rect(pos_x+3, unit_y+6, 8, 3, color)
    display.fill_rect(pos_x+3, unit_y+13, 8, 3, color)
    display.fill_rect(pos_x+11, unit_y+3, 3, 3, color)
    display.fill_rect(pos_x+11, unit_y+10, 3, 3, color)
    pos_x += 18
    
    # m
    display.fill_rect(pos_x, unit_y+6, 3, 10, color)
    display.fill_rect(pos_x+3, unit_y+6, 3, 3, color)
    display.fill_rect(pos_x+6, unit_y+9, 3, 7, color)
    display.fill_rect(pos_x+9, unit_y+6, 3, 3, color)
    display.fill_rect(pos_x+12, unit_y+9, 3, 7, color)

def update_display(temp, hum, wifi_rssi, prev_temp, prev_hum, prev_rssi):
    """Update the GC9A01 display with current readings - only redraw changed values"""
    
    # Only update temperature if it changed
    if prev_temp != temp:
        display.fill_rect(20, 50, 170, 40, gc9a01.BLACK)
        draw_number(20, 50, temp, gc9a01.RED)
        draw_unit_c(130, 55, gc9a01.RED)
    
    # Only update humidity if it changed
    if prev_hum != hum:
        display.fill_rect(20, 100, 170, 40, gc9a01.BLACK)
        draw_number(20, 100, hum, gc9a01.BLUE)
        draw_unit_percent(130, 105, gc9a01.BLUE)
    
    # Only update WiFi if it changed
    if prev_rssi != wifi_rssi:
        display.fill_rect(20, 150, 200, 40, gc9a01.BLACK)
        if wlan.isconnected():
            draw_unit_dbm(20, 150, wifi_rssi, gc9a01.GREEN)
        else:
            display.fill_rect(20, 150, 100, 30, gc9a01.RED)

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
                wifi_rssi = wlan.status('rssi') if wlan.isconnected() else -100
                
                # Update display only if values changed
                update_display(temp, hum, wifi_rssi, prev_temp, prev_hum, prev_rssi)
                
                # Check if any value actually changed for logging
                changed = (prev_temp != temp or prev_hum != hum or prev_rssi != wifi_rssi)
                if changed:
                    print(f"Display updated: temp={temp:.1f}°C, hum={hum:.1f}%, rssi={wifi_rssi}dBm")
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
            path = request_line.split(" ")[1] if len(request_line.split(" ")) > 1 else "/"
            
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
