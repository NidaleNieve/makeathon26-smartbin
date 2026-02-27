import time
import rasp_connection

print("Start program.")

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



try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    pass