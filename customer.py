from machine import Pin, I2C
import time
import network
from esp import espnow
from ssd1306 import SSD1306_I2C
import json

# init PIN
led = Pin(16, Pin.OUT)
BUTTON_A_PIN = const(17)
BUTTON_B_PIN = const(5)
BUTTON_C_PIN = const(12)
i2c_1 = I2C(scl=Pin(22), sda=Pin(21), freq=100000)
customer_oled = SSD1306_I2C(128, 64, i2c_1)
is_served = True
TABLE_NUM = 1
COUNT = 0
PRICE = 0
ORDER = {}
ORDER[1] = 0
ORDER[2] = 0

# init WIFI
w = network.WLAN()
w.active(True)

# espnow-tx
BROADCAST = b'\xFF'*6
espnow.init()
espnow.add_peer(BROADCAST)

# espnow-rx


class Button:
    """
    Debounced pin handler
    usage e.g.:
    def button_callback(pin):
        print("Button (%s) changed to: %r" % (pin, pin.value()))
    button_handler = Button(pin=Pin(32, mode=Pin.IN, pull=Pin.PULL_UP), callback=button_callback)
    """

    def __init__(self, pin, callback, trigger=Pin.IRQ_FALLING, min_ago=300):
        self.callback = callback
        self.min_ago = min_ago

        self._blocked = False
        self._next_call = time.ticks_ms() + self.min_ago

        pin.irq(trigger=trigger, handler=self.debounce_handler)

    def call_callback(self, pin):
        self.callback(pin)

    def debounce_handler(self, pin):
        if time.ticks_ms() > self._next_call:
            self._next_call = time.ticks_ms() + self.min_ago
            self.call_callback(pin)
        # else:
        #    print("debounce: %s" % (self._next_call - time.ticks_ms()))


def toggleLED():
    print(is_served)
    if(is_served == False):
        led.value(1)
    elif(is_served):
        led.value(0)


def button_a_callback(pin):
    order = {}
    order['table_num'] = 1
    order['chef_num'] = 1
    print("order1")
    msg = json.dumps(order)
    print("Sending:", msg)
    espnow.send(BROADCAST, msg)
    global is_served
    global COUNT
    global PRICE
    global ORDER
    ORDER[1] += 1
    COUNT += 1
    is_served = False
    toggleLED()


def button_b_callback(pin):
    order = {}
    order['table_num'] = 1
    order['chef_num'] = 2
    print("order2")
    msg = json.dumps(order)
    print("Sending:", msg)
    espnow.send(BROADCAST, msg)
    global is_served
    global COUNT
    global PRICE
    global ORDER
    ORDER[2] += 1
    COUNT += 1
    is_served = False
    toggleLED()


def button_c_callback(pin):
    global PRICE
    PRICE += ORDER[1] * 40
    PRICE += ORDER[2] * 50
    update_oled()
    PRICE = 0


def update_oled():
    global PRICE
    msg = str(PRICE)
    print("Price", msg)
    customer_oled(0)
    customer_oled.text(msg, 0, 20)
    customer_oled.show()


def isChef(mac):
    castmac = "".join(["{:02X}".format(x) for x in mac])
    return castmac in ['30AEA41264E0']


def receive_callback(*dobj):
    mac, order_served = dobj[0]
    order = json.loads(order_served)

    print(json.loads(order_served))
    if(not isChef(mac)):
        print('is not a chef')
        return None
    elif(TABLE_NUM == order['table_num']):
        global is_served
        global COUNT
        COUNT -= 1
        if(COUNT == 0):
            is_served = True
            toggleLED()


espnow.on_recv(receive_callback)

button_a = Button(pin=Pin(BUTTON_A_PIN, mode=Pin.IN,
                          pull=Pin.PULL_UP), callback=button_a_callback)
button_b = Button(pin=Pin(BUTTON_B_PIN, mode=Pin.IN,
                          pull=Pin.PULL_UP), callback=button_b_callback)
button_c = Button(pin=Pin(BUTTON_C_PIN, mode=Pin.IN,
                          pull=Pin.PULL_UP), callback=button_c_callback)
