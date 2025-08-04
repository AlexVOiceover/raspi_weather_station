# Simple web server for weather data
import socket
import select
import time


class WeatherWebServer:
    def __init__(self, wifi_manager, led_controller=None):
        self.wifi_manager = wifi_manager
        self.led_controller = led_controller
        self.server_socket = None
        self.poller = select.poll()
        self.clients = {}
        self.start_time = time.time()
        self.history = []  # Store readings: [(timestamp, temp, hum), ...]
        self.last_history_update = 0

        self.html_template = """<!DOCTYPE html>
<html>
<head>
    <title>Pico W Weather Station</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f0f8ff; }}
        .container {{ max-width: 800px; margin: 0 auto; }}
        .header {{ text-align: center; color: #2c3e50; margin-bottom: 30px; }}
        .current {{ background: #fff; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 20px; }}
        .metric {{ display: inline-block; margin: 10px 20px; text-align: center; }}
        .metric-value {{ font-size: 2.5em; font-weight: bold; color: #e74c3c; }}
        .metric-label {{ font-size: 1.2em; color: #7f8c8d; }}
        .history {{ background: #fff; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .history-item {{ padding: 8px; border-bottom: 1px solid #ecf0f1; display: flex; justify-content: space-between; }}
        .history-item:last-child {{ border-bottom: none; }}
        .info {{ background: #3498db; color: white; padding: 15px; border-radius: 10px; margin-bottom: 20px; text-align: center; }}
        .footer {{ text-align: center; margin-top: 20px; color: #7f8c8d; font-size: 0.9em; }}
        @media (max-width: 600px) {{ .metric {{ margin: 10px 5px; }} .metric-value {{ font-size: 2em; }} }}
    </style>
    <script>
        setTimeout(function(){{ location.reload(); }}, 30000); // Auto-refresh every 30 seconds
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌡️ Pico W Weather Station</h1>
        </div>
        
        <div class="info">
            <strong>Server Started:</strong> {start_time}<br>
            <strong>Uptime:</strong> {uptime}<br>
            <strong>IP Address:</strong> {ip_address}<br>
            <strong>WiFi Signal:</strong> {wifi_rssi} dBm ({wifi_strength})
        </div>
        
        <div class="current">
            <h2>Current Readings</h2>
            <div class="metric">
                <div class="metric-value">{temp:.1f}°</div>
                <div class="metric-label">Temperature (°C)</div>
            </div>
            <div class="metric">
                <div class="metric-value">{hum:.1f}%</div>
                <div class="metric-label">Humidity</div>
            </div>
        </div>
        
        <div class="history">
            <h2>📊 Recent History (Last {history_count} readings)</h2>
            {history_html}
        </div>
        
        <div class="footer">
            Last updated: {current_time} | Auto-refresh in 30s
        </div>
    </div>
</body>
</html>"""

    def start(self):
        """Start the web server"""
        if not self.wifi_manager.is_connected():
            raise Exception("WiFi not connected")

        addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
        self.server_socket = socket.socket()
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(addr)
        self.server_socket.listen(5)
        self.server_socket.setblocking(False)
        self.poller.register(self.server_socket, select.POLLIN)
        print(f"HTTP server at http://{self.wifi_manager.get_ip()}:80")
        return True

    def update_history(self, temp, hum, rssi):
        """Update historical data - called every minute"""
        current_time = time.time()

        # Add reading if it's been at least 60 seconds since last update
        if current_time - self.last_history_update >= 60:
            self.history.append((current_time, temp, hum, rssi))

            # Keep only last 24 readings (24 minutes of history)
            if len(self.history) > 24:
                self.history.pop(0)

            self.last_history_update = current_time

    def _format_time(self, timestamp):
        """Format timestamp for display"""
        # Simple time formatting for MicroPython
        elapsed = int(timestamp - self.start_time)
        hours = elapsed // 3600
        minutes = (elapsed % 3600) // 60
        return f"{hours:02d}:{minutes:02d}"

    def _get_uptime(self):
        """Get formatted uptime"""
        elapsed = int(time.time() - self.start_time)
        hours = elapsed // 3600
        minutes = (elapsed % 3600) // 60
        seconds = elapsed % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def _get_signal_strength(self, rssi):
        """Convert RSSI to descriptive signal strength"""
        if rssi >= -50:
            return "Excellent"
        elif rssi >= -60:
            return "Good"
        elif rssi >= -70:
            return "Fair"
        elif rssi >= -80:
            return "Weak"
        else:
            return "Poor"

    def handle_request(self, temp, hum):
        """Handle incoming web requests using polling"""
        if not self.server_socket:
            return

        # Update history every minute
        rssi = self.wifi_manager.get_rssi()
        self.update_history(temp, hum, rssi)

        try:
            events = self.poller.poll(10)  # Poll for 10ms
            for sock, event in events:
                if sock is self.server_socket:
                    # New connection
                    cl, addr = self.server_socket.accept()
                    cl.setblocking(False)
                    print("Web request from", addr)
                    self.poller.register(cl, select.POLLIN)
                    self.clients[cl] = addr
                elif event & select.POLLIN:
                    # Data received from a client
                    client_socket = sock
                    addr = self.clients.get(client_socket)
                    try:
                        request = client_socket.recv(1024)
                        if request:
                            request_str = request.decode("utf-8")
                            request_line = request_str.split("\r\n")[0]
                            path = (
                                request_line.split(" ")[1]
                                if len(request_line.split(" ")) > 1
                                else "/"
                            )

                            if path == "/favicon.ico":
                                self._send_404(client_socket)
                            else:
                                # Flash LED 3 times for web request
                                if self.led_controller:
                                    self.led_controller.web_request_flash()
                                self._send_weather_page(client_socket, temp, hum)
                        else:
                            # No data, connection closed by client
                            print(f"Connection closed by {addr}")
                    except OSError as e:
                        if e.args[0] != 11:  # EAGAIN
                            print(f"Error reading from client {addr}: {e}")
                    finally:
                        self.poller.unregister(client_socket)
                        client_socket.close()
                        del self.clients[client_socket]

        except Exception as e:
            print(f"Server error: {e}")

    def _send_404(self, client):
        """Send 404 response"""
        error_response = "404 Not Found"
        headers = "HTTP/1.1 404 Not Found\r\n"
        headers += "Connection: close\r\n"
        headers += f"Content-Length: {len(error_response)}\r\n\r\n"
        client.send(headers.encode("utf-8"))
        client.send(error_response.encode("utf-8"))

    def _send_weather_page(self, client, temp, hum):
        """Send weather data page"""
        # Generate history HTML
        history_html = ""
        if self.history:
            for item in reversed(self.history):  # Most recent first
                if len(item) == 4:  # New format with RSSI
                    timestamp, h_temp, h_hum, h_rssi = item
                    signal_strength = self._get_signal_strength(h_rssi)
                    time_str = self._format_time(timestamp)
                    history_html += f"""
                    <div class="history-item">
                        <span>{time_str}</span>
                        <span>{h_temp:.1f}°C, {h_hum:.1f}%, {h_rssi}dBm ({signal_strength})</span>
                    </div>"""
                else:  # Old format without RSSI (backward compatibility)
                    timestamp, h_temp, h_hum = item
                    time_str = self._format_time(timestamp)
                    history_html += f"""
                    <div class="history-item">
                        <span>{time_str}</span>
                        <span>{h_temp:.1f}°C, {h_hum:.1f}%</span>
                    </div>"""
        else:
            history_html = '<div class="history-item"><span>No historical data yet</span><span>-</span></div>'

        # Format start time
        start_time_str = self._format_time(self.start_time)

        # Get current time for footer
        current_time_str = self._format_time(time.time())

        current_rssi = self.wifi_manager.get_rssi()
        response = self.html_template.format(
            temp=temp,
            hum=hum,
            start_time=start_time_str,
            wifi_rssi=current_rssi,
            wifi_strength=self._get_signal_strength(current_rssi),
            uptime=self._get_uptime(),
            ip_address=self.wifi_manager.get_ip(),
            history_html=history_html,
            history_count=len(self.history),
            current_time=current_time_str,
        )

        headers = "HTTP/1.1 200 OK\r\n"
        headers += "Content-Type: text/html; charset=utf-8\r\n"
        headers += "Access-Control-Allow-Origin: *\r\n"
        headers += "Connection: close\r\n"
        headers += f"Content-Length: {len(response)}\r\n\r\n"

        client.send(headers.encode("utf-8"))
        client.send(response.encode("utf-8"))

    def stop(self):
        """Stop the web server"""
        if self.server_socket:
            self.poller.unregister(self.server_socket)
            self.server_socket.close()
            self.server_socket = None
            print("Web server stopped")
