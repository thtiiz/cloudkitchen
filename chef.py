import time
import network
from esp import espnow
from machine import Pin, I2C, Timer
from ssd1306 import SSD1306_I2C
import json

i2c_1 = I2C(scl=Pin(22), sda=Pin(21), freq=100000)
chef1_oled = SSD1306_I2C(128, 64, i2c_1)

i2c_2 = I2C(scl=Pin(17), sda=Pin(16), freq=100000)
chef2_oled = SSD1306_I2C(128, 64, i2c_2)


class Chef:
    def __init__(self):
        # self.led = led
        self.food_remain = 10
        self.queue = []
        # timer.callback(self.cb)

    def cb(self, tim):
        print('Serve!!!!')
        # self.led.toggle()


Chefs = [
    {},
    {
        'food_remain': 10,
        'queue': [],
        'current_queue': 0
    },
    {
        'food_remain': 15,
        'queue': [],
        'current_queue': 0
    }
]


def isCustomer(mac):
    castmac = "".join(["{:02X}".format(x) for x in mac])
    return castmac in ['4C11AE793A28', 'A4CF128FD130', 'A4CF128FB8AC']


def init_chef():

    chef1_oled.fill(0)
    chef1_oled.text('Chef1: Hello!!', 0, 0)
    chef1_oled.show()

    chef2_oled.fill(0)
    chef2_oled.text('Chef2: Hello!!', 0, 0)
    chef2_oled.show()


def init_wifi():
    w = network.WLAN()
    w.active(True)
    espnow.init()


def update_oled(chef_num):
    msg = ",".join(Chefs[chef_num]['queue'])
    print("chef queue(table):", msg)
    if(chef_num == 1):
        chef1_oled.fill(0)
        chef1_oled.text(msg, 0, 20)
        chef1_oled.show()
    else:
        chef2_oled.fill(0)
        chef2_oled.text(msg, 0, 20)
        chef2_oled.show()


def serve_from_chef1(timer):
    Chefs[1]['queue'].pop(0)
    update_oled(1)


def serve_from_chef2(timer):
    Chefs[2]['queue'].pop(0)
    update_oled(2)


def onOrder(*order):
    mac, order_detail = order[0]

    # table_num: หมายเลขโต๊ะ
    # chef_num: หมายเลขเชฟ
    if(not isCustomer(mac)):
        print('is not customer')
        return None

    detail = json.loads(order_detail)
    chef_num = detail['chef_num']
    table_num = detail['table_num']

    if(Chefs[chef_num]['food_remain'] > 0):
        Chefs[chef_num]['food_remain'] -= 1
        Chefs[chef_num]['queue'].append(str(table_num))
        Chefs[chef_num]['current_queue'] += 1
        if(chef_num == 1):
            update_oled(1)
            tim = Timer(Chefs[1]['current_queue'])
            tim.init(period=2500, mode=Timer.ONE_SHOT,
                     callback=serve_from_chef1)
        else:
            update_oled(2)
            tim = Timer(200 + Chefs[2]['current_queue'])
            tim.init(period=2500, mode=Timer.ONE_SHOT,
                     callback=serve_from_chef2)
    else:
        pass


init_chef()
init_wifi()
espnow.on_recv(onOrder)

while(1):
    # print(Chefs[1])
    # time.sleep(1)
    pass
