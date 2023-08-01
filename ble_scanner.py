from multiprocessing import Process
from config import Config
import asyncio
from bleak import BleakScanner
from ble_uuid import BLE_UUID

class BleScanner(Process):
    def __init__(self, rssi_val):
        Process.__init__(self)
        self.scanner = BleakScanner(scanning_mode="passive")
        self.scanner.register_detection_callback(self.scan_cb)
        self.rssi_v = rssi_val

    def scan_cb(self, device, advertisement_data):
        if device.address in self.rssi_v.keys():
            self.rssi_v[device.address] = device.rssi
        else:
            for uuid in device.metadata["uuids"]:
                if BLE_UUID(uuid) in [k for k in self.rssi_v.keys() if type(k) == BLE_UUID]:
                    self.rssi_v[BLE_UUID(uuid)] = device.rssi
                    break

    def run(self):
        asyncio.run(self.scan())
        
    async def scan(self):
        await self.scanner.start()
        while(True):
            await asyncio.sleep(10)
        # await scanner.stop()