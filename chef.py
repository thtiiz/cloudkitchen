import time
import network
from esp import espnow
from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
import json

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
    Chef(),
    Chef(),
    Chef()
]

# Chefs = [
#     {},
#     {
#         'food_remain': 10,
#         'queue': []
#     },
#     {
#         'food_remain': 15,
#         'queue': []
#     }
# ]

def isCustomer(mac):
    castmac = "".join(["{:02X}".format(x) for x in mac])
    return castmac in ['4C11AE793A28', 'A4CF128FD130', 'A4CF128FB8AC']

def init_chef():
    i2c_1 = I2C(scl=Pin(22),sda=Pin(21),freq=100000)
    chef1 = SSD1306_I2C(128,64,i2c_1)
    chef1.fill(0)
    chef1.text('asdfasdf',0,0)
    chef1.show()

    i2c_2 = I2C(scl=Pin(17),sda=Pin(16),freq=100000)
    chef2 = SSD1306_I2C(128,64,i2c_2)
    chef2.fill(0)
    chef2.text('asdfasdf',0,0)
    chef2.show()

def init_wifi():
    w = network.WLAN()
    w.active(True)
    espnow.init()

def printMsg(chef, msg):
    chef.fill(0)
    chef.text(msg,0,0)
    chef.show()
    
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
        Chefs[chef_num]['queue'].append(table_num)
    else:
        pass
    


init_chef()
init_wifi()
espnow.on_recv(onOrder)

while(1):
    print(Chefs[1].food_remain)
    time.sleep(1)
    pass
