# Simple web server for weather data
import socket
import select


class WeatherWebServer:
    def __init__(self, wifi_manager):
        self.wifi_manager = wifi_manager
        self.server_socket = None
        self.poller = select.poll()
        self.clients = {}
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
        self.server_socket = socket.socket()
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(addr)
        self.server_socket.listen(5)
        self.server_socket.setblocking(False)
        self.poller.register(self.server_socket, select.POLLIN)
        print(f"HTTP server at http://{self.wifi_manager.get_ip()}:80")
        return True

    def handle_request(self, temp, hum):
        """Handle incoming web requests using polling"""
        if not self.server_socket:
            return

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
        response = self.html_template.format(temp=temp, hum=hum)
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
