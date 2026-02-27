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


min_confidence_score = 60.0

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
def trash(message):
    try:
        # Expecting message format: "category,confidence" (e.g., "paper,85")
        parts = message.split(',')
        #error handling
        if len(parts) != 2:
            print("Invalid message format")
            return
        
        category = parts[0].strip().lower() #trash type
        confidence = float(parts[1].strip()) #condidence score
        
        #If the trash detected doesnt meet the min confidence score, then its waste
        if confidence < min_confidence_score:
            category = "waste"
            
        #move motor based on trash
        if category == "paper":
            print("Moving stepper to Paper position")
            #Stepper code
            pass
        elif category == "plastic":
            print("Moving stepper to Plastic position")
            #Stepper code
            pass
        elif category == "glass":
            print("Moving stepper to Glass position")
            #Stepper code
            pass
        else:
            print("Moving stepper to Waste position")
            #Stepper code
            pass

            
        #Moves servo to push the lid open
        print("Pushing Servo motor to open the lid")
        #Servo code
        time.sleep(2) #Time it takes to move
        
        print("Servo goes down")
        #Servo code
        time.sleep(2) #Time it takes to move

        print("Resetting Stepper to original position")
        #Stepper code
        
    except Exception as e:
        print(f"Error processing message: {e}")    

#Send function
    #Send BLE Packet to PI with "Start".
def send_start():
    connection.send("start")


#Infinite asyncio loop that looks for movement from movement sensor
    #when it does it runs the Send function. 
async def sensor_listener(poll_ms=50, debounce_ms=500):
    last = 0
    while True:
        status = motion_sensor_in.value()
        motion_sensor_out.value(status)

        #if it detects the movement here it sends the "start" message to the pi
        if status == 1 and last == 0:
            send_start()
            #debounce
            await asyncio.sleep_ms(debounce_ms)

        last = status
        await asyncio.sleep_ms(poll_ms)

async def main():
    asyncio.create_task(connection.listen()) #listens for messages directly 
    asyncio.create_task(sensor_listener())
    while True:
        await asyncio.sleep(1)

asyncio.run(main())