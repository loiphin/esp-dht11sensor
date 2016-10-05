# Import libraries and settings

from settings import *
import http_client
import machine
import time
import dht
import network
import webrepl

# Run the ESP8266 at max speed
machine.freq(160000000)

# Load WebREPL
webrepl.start()	


# Functions

def measure():
    d = dht.DHT11(machine.Pin(4))
    d.measure()
    temp = d.temperature()
    hum = d.humidity()
    print('Temp: ', temp)  # eg. 23.6 (°C)
    print('Humidity: ', hum)  # eg. 41.3 (% RH)
    return temp, hum


def do_connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect(WIFI_SSID, WIFI_KEY)
        while not wlan.isconnected():
            time.sleep(0.1)
    print('network config:', wlan.ifconfig())


def go_sleep():
    # put the device to sleep for 60 seconds
    time.sleep(60)

	
def post_data(temp,hum):
	http_client.get('https://api.thingspeak.com/update?api_key=' + APIKEY + '&field1=' + str(temp) + '&field2=' + str(hum))
	print('Posted to Thingspeak')
	

	
	
	
# Start of actual program

while True:
    do_connect()
    (temp, hum) = measure()
    post_data(temp,hum)
    go_sleep()
