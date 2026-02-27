import asyncio
from bleak import BleakClient, BleakScanner

UART_WRITE_UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E" # Pi Writes to this
UART_NOTIFY_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E" # Pi Reads/Notifies from this

class PiConnection:
    def __init__(self):
        self.items_to_send = []
        self.attachments = []
        self.client = None

    def send(self, value: str):
        self.items_to_send.append(value)

    def attach(self, value: str, function):
        self.attachments.append((value, function))

    async def notification_handler(self, sender, data):
        received_string = data.decode('utf-8').strip()
        print(f"Received from ESP: {received_string}")
        for string, function in self.attachments:
            if string == received_string:
                if asyncio.iscoroutinefunction(function):
                    await function()
                else:
                    function()

    async def running(self):
        print("Scanning for ESP32_BLE...")
        device = await BleakScanner.find_device_by_name("ESP32_BLE")
        
        while not device:
            print("ESP32 not found. Make sure it is powered on and advertising.")
            await asyncio.sleep(2.5)
            print("Searching again...")
            device = await BleakScanner.find_device_by_name("ESP32_BLE")
        
        print(f"Found ESP32: {device.address}. Connecting...")

        async with BleakClient(device) as client:
            self.client = client
            await client.start_notify(UART_NOTIFY_UUID, self.notification_handler)
            print("Connected and listening for notifications.")

            while True:
                if len(self.items_to_send) > 0:
                    item = self.items_to_send.pop(0)
                    try:
                        await client.write_gatt_char(UART_WRITE_UUID, item.encode('utf-8'))
                        print(f"Sent to ESP: {item}")
                    except Exception as e:
                        print(f"Failed to send {item}: {e}")
                        self.items_to_send.insert(0, item)
                        await asyncio.sleep(1)
                else:
                    await asyncio.sleep(0.1)

    async def start(self):
        await self.running()
