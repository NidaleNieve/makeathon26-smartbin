import time
import rasp_connection

from servo import Servo
from machine import Pin

print("Start program.")

servo = Servo(Pin(6), freq=50, min_us=500, max_us=2500)

connection = rasp_connection.Connector()

# Example Usage, feel free to change or comment out whenever you need to use main for something
def left():
    print("left!")

def right():
    print("right!")

def up():
    print("up!")

def down():
    print("down!")
    connection.send("test")

connection.attach("left", left)
connection.attach("right", right)
connection.attach("up", up)
connection.attach("down", down)

#Start position
servo.write_angle(0)

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    pass