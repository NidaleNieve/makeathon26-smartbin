# Main Module meant for communication with our ESP

#class Controller
import time
import asyncio
from bleak import BleakClient, BleakScanner

# Same Nordic UART Service UUIDs
UART_WRITE_UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E" # Pi Writes to this
UART_NOTIFY_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E" # Pi Reads/Notifies from this

class Connection:
    items_to_send = []
    attachments = []

    def __init__(self):
        pass

    def send(self, value: str):
        Connection.items_to_send.append(value)

    def attach(self, value: str, function):
        Connection.attachments.append((value, function))


# 1. THE LISTENER FUNCTION
# This triggers automatically whenever the ESP32 sends a packet back
async def notification_handler(sender, data):
    received_string = data.decode('utf-8')
    for string, function in Connection.attachments:
        if string == received_string:
            function()

async def running():
    
    print("Scanning for ESP32_BLE...")
    # Find the ESP32 by the name we gave it

    device = await BleakScanner.find_device_by_name("ESP32_BLE")
    # Make sure we get device.
    while True:
        if not device:
            print("ESP32 not found. Make sure it is powered on and advertising.")
            time.sleep(2.5)
            print("Searching again...")
            device = await BleakScanner.find_device_by_name("ESP32_BLE")
        else:
            break
    
    print(f"Found ESP32: {device.address}. Connecting...")

    
    async with BleakClient(device) as client:
        await client.start_notify(UART_NOTIFY_UUID, notification_handler)




    
        
        # Start listening for incoming packets from the ESP32
        

        # 2. THE SENDER FUNCTION
        # A list of basic strings to send
        commands_to_send = ["left", "right", "up", "down", "none"]
        
        for item in Connection.items_to_send:
            # Write the string to the ESP32
            
            await client.write_gatt_char(UART_WRITE_UUID, item.encode('utf-8'))
            # Wait 3 seconds before sending the next one 
            # (Allows time for the ESP to receive, process, and reply)
            await asyncio.sleep(3)

            ### print("Finished sending all commands. Listening for 5 more seconds...")
            ### await asyncio.sleep(5)
            
            # Stop listening before disconnecting
            ### await client.stop_notify(UART_NOTIFY_UUID)

async def start():
    # Run the async loop
    asyncio.create_task(running())
    #asyncio.create_task(running)

# 34:85:18:A6:43:BA ESP MAC