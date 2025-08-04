# WiFi connection debug script
# Upload and run this to diagnose WiFi issues

from machine import Pin, I2C
import network
import time
import sys

print("=== WiFi Debug Script ===")

# Test 1: Basic WiFi hardware
print("1. Testing WiFi hardware...")
try:
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    print("   ✓ WiFi hardware OK")
except Exception as e:
    print(f"   ✗ WiFi hardware error: {e}")
    sys.exit()

# Test 2: Config file
print("2. Testing config file...")
try:
    from config import SSID, PASSWORD
    print(f"   ✓ Config loaded: SSID='{SSID}'")
except ImportError as e:
    print(f"   ✗ Config error: {e}")
    sys.exit()

# Test 3: Network scan
print("3. Scanning networks...")
try:
    networks = wlan.scan()
    print(f"   ✓ Found {len(networks)} networks:")
    found_target = False
    for net in networks:
        ssid = net[0].decode('utf-8')
        print(f"     - {ssid}")
        if ssid == SSID:
            found_target = True
            print(f"       ✓ Target network '{SSID}' found!")
    
    if not found_target:
        print(f"   ✗ Target network '{SSID}' not found!")
        print("   Check SSID spelling and ensure network is broadcasting")
except Exception as e:
    print(f"   ✗ Network scan error: {e}")

# Test 4: Connection attempt
print("4. Testing connection...")
try:
    print(f"   Connecting to '{SSID}'...")
    wlan.disconnect()
    time.sleep(1)
    wlan.connect(SSID, PASSWORD)
    
    # Wait with detailed status
    for i in range(30):  # 15 second timeout
        status = wlan.status()
        print(f"   Attempt {i+1}/30, Status: {status}")
        
        if status == 3:  # Connected
            print("   ✓ Connected successfully!")
            print(f"   IP: {wlan.ifconfig()[0]}")
            break
        elif status < 0:  # Error
            print(f"   ✗ Connection failed with status: {status}")
            if status == -3:
                print("     Network not found")
            elif status == -2:
                print("     Wrong password or security type")
            break
            
        time.sleep(0.5)
    else:
        print("   ✗ Connection timeout")
        print(f"   Final status: {wlan.status()}")

except Exception as e:
    print(f"   ✗ Connection error: {e}")

print("=== Debug Complete ===")