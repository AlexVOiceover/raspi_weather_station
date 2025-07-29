# Simple web server for weather data
import socket

class WeatherWebServer:
    def __init__(self, wifi_manager):
        self.wifi_manager = wifi_manager
        self.socket = None
        self.html_template = """<!DOCTYPE html>
<html>
  <head><title>Pico W DHT22</title></head>
  <body><h1>Temperature and Humidity</h1>
    <p>Temp: {temp:.1f} &deg;C<br>Hum: {hum:.1f} %</p>
  </body>
</html>"""
    
    def start(self):
        """Start the web server"""
        if not self.wifi_manager.is_connected():
            raise Exception("WiFi not connected")
        
        addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
        self.socket = socket.socket()
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(addr)
        self.socket.listen(1)
        print(f"HTTP server at http://{self.wifi_manager.get_ip()}:80")
        return True
    
    def handle_request(self, temp, hum, timeout=0.5):
        """Handle incoming web requests (non-blocking)"""
        if not self.socket:
            return
        
        self.socket.settimeout(timeout)
        try:
            cl, addr = self.socket.accept()
            print("Web request from", addr)
            
            try:
                # Read HTTP request with timeout
                cl.settimeout(2.0)  # Give client time to send request
                request = cl.recv(1024)
                
                if not request:
                    cl.close()
                    return
                    
                request_str = request.decode("utf-8")
                
                # Parse request path
                request_line = request_str.split("\r\n")[0]
                path = request_line.split(" ")[1] if len(request_line.split(" ")) > 1 else "/"
                
                if path == "/favicon.ico":
                    # Return 404 for favicon
                    self._send_404(cl)
                else:
                    # Serve main page
                    self._send_weather_page(cl, temp, hum)
                    
            except Exception as e:
                print(f"Error processing request: {e}")
            finally:
                try:
                    cl.close()
                except:
                    pass  # Socket may already be closed
            
        except OSError:
            # No incoming connections (normal for non-blocking)
            pass
        except Exception as e:
            print(f"Server error: {e}")
            # Try to restart server if needed
            self._restart_if_needed()
    
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
        response = self.html_template.format(temp=temp, hum=hum)
        headers = "HTTP/1.1 200 OK\r\n"
        headers += "Content-Type: text/html; charset=utf-8\r\n"
        headers += "Access-Control-Allow-Origin: *\r\n"
        headers += "Connection: close\r\n"
        headers += f"Content-Length: {len(response)}\r\n\r\n"
        
        client.send(headers.encode("utf-8"))
        client.send(response.encode("utf-8"))
    
    def _restart_if_needed(self):
        """Restart server if socket is broken"""
        try:
            if self.socket:
                self.socket.close()
        except:
            pass
        
        try:
            # Restart server
            self.start()
            print("Web server restarted")
        except Exception as e:
            print(f"Failed to restart server: {e}")