from time import sleep
from read_pin import connect, meas_send_ticks

connect()

while True:
    meas_send_ticks()
    sleep(10)
