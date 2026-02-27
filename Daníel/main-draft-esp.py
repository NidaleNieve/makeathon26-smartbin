#Setup
    #libraries
    #GPIO pin
    #confidence score minimum
    #motor starting positions

import uasyncio as asyncio
from machine import Pin
from rasp_connection_async import Connector
from machine import Pin
import time


motion_sensor_in = Pin(23, Pin.IN)
motion_sensor_out = Pin(2, Pin.OUT)


#setting up BLE Server and listener.
connection = Connector()


#Reset motoros to starting positions



#Main trash Function, runs when received message from PI (stops the asyncio threads)
    #Basic If or else statements. Depending on the message. "Up", "Down", "Left", "Right" and the confidence score
        #If confidence score is less than X amount then move to Waste position.

        #Each message moves the stepper motor Y amount of degrees. 

    #Pushes Servo motor to open the lid

    #Servo goes down.

    #Resets Stepper to original position

def trash():


#Send function
    #Send BLE Packet to PI with "Start".

def send():
    connection.send("start")



#Infinite asyncio loop that listens for message from PI
    #when it does it calls the main function with the message from the pi as the argument. 

connection.attach("cmd", on_ble_command)
sensor_pin = Pin(14, Pin.IN, Pin.PULL_UP)  # Change pin/pull to match your sensor


#Infinite asyncio loop that looks for movement from movement sensor
    #when it does it runs the Send function. 
async def sensor_listener():
    pass

async def main():
    asyncio.create_task(connection.listen())
    asyncio.create_task(sensor_listener(movement_sensor, send))
    while True:
        await asyncio.sleep(1)

asyncio.run(main())