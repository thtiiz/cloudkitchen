# Complete project details at https://RandomNerdTutorials.com

from machine import Pin
import time
import network
from esp import espnow
# from adafruit_debouncer import Debouncer
BUTTON_A_PIN = const(17)
BUTTON_B_PIN = const(5)
is_served = True


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


def send_order():
    is_served = False
    if(~is_served):
        led.value(1)
    elif(is_served):
        led.value(0)
    global order = {}


def button_a_callback(pin):
    order[table_num] = 1
    order[chef_num] = 1
    print("order1")
    send_order()


def button_b_callback(pin):
    order.append(2)
    print("order2")
    send_order()


w = network.WLAN()
w.active(True)

BROADCAST = b'\x30AEA412640'

espnow.init()
espnow.add_peer(BROADCAST)


count = 0
while True:
    count += 1
    msg = "Count = {}".format(count)
    print("Sending:", msg)
    espnow.send(BROADCAST, msg)
    time.sleep(1)

# button_a = Button(pin=Pin(BUTTON_A_PIN, mode=Pin.IN, pull=Pin.PULL_UP), callback=button_a_callback)
# button_b = Button(pin=Pin(BUTTON_B_PIN, mode=Pin.IN, pull=Pin.PULL_UP), callback=button_b_callback)
button_a = Button(pin=Pin(BUTTON_A_PIN, mode=Pin.IN,
                          pull=Pin.PULL_UP), callback=button_a_callback)
button_b = Button(pin=Pin(BUTTON_B_PIN, mode=Pin.IN,
                          pull=Pin.PULL_UP), callback=button_b_callback)
