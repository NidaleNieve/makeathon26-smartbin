import time
import rasp_connection

from servo import Servo
from machine import Pin

print("Start program.")

motion_sensor = Pin(5, Pin.IN)
servo = Servo(Pin(6), freq=50, min_us=500, max_us=2500)

connection = rasp_connection.Connector()

# Example Usage, feel free to change or comment out whenever you need to use main for something

def test():
    print("test!")
    connection.send("test")

def send_motion(p):
    print("motion found")
    connection.send("motion")

# Command Attachments/Callbacks & IRQ Callbacks
connection.attach("test", test)
motion_sensor.irq(send_motion, Pin.IRQ_RISING)

#Start position
servo.write_angle(0)

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    pass