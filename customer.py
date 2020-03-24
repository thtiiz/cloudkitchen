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
TABLE_NUM = 2
COUNT = 0
PRICE = 0
ORDER = {}
ORDER[1] = 0
ORDER[2] = 0
PRICE_1 = 40
PRICE_2 = 50
STATE = 'ORDER'
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


def init_display():
    customer_oled.fill(0)
    msg_table = 'Table {}'.format(TABLE_NUM)
    customer_oled.text(msg_table, 0, 0)
    customer_oled.show()


def update_cooking():
    customer_oled.fill(0)
    msg_table = 'Table {}'.format(TABLE_NUM)
    customer_oled.text(msg_table, 0, 0)
    customer_oled.show()
    msg = 'Cooking . . .'
    customer_oled.text(msg, 0, 30)
    customer_oled.show()


def toggleLED():
    print(is_served)
    if(is_served == False):
        led.value(1)
        update_cooking()
    elif(is_served):
        led.value(0)
        init_display()


def button_a_callback(pin):
    global STATE
    if(STATE == 'ORDER'):
        order = {}
        order['table_num'] = TABLE_NUM
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
    global STATE
    if(STATE == 'ORDER'):
        order = {}
        order['table_num'] = TABLE_NUM
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
    global STATE
    if(STATE == 'ORDER'):
        if(COUNT == 0):
            global PRICE
            global ORDER
            PRICE += ORDER[1] * PRICE_1
            PRICE += ORDER[2] * PRICE_2
            update_oled()
            PRICE = 0
            ORDER[1] = 0
            ORDER[2] = 0
            STATE = 'SERVE'
    elif(STATE == 'SERVE'):
        init_display()
        STATE = 'ORDER'


def update_oled():
    global PRICE
    msg_1 = ""
    msg_1_1 = ""
    msg_2 = ""
    msg_2_1 = ""
    y = 0
    customer_oled.fill(0)
    if(ORDER[1] > 0):
        msg_1 = 'Chef 1: ' + \
            str(ORDER[1]) + ' orders'
        msg_1_1 = 'price: ' + \
            str(ORDER[1] * PRICE_1) + ' Baht'
        customer_oled.text(msg_1, 0, 0)
        customer_oled.text(msg_1_1, 0, 12)
        y += 24
    if(ORDER[2] > 0):
        msg_2 = 'Chef 2: ' + \
            str(ORDER[2]) + ' orders'
        msg_2_1 = 'price: ' + \
            str(ORDER[2] * PRICE_2) + ' Baht'
        customer_oled.text(msg_2, 0, y)
        customer_oled.text(msg_2_1, 0, y+12)
        y += 24
    msg = 'Total: ' + str(PRICE)
    print("Price", msg)
    customer_oled.text(msg, 0, y)
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

button_a = Button(pin=Pin(BUTTON_A_PIN, mode=Pin.IN, pull=Pin.PULL_UP), callback=button_a_callback)
button_b = Button(pin=Pin(BUTTON_B_PIN, mode=Pin.IN, pull=Pin.PULL_UP), callback=button_b_callback)
button_c = Button(pin=Pin(BUTTON_C_PIN, mode=Pin.IN, pull=Pin.PULL_UP), callback=button_c_callback)
init_display()
