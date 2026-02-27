from machine import Pin
import time

pin_in = Pin(23, Pin.IN)
pin_out = Pin(2, Pin.OUT)

while True:
    status = pin_in.value()
    pin_out.value(status)
    