import network, socket
from machine import Pin
import dht
import time

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

while True:
    try:
        cl, addr = s.accept()
        print("Petición desde", addr)

        # Read the HTTP request
        request = cl.recv(1024)
        request_str = request.decode("utf-8")
        print("Request:", request_str[:100])

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
            # Serve main page
            # Read sensor
            try:
                sensor.measure()
                temp = sensor.temperature()
                hum = sensor.humidity()
            except Exception as e:
                temp = hum = 0.0
                print("Error sensor:", e)
                # Brief LED off for sensor error
                led.off()
                time.sleep(0.05)
                led.on()

            response = html.format(temp=temp, hum=hum)
            print(f"Enviando respuesta: temp={temp}, hum={hum}")

            # Send response with proper headers
            headers = "HTTP/1.1 200 OK\r\n"
            headers += "Content-Type: text/html; charset=utf-8\r\n"
            headers += "Access-Control-Allow-Origin: *\r\n"
            headers += "Connection: close\r\n"
            headers += f"Content-Length: {len(response)}\r\n\r\n"

            cl.send(headers.encode("utf-8"))
            cl.send(response.encode("utf-8"))
        time.sleep(0.1)  # Small delay before closing
        cl.close()
        print("Respuesta enviada")
    except Exception as e:
        print("Error servidor:", e)
        try:
            cl.close()
        except:
            pass
