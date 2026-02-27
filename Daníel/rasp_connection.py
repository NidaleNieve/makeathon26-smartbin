import time

import bluetooth

from micropython import const

_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)
_IRQ_GATTS_READ_REQUEST = const(4)
_IRQ_SCAN_RESULT = const(5)
_IRQ_SCAN_DONE = const(6)
_IRQ_PERIPHERAL_CONNECT = const(7)
_IRQ_PERIPHERAL_DISCONNECT = const(8)
_IRQ_GATTC_SERVICE_RESULT = const(9)
_IRQ_GATTC_SERVICE_DONE = const(10)
_IRQ_GATTC_CHARACTERISTIC_RESULT = const(11)
_IRQ_GATTC_CHARACTERISTIC_DONE = const(12)
_IRQ_GATTC_DESCRIPTOR_RESULT = const(13)
_IRQ_GATTC_DESCRIPTOR_DONE = const(14)
_IRQ_GATTC_READ_RESULT = const(15)
_IRQ_GATTC_READ_DONE = const(16)
_IRQ_GATTC_WRITE_DONE = const(17)
_IRQ_GATTC_NOTIFY = const(18)
_IRQ_GATTC_INDICATE = const(19)
_IRQ_GATTS_INDICATE_DONE = const(20)
_IRQ_MTU_EXCHANGED = const(21)
_IRQ_L2CAP_ACCEPT = const(22)
_IRQ_L2CAP_CONNECT = const(23)
_IRQ_L2CAP_DISCONNECT = const(24)
_IRQ_L2CAP_RECV = const(25)
_IRQ_L2CAP_SEND_READY = const(26)
_IRQ_CONNECTION_UPDATE = const(27)
_IRQ_ENCRYPTION_UPDATE = const(28)
_IRQ_GET_SECRET = const(29)
_IRQ_SET_SECRET = const(30)

# Standard Nordic UART Service UUIDs
MOVEMENT_SERVICE_UUID = bluetooth.UUID('6E400001-B5A3-F393-E0A9-E50E24DCCA9E')
UART_WRITE_UUID = bluetooth.UUID('6E400002-B5A3-F393-E0A9-E50E24DCCA9E')  # Pi writes here
UART_NOTIFY_UUID = bluetooth.UUID('6E400003-B5A3-F393-E0A9-E50E24DCCA9E')  # Pi listens here


class _BLEUART:
    def __init__(self, name="ESP32_BLE"):
        self.ble = bluetooth.BLE()
        self.ble.active(True)
        self.ble.irq(self.ble_irq)
        self.conn_handle = None
        self.name = name

        #List of tuples containing a string and function
        #The function will be called when the string is received from the raspberry
        self.attachments = []

        # Register the GATT Server Services
        services = (
            (MOVEMENT_SERVICE_UUID, (
                (UART_WRITE_UUID, bluetooth.FLAG_WRITE),
                (UART_NOTIFY_UUID, bluetooth.FLAG_NOTIFY)
            )),
        )
        ((self.write_handle, self.notify_handle),) = self.ble.gatts_register_services(services)

        # Start Advertising
        self.advertise(self.name)

    def ble_irq(self, event, data):
        if event == _IRQ_CENTRAL_CONNECT:
            self.conn_handle, _, _ = data
            print("Raspberry Pi Connected!")

        elif event == _IRQ_CENTRAL_DISCONNECT:
            print("Raspberry Pi Disconnected. Re-advertising...")
            self.conn_handle = None
            self.advertise("ESP32_BLE")

        elif event == _IRQ_GATTS_WRITE:
            conn_handle, value_handle = data
            if value_handle == self.write_handle:
                # Read the incoming string
                received_bytes = self.ble.gatts_read(self.write_handle)
                received_string = received_bytes.decode('utf-8')

                # Check if the string is something that has an attached function, then run that function
                for compare_string, function in self.attachments:
                    if received_string == compare_string:
                        function()


    def send(self, data: str):
        if self.conn_handle is not None:
            print(f"Sending Data: {data}")
            self.ble.gatts_notify(self.conn_handle, self.notify_handle, data.encode('utf-8'))

    def attach(self, string: str, function):
        self.attachments.append((string, function))

    def advertise(self, name):
        # Create a basic BLE advertising payload with the device name
        name_bytes = bytes(name, 'utf-8')
        payload = bytearray((len(name_bytes) + 1, 0x09)) + name_bytes
        self.ble.gap_advertise(100000, adv_data=payload)
        print(f"Advertising as {name}...")


# Small wrapper to ease use for other parts of the code
class Connector:
    ble_uart = _BLEUART()
    def __init__(self):
        self.ble = Connector.ble_uart
        #Give it some time to run
        time.sleep(1)

    def attach(self, string: str, function):
        self.ble.attach(string, function)

    def send(self, string: str):
        self.ble.send(string)

