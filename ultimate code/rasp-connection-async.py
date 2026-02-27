# rasp_connection_async.py
import bluetooth
import micropython
import uasyncio as asyncio
from micropython import const

_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)

MOVEMENT_SERVICE_UUID = bluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
UART_WRITE_UUID = bluetooth.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E")   # Central writes here
UART_NOTIFY_UUID = bluetooth.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E")  # Central receives notify here


class _BLEUART:
    def __init__(self, name="ESP32_BLE"):
        self.ble = bluetooth.BLE()
        self.ble.active(True)
        self.ble.irq(self._irq)

        self.conn_handle = None
        self.name = name

        self.attachments = []  # (string, function)
        self._rx_queue = asyncio.Queue(16)
        self._rx_pending = []
        self._sched_armed = False

        services = (
            (MOVEMENT_SERVICE_UUID, (
                (UART_WRITE_UUID, bluetooth.FLAG_WRITE),
                (UART_NOTIFY_UUID, bluetooth.FLAG_NOTIFY),
            )),
        )
        ((self.write_handle, self.notify_handle),) = self.ble.gatts_register_services(services)
        self._advertise(self.name)

    def _irq(self, event, data):
        if event == _IRQ_CENTRAL_CONNECT:
            self.conn_handle, _, _ = data
            return

        if event == _IRQ_CENTRAL_DISCONNECT:
            self.conn_handle = None
            self._advertise(self.name)
            return

        if event == _IRQ_GATTS_WRITE:
            conn_handle, value_handle = data
            if value_handle != self.write_handle:
                return

            b = self.ble.gatts_read(self.write_handle)  # bytes
            self._rx_pending.append(b)

            if not self._sched_armed:
                self._sched_armed = True
                micropython.schedule(self._drain_rx_to_queue, 0)

    def _drain_rx_to_queue(self, _):
        self._sched_armed = False
        while self._rx_pending:
            b = self._rx_pending.pop(0)
            try:
                self._rx_queue.put_nowait(b)
            except:
                pass

        if self._rx_pending:
            self._sched_armed = True
            micropython.schedule(self._drain_rx_to_queue, 0)

    def send(self, data: str):
        if self.conn_handle is None:
            return
        self.ble.gatts_notify(self.conn_handle, self.notify_handle, data.encode("utf-8"))

    def attach(self, string: str, function):
        self.attachments.append((string, function))

    async def listen(self):
        while True:
            b = await self._rx_queue.get()
            s = b.decode("utf-8").strip()

            for compare_string, fn in self.attachments:
                if s == compare_string:
                    res = fn()
                    if hasattr(res, "__await__"):
                        await res

    def _advertise(self, name):
        name_b = name.encode("utf-8")
        payload = bytearray((len(name_b) + 1, 0x09)) + name_b
        self.ble.gap_advertise(100_000, adv_data=payload)


class Connector:
    def __init__(self, name="ESP32_BLE"):
        self.ble = _BLEUART(name=name)

    def attach(self, string: str, function):
        self.ble.attach(string, function)

    def send(self, string: str):
        self.ble.send(string)

    async def listen(self):
        await self.ble.listen()