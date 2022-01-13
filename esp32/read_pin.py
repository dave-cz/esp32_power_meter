import gc
import json
import network
import ntptime
from machine import Pin, ADC
from time import sleep, ticks_us, localtime
from urequests import post

with open('config.json', 'r') as f:
    config = json.load(f)

meter = ADC(Pin(config['pin']))
meter.atten(ADC.ATTN_11DB)  # 3.3V full voltage range

data = config['data_len'] * [0]
data_ticks = config['data_len'] * [0]


def meas_send_ticks():
    dt = localtime()
    for i in range(config['data_len']):
        data[i] = meter.read()
        data_ticks[i] = ticks_us()
    dt_str = '%04i-%02i-%02iT%02i:%02i:%02iZ' % dt[:6]
    send_data = json.dumps({
        'payload': data,
        'ticks': data_ticks,
        'dt': dt_str
    }).replace(' ', '')
    try:
        res = post(
            config['url'],
            data=send_data,
            headers=config['headers']
        )
        print(res.status_code)
    except Exception as ex:
        print(ex)
        gc.collect()
    return None


def connect():
    station = network.WLAN(network.STA_IF)
    station.active(True)
    station.connect(config['ssid'], config['password'])

    conn_counter = 0
    while not station.isconnected():
        sleep(1)
        conn_counter += 1
        if conn_counter > 5:
            print('connection to network failed')
            break

    ntptime.settime()
    gc.collect()
    return None
