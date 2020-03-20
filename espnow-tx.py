# Complete project details at https://RandomNerdTutorials.com

from machine import Pin
import time
import network
from esp import espnow
import json
# from adafruit_debouncer import Debouncer
led = Pin(16, Pin.OUT)
BUTTON_A_PIN = const(17)
BUTTON_B_PIN = const(5)
is_served = True

w = network.WLAN()
w.active(True)

# BROADCAST = b'\x30'+b'\xAE'+b'\xA4'+b'\x12'+b'\x64'+b'\xE0' #AEA41264E0
BROADCAST = b'\xFF'*6
espnow.init()
espnow.add_peer(BROADCAST)


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


def ledIsOn():
    is_served = False
    if(~is_served):
        led.value(1)
    elif(is_served):
        led.value(0)


def button_a_callback(pin):
    print('order1')
    order = {}
    order['table_num'] = 1
    order['chef_num'] = 1
    msg = json.dumps(order)
    espnow.send(BROADCAST, msg)
    ledIsOn()


def button_b_callback(pin):
    print('order2')
    order = {}
    order['table_num'] = 1
    order['chef_num'] = 2
    msg = json.dumps(order)
    espnow.send(BROADCAST, msg)
    ledIsOn()


button_a = Button(pin=Pin(BUTTON_A_PIN, mode=Pin.IN,
                          pull=Pin.PULL_UP), callback=button_a_callback)
button_b = Button(pin=Pin(BUTTON_B_PIN, mode=Pin.IN,
                          pull=Pin.PULL_UP), callback=button_b_callback)
