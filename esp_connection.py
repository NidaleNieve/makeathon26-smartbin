# Main Module meant for communication with our ESP

import time
import asyncio
from bleak import BleakClient, BleakScanner

# Same Nordic UART Service UUIDs
UART_WRITE_UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E" # Pi Writes to this
UART_NOTIFY_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E" # Pi Reads/Notifies from this

class Connection:
    items_to_send = ["active"]
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
        # Start listening for incoming packets from the ESP32
        await client.start_notify(UART_NOTIFY_UUID, notification_handler)

        # 2. THE SENDER FUNCTION
        while True:
            # Get the item from the list
            if len(Connection.items_to_send) > 0:
                item = Connection.items_to_send.pop(0)
                
                # Write the string to the ESP32
                try:
                    await client.write_gatt_char(UART_WRITE_UUID, item.encode('utf-8'))
                except:
                    # if it failed to send we place it back in the queue where we took it.
                    Connection.items_to_send.insert(0, item)


async def start():
    asyncio.create_task(running())

