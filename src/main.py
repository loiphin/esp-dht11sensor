from settings import *
import http_client2
import machine
import time
import dht
import network
import os
import ujson
import esp

# Variables to set
WIFI_SSID = 'your-wifi-network'
WIFI_KEY = 'your-password'


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


def init_timer():
    tim = machine.Timer(-1)
    tim.init(period=2000, mode=machine.Timer.PERIODIC, callback=measure)


def go_sleep():
    # set RTC.ALARM0 to fire after 10 seconds (waking the device)
    rtc.alarm(rtc.ALARM0, 60 * 1000 * 5)

    # put the device to sleep
    machine.deepsleep()
    #import time
    #time.sleep(15)


def post_data(settings, temp, hum):
    if 'channelkey' not in settings.keys():
        create_channel(settings)

    head = {'THINGSPEAKAPIKEY': settings['channelkey']}
    r = http_client2.post('https://api.thingspeak.com/update.json', headers=head, json={'field1': temp, 'field2': hum})
    print(r.json())

def create_channel(settings):
    wlan = network.WLAN(network.STA_IF)
    channel_definition = {
        'api_key' : APIKEY,
        'field1': 'temperature',
        'field2': 'humidity',
        'name' : str(wlan.config('mac') ),
        'public_flag' : 'false'}
    r = http_client2.post('https://api.thingspeak.com/channels.json', json=channel_definition)
    print(r.json())
    settings['channelkey'] = r.json()["api_keys"][0]["api_key"]


def get_settings():
    ret = {}
    if 'settings.json' in os.listdir():
        f = open('settings.json')
        ret = ujson.loads(f.readall())
        f.close()
    return ret

def write_settings(settings):
    f = open('settings.json', 'w')
    f.write(ujson.dumps(settings))
    f.close()


# configure RTC.ALARM0 to be able to wake the device
rtc = machine.RTC()
rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)

# check if the device woke from a deep sleep
if machine.reset_cause() == machine.DEEPSLEEP_RESET:
    print('woke from a deep sleep')

while True:
    do_connect()
    settings = get_settings()
    (temp, hum) = measure()
    post_data(settings, temp, hum)
    write_settings(settings)
    go_sleep()
