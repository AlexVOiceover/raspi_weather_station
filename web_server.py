# Simple web server for weather data
import socket
import select
import time
from machine import ADC
from weather_ai import TinyWeatherPerceptron


class WeatherWebServer:
    def __init__(self, wifi_manager, led_controller=None):
        self.wifi_manager = wifi_manager
        self.led_controller = led_controller
        self.server_socket = None
        self.poller = select.poll()
        self.clients = {}
        self.start_time = time.time()
        self.history = []  # Store readings: [(timestamp, temp, hum), ...]
        self.last_history_update = time.time()  # Initialize to current time
        self.internal_temp_sensor = ADC(4)  # Internal temperature sensor
        self.ai_brain = TinyWeatherPerceptron()  # Real AI neural network

        self.html_template = """<!DOCTYPE html>
<html>
<head>
    <title>FAC Weather Station</title>
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
        .history-item {{ padding: 8px; border-bottom: 1px solid #ecf0f1; display: grid; grid-template-columns: 1fr 1fr 1fr 2fr; gap: 10px; align-items: center; }}
        .history-item:last-child {{ border-bottom: none; }}
        .history-header {{ padding: 10px 8px; border-bottom: 2px solid #3498db; display: grid; grid-template-columns: 1fr 1fr 1fr 2fr; gap: 10px; font-weight: bold; color: #2c3e50; }}
        .ai-section {{ background: #fff; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 20px; border-left: 4px solid #e74c3c; display: none; }}
        .ai-prediction {{ text-align: center; }}
        .comfort-level {{ margin-bottom: 10px; }}
        .comfort-label {{ color: #7f8c8d; font-size: 1.1em; }}
        .comfort-value {{ color: #2c3e50; font-size: 1.8em; font-weight: bold; margin: 0 10px; }}
        .comfort-score {{ color: #95a5a6; font-size: 1.2em; }}
        .learning-info {{ color: #7f8c8d; margin-top: 15px; line-height: 1.4; }}
        .feedback-section {{ margin: 20px 0; padding: 15px; background: #f8f9fa; border-radius: 8px; }}
        .feedback-buttons {{ display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; margin: 10px 0; }}
        .feedback-btn {{ padding: 8px 12px; border: none; border-radius: 20px; cursor: pointer; font-size: 0.9em; transition: all 0.2s; }}
        .feedback-btn:hover {{ transform: translateY(-2px); box-shadow: 0 4px 8px rgba(0,0,0,0.2); }}
        .comfortable {{ background: #27ae60; color: white; }}
        .good {{ background: #2ecc71; color: white; }}
        .neutral {{ background: #95a5a6; color: white; }}
        .poor {{ background: #e67e22; color: white; }}
        .bad {{ background: #e74c3c; color: white; }}
        #feedback-status {{ margin-top: 10px; font-weight: bold; color: #27ae60; }}
        .info {{ background: #3498db; color: white; padding: 15px; border-radius: 10px; margin-bottom: 20px; text-align: center; }}
        .footer {{ text-align: center; margin-top: 20px; color: #7f8c8d; font-size: 0.9em; }}
        @media (max-width: 600px) {{ .metric {{ margin: 10px 5px; }} .metric-value {{ font-size: 2em; }} }}
    </style>
    <script>
        setTimeout(function(){{ location.reload(); }}, 30000); // Auto-refresh every 30 seconds
        
        let clickCount = 0;
        function revealAI() {{
            clickCount++;
            if (clickCount >= 3) {{
                document.querySelector('.ai-section').style.display = 'block';
            }}
        }}
        
        function sendFeedback(rating) {{
            const temp = {temp};
            const humidity = {hum};
            
            // Send feedback to server
            fetch('/feedback', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{'rating': rating, 'temp': temp, 'humidity': humidity}})
            }})
            .then(response => response.text())
            .then(data => {{
                document.getElementById('feedback-status').innerHTML = 'Thanks! Neural network learned from your feedback.';
                setTimeout(() => {{
                    document.getElementById('feedback-status').innerHTML = '';
                }}, 3000);
            }})
            .catch(error => {{
                document.getElementById('feedback-status').innerHTML = 'Feedback sent! (Training neural network...)';
                console.log('Feedback sent:', rating);
            }});
        }}
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1><span onclick="revealAI()">🌡️</span> Pico W Weather Station</h1>
        </div>
        
        <div class="info">
            <strong>Server Started:</strong> {start_time}<br>
            <strong>Uptime:</strong> {uptime}<br>
            <strong>IP Address:</strong> {ip_address}<br>
            <strong>WiFi Signal:</strong> {wifi_rssi} dBm ({wifi_strength})<br>
            <strong>Chip Temperature:</strong> {internal_temp:.1f}°C
        </div>
        
        <div class="current">
            <h2>Current Readings</h2>
            <div class="metric">
                <div class="metric-value">{temp:.1f}°</div>
                <div class="metric-label">Temperature</div>
            </div>
            <div class="metric">
                <div class="metric-value">{hum:.1f}%</div>
                <div class="metric-label">Humidity</div>
            </div>
        </div>
        
        <div class="ai-section">
            <h2>🧠 Neural Network Prediction</h2>
            <div class="ai-prediction">
                <div class="comfort-level">
                    <span class="comfort-label">Comfort Level:</span>
                    <span class="comfort-value">{comfort_description}</span>
                    <span class="comfort-score">({comfort_score:.1%})</span>
                </div>
                <div class="feedback-section">
                    <p><strong>Help train the AI:</strong> How do you feel about these conditions?</p>
                    <div class="feedback-buttons">
                        <button onclick="sendFeedback(1.0)" class="feedback-btn comfortable">😊 Very Comfortable</button>
                        <button onclick="sendFeedback(0.7)" class="feedback-btn good">🙂 Comfortable</button>
                        <button onclick="sendFeedback(0.5)" class="feedback-btn neutral">😐 Neutral</button>
                        <button onclick="sendFeedback(0.3)" class="feedback-btn poor">🙁 Uncomfortable</button>
                        <button onclick="sendFeedback(0.0)" class="feedback-btn bad">😣 Very Uncomfortable</button>
                    </div>
                    <div id="feedback-status"></div>
                </div>
                <div class="learning-info">
                    <small>Neural network has made {prediction_count} predictions</small><br>
                    <small>Weights: T={temp_weight:.3f}, H={humidity_weight:.3f}, B={bias:.3f}</small>
                </div>
            </div>
        </div>
        
        <div class="history">
            <h2>📊 Recent History (Last {history_count} readings)</h2>
            <div class="history-header">
                <span>Time</span>
                <span>Temperature</span>
                <span>Humidity</span>
                <span>WiFi Signal</span>
            </div>
            {history_html}
        </div>
        
        <div class="footer">
            <p>Last updated: {current_time} | Auto-refresh in 30s</p>
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
            print(f"History updated: {len(self.history)} readings stored")

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

    def _read_internal_temperature(self):
        """Read internal chip temperature"""
        try:
            reading = self.internal_temp_sensor.read_u16() * (3.3 / 65535)
            temperature = 27 - (reading - 0.706) / 0.001721
            return temperature
        except:
            return 0.0  # Return 0 if sensor fails

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

                                # REAL AI: Record that we made a prediction
                                self.ai_brain.record_prediction(temp, hum)

                                if path == "/feedback":
                                    self._handle_feedback(
                                        client_socket, request_str, temp, hum
                                    )
                                else:
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

    def _handle_feedback(self, client, request_str, current_temp, current_hum):
        """Handle user feedback for neural network training"""
        try:
            # Parse JSON from POST request body
            if "POST" in request_str and "{" in request_str:
                # Extract JSON from request
                json_start = request_str.find("{")
                json_end = request_str.rfind("}") + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = request_str[json_start:json_end]

                    # Simple JSON parsing (avoiding imports)
                    if (
                        '"rating":' in json_str
                        and '"temp":' in json_str
                        and '"humidity":' in json_str
                    ):
                        # Extract rating value
                        rating_start = json_str.find('"rating":') + 9
                        rating_end = json_str.find(",", rating_start)
                        if rating_end == -1:
                            rating_end = json_str.find("}", rating_start)
                        rating = float(json_str[rating_start:rating_end].strip())

                        # Extract temperature
                        temp_start = json_str.find('"temp":') + 7
                        temp_end = json_str.find(",", temp_start)
                        if temp_end == -1:
                            temp_end = json_str.find("}", temp_start)
                        temp = float(json_str[temp_start:temp_end].strip())

                        # Extract humidity
                        hum_start = json_str.find('"humidity":') + 11
                        hum_end = json_str.find(",", hum_start)
                        if hum_end == -1:
                            hum_end = json_str.find("}", hum_start)
                        humidity = float(json_str[hum_start:hum_end].strip())

                        # REAL AI LEARNING: Train neural network with user feedback
                        self.ai_brain.learn_from_user_feedback(temp, humidity, rating)

                        # Send success response
                        response = "OK"
                        headers = "HTTP/1.1 200 OK\r\n"
                        headers += "Content-Type: text/plain\r\n"
                        headers += "Access-Control-Allow-Origin: *\r\n"
                        headers += "Connection: close\r\n"
                        headers += f"Content-Length: {len(response)}\r\n\r\n"

                        client.send(headers.encode("utf-8"))
                        client.send(response.encode("utf-8"))

                        print(
                            f"✅ Neural network learned from user: {temp}°C, {humidity}% -> {rating} comfort"
                        )
                        return

        except Exception as e:
            print(f"Error processing feedback: {e}")

        # Send error response
        error_response = "Invalid feedback"
        headers = "HTTP/1.1 400 Bad Request\r\n"
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
                    history_html += f'<div class="history-item"><span>{time_str}</span><span>{h_temp:.1f}°C</span><span>{h_hum:.1f}%</span><span>{h_rssi}dBm ({signal_strength})</span></div>'
                else:  # Old format without RSSI (backward compatibility)
                    timestamp, h_temp, h_hum = item
                    time_str = self._format_time(timestamp)
                    history_html += f'<div class="history-item"><span>{time_str}</span><span>{h_temp:.1f}°C</span><span>{h_hum:.1f}%</span><span>No WiFi data</span></div>'
        else:
            history_html = '<div class="history-item"><span>No historical data yet</span><span>-</span><span>-</span><span>-</span></div>'

        # Format start time
        start_time_str = self._format_time(self.start_time)

        # Get current time for footer
        current_time_str = self._format_time(time.time())

        current_rssi = self.wifi_manager.get_rssi()
        internal_temp = self._read_internal_temperature()

        try:
            # REAL AI: Get neural network prediction
            comfort_score = self.ai_brain.predict_comfort_level(temp, hum)
            comfort_description = self.ai_brain.get_comfort_description(comfort_score)
            ai_stats = self.ai_brain.get_learning_stats()

            response = self.html_template.format(
                temp=temp,
                hum=hum,
                internal_temp=internal_temp,
                start_time=start_time_str,
                wifi_rssi=current_rssi,
                wifi_strength=self._get_signal_strength(current_rssi),
                uptime=self._get_uptime(),
                ip_address=self.wifi_manager.get_ip(),
                history_html=history_html,
                history_count=len(self.history),
                current_time=current_time_str,
                # Real AI predictions
                comfort_score=comfort_score,
                comfort_description=comfort_description,
                prediction_count=ai_stats["predictions_made"],
                temp_weight=ai_stats["temp_weight"],
                humidity_weight=ai_stats["humidity_weight"],
                bias=ai_stats["bias"],
            )

        except Exception as e:
            print(f"Error formatting template: {e}")
            # Send simple fallback page
            response = f"""<!DOCTYPE html>
<html>
<head><title>Weather Station</title></head>
<body>
<h1>Weather Station</h1>
<p>Temperature: {temp:.1f}°C</p>
<p>Humidity: {hum:.1f}%</p>
<p>Error: {e}</p>
</body>
</html>"""

        try:
            # Encode response to bytes first to get correct length
            response_bytes = response.encode("utf-8")

            print(f"Response length: {len(response_bytes)} bytes")

            # Remove Content-Length header to avoid mismatch issues
            headers = "HTTP/1.1 200 OK\r\n"
            headers += "Content-Type: text/html; charset=utf-8\r\n"
            headers += "Access-Control-Allow-Origin: *\r\n"
            headers += "Connection: close\r\n\r\n"

            # Send in chunks to prevent truncation
            client.send(headers.encode("utf-8"))

            # Send response in small chunks with retry logic
            sent = 0
            while sent < len(response_bytes):
                try:
                    chunk_size = min(512, len(response_bytes) - sent)
                    chunk = response_bytes[sent : sent + chunk_size]
                    bytes_sent = client.send(chunk)
                    sent += bytes_sent
                except OSError as e:
                    if e.args[0] == 11:  # EAGAIN - socket buffer full
                        continue  # Retry
                    else:
                        raise

            print(f"Successfully sent {sent}/{len(response_bytes)} bytes")

        except Exception as e:
            print(f"Error sending response: {e}")
            # Send minimal error response
            error_response = (
                "HTTP/1.1 500 Internal Server Error\r\n\r\nError generating page"
            )
            client.send(error_response.encode("utf-8"))

    def stop(self):
        """Stop the web server"""
        if self.server_socket:
            self.poller.unregister(self.server_socket)
            self.server_socket.close()
            self.server_socket = None
            print("Web server stopped")
