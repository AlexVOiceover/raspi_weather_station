# Raspberry Pi Pico W Weather Station

A simple weather monitoring project using the Raspberry Pi Pico W and DHT22 sensor.

## About

This project was created for a workshop on development boards. It demonstrates how to:
- Connect a DHT22 temperature and humidity sensor to a Raspberry Pi Pico W
- Create a basic web server to display sensor readings
- Use the built-in LED for status indication

## Hardware Requirements

- Raspberry Pi Pico W
- DHT22 temperature and humidity sensor
- Connecting wires

## Setup

1. Connect the DHT22 sensor to GPIO pin 2
2. Copy the files to your Pico W
3. Configure your WiFi credentials in `config.py` or modify the fallback credentials in `main.py`
4. Run the script and access the web interface at the displayed IP address

## Features

- Real-time temperature and humidity monitoring
- Simple web interface
- WiFi connectivity
- LED status indicators for startup, connection, and errors