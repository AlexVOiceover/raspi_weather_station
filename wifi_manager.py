# WiFi connection management
import network
import time

class WiFiManager:
    def __init__(self, ssid, password, display_manager=None, led_controller=None):
        self.ssid = ssid
        self.password = password
        self.display_manager = display_manager
        self.led_controller = led_controller
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)
    
    def scan_networks(self):
        """Scan and return available networks"""
        print("WiFi activo:", self.wlan.active())
        print("Redes disponibles:")
        networks = self.wlan.scan()
        for net in networks:
            print("  ", net[0].decode("utf-8"))
        return networks
    
    def connect(self, timeout=60):
        """Connect to WiFi with timeout and display updates"""
        print(f"Conectando a: {self.ssid}")
        self.wlan.disconnect()
        time.sleep(1)
        self.wlan.connect(self.ssid, self.password)
        
        print("Conectando a Wi-Fi...", end="")
        max_wait = timeout
        
        while max_wait > 0:
            # Show connection progress on display if available
            if self.display_manager:
                self.display_manager.show_wifi_connecting(self.ssid, max_wait, timeout)
            
            status = self.wlan.status()
            if status == 3:  # Connected and got IP
                break
            elif status < 0:  # Connection failed
                print(f"\nError de conexión: {status}")
                if self.led_controller:
                    self.led_controller.error_pattern()
                return False
                
            max_wait -= 1
            time.sleep(0.5)
            print(".", end="")
            
            # LED feedback every 10 attempts
            if self.led_controller and max_wait % 10 == 0:
                self.led_controller.blink(1, 0.1)
        
        if self.wlan.isconnected():
            print(f"\nConectado: {self.wlan.ifconfig()}")
            if self.led_controller:
                self.led_controller.blink(2, 0.3)  # Success pattern
            return True
        else:
            status = self.wlan.status()
            print("\nFallo conexión Wi-Fi")
            print("Status:", status)
            
            # Show error on display
            if self.display_manager:
                self.display_manager.show_wifi_error(self.ssid, status)
            
            if self.led_controller:
                self.led_controller.error_pattern()
            return False
    
    def is_connected(self):
        """Check if WiFi is connected"""
        return self.wlan.isconnected()
    
    def get_rssi(self):
        """Get WiFi signal strength"""
        return self.wlan.status('rssi') if self.is_connected() else -100
    
    def get_ip(self):
        """Get IP address"""
        return self.wlan.ifconfig()[0] if self.is_connected() else None