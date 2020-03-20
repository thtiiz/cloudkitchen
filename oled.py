import time
from utime import sleep_ms
from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
import network
from esp import espnow

def connect_wifi():
    ssid = 'porporpor'
    passwd = 'roproprop'
    ap = network.WLAN(network.AP_IF)
    ap.active(False)

    print("Connecting to WiFi '%s'. This takes some time..." % ssid)

    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    wifi.connect(ssid, passwd)

    while wifi.status() == network.STAT_CONNECTING:
        sleep_ms(100)

    if wifi.isconnected():
        print("Connection established. My IP is " + str(wifi.ifconfig()[0]))
        return True
    else:
        status = wifi.status()
        if status == network.STAT_WRONG_PASSWORD:
            status = "WRONG PASSWORD"
        elif status == network.STAT_NO_AP_FOUND:
            status = "NETWORK '%s' NOT FOUND" % ssid
        else:
            status = "Status code %d" % status
        print("Connection failed: %s!" % status)
        return False



connect_wifi()

BROADCAST = b'\xFF' * 6

espnow.init()
espnow.add_peer(BROADCAST)

count = 0
while True:
    count += 1
    msg = "Count = {}".format(count)
    print("Sending:", msg)
    espnow.send(BROADCAST, msg)
    time.sleep(3)
