import time
from utime import sleep_ms
from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
import network
from esp import espnow

def receive_callback(*dobj):
    mac, msg = dobj[0]
    print("Received:", msg)
    print("From:", ":".join(["{:02X}".format(x) for x in mac]))

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
espnow.init()
espnow.on_recv(receive_callback)

i2c = I2C(scl=Pin(22),sda=Pin(21),freq=100000)
oled = SSD1306_I2C(128,64,i2c)
oled.fill(0)
oled.text("ESP32 started...",0,0)
oled.show()

while(1):
    pass