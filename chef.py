import time
import network
from esp import espnow
from machine import Pin, I2C, Timer, PWM
from ssd1306 import SSD1306_I2C
import json

TIME_REFILL = 2000
TIME_COOKING = 2000

BROADCAST = b'\xFF' * 6

i2c_1 = I2C(scl=Pin(22),sda=Pin(21),freq=100000)
chef1_oled = SSD1306_I2C(128,64,i2c_1)

i2c_2 = I2C(scl=Pin(17),sda=Pin(16),freq=100000)
chef2_oled = SSD1306_I2C(128,64,i2c_2)

Chefs = [
    {},
    {
        'food_remain': 2,
        'queue': [],
        'out_order_queue': [],
        'current_queue': 0
    },
    {
        'food_remain': 20,
        'queue': [],
        'out_order_queue': [],
        'current_queue': 0
    }
]

def isCustomer(mac):
    castmac = "".join(["{:02X}".format(x) for x in mac])
    return castmac in ['4C11AE793A28', 'A4CF128FD130', 'A4CF128FB8AC']

def init_wifi():
    w = network.WLAN()
    w.active(True)
    espnow.init()
    espnow.add_peer(BROADCAST)

def update_oled(chef_num):
    global Chefs
    queue = Chefs[chef_num]['queue'] + Chefs[chef_num]['out_order_queue']
    queue_1 =  ",".join([str(q) for q in queue[:5]])
    queue_2 =  ",".join([str(q) for q in queue[5:]])
    if(chef_num == 1):
        chef1_oled.fill(0)
        chef1_oled.text('Chef 1: Hello!!',0,0)
        chef1_oled.text('food remain: {}'.format(Chefs[1]['food_remain']),0,15)
        chef1_oled.text('queue: {}'.format(queue_1),0,30)
        chef1_oled.text(queue_2,0,45)
        chef1_oled.show()
    else:
        chef2_oled.fill(0)
        chef2_oled.text('Chef 2: Hello!!',0,0)
        chef2_oled.text('food remain: {}'.format(Chefs[2]['food_remain']),0,15)
        chef2_oled.text('queue: {}'.format(queue_1),0,30)
        chef2_oled.text(queue_2,0,45)
        chef2_oled.show()

def serve_from_chef1(timer):
    global Chefs
    table_num = Chefs[1]['queue'].pop(0)
    Chefs[1]['current_queue'] -= 1
    update_oled(1)
    handleQueue(1)
    send_serve_msg(1, table_num)

def serve_from_chef2(timer):
    global Chefs
    table_num = Chefs[2]['queue'].pop(0)
    Chefs[2]['current_queue'] -= 1
    update_oled(2)
    handleQueue(2)
    send_serve_msg(2, table_num)

def refill_food_chef1(timer):
    update_oled(1)
    Chefs[1]['food_remain'] = 20 - len(Chefs[1]['out_order_queue'])
    Chefs[1]['queue'] += Chefs[1]['out_order_queue']
    Chefs[1]['out_order_queue'] = []

def refill_food_chef2(timer):
    update_oled(2)
    Chefs[2]['food_remain'] = 20 - len(Chefs[2]['out_order_queue'])
    Chefs[2]['queue'] += Chefs[2]['out_order_queue']
    Chefs[2]['out_order_queue'] = []

def send_serve_msg(chef_num, table_num):
    msg = {'table_num': table_num, 'chef_num': chef_num}
    espnow.send(BROADCAST, json.dumps(msg))

def handleQueue(chef_num):
    # print('handle', chef_num)
    if(len(Chefs[chef_num]['queue']) > 0 ):
        Chefs[chef_num]['current_queue'] += 1
        if(chef_num == 1):
            print('do 1')
            tim = Timer(1)
            tim.init(period=TIME_COOKING, mode=Timer.ONE_SHOT, callback=serve_from_chef1)
        else:
            print('do 2')
            tim = Timer(2)
            tim.init(period=TIME_COOKING, mode=Timer.ONE_SHOT, callback=serve_from_chef2)
    
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
        Chefs[chef_num]['food_remain'] -= 1 # ลดอาหาร
        Chefs[chef_num]['queue'].append(table_num) # เพ่ิ่มเข้า queue
        
        # refill food
        if(Chefs[chef_num]['food_remain'] == 0): 
            if(chef_num == 1):
                tim = Timer(3)
                tim.init(period=TIME_REFILL, mode=Timer.ONE_SHOT, callback=refill_food_chef1)
            else:
                tim = Timer(3)
                tim.init(period=TIME_REFILL, mode=Timer.ONE_SHOT, callback=refill_food_chef2)
        if(Chefs[chef_num]['current_queue'] == 0): # ถ้าเชฟว่างก็ให้ทำอาหาร
            handleQueue(chef_num)
    else:
        Chefs[chef_num]['out_order_queue'].append(table_num)
        print('out of order')
        # pass
    update_oled(chef_num)
    
if(__name__ == "__main__"):
    update_oled(1)
    update_oled(2)
    init_wifi()
    espnow.on_recv(onOrder)
    while(1):
        pass
