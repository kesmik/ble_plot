import csv
from multiprocessing import Process
from config import Config
from ble_uuid import BLE_UUID
import os

class CSVWriter(Process):
    def __init__(self, queue) -> None:
        Process.__init__(self)
        config = Config().get_settings()['csv']
        self.queue = queue
        self.fname = os.path.join(config['dir'], config['fname'])
        
        if not os.path.exists(config['dir']):
            os.makedirs(config['dir'])

        with open(self.fname, 'w', newline='', encoding="utf-8") as f:
            filters = Config().get_settings()['BLE_FILTERS']
            devices = {
                **filters['MAC'],
                **{BLE_UUID(k):v for k, v in filters['UUID'].items()}
                }
            header = ["t"] + [devices[n] for n in devices.keys()]
            csv_w = csv.writer(f)
            csv_w.writerow(header)
    
    def run(self):
        while(True):
            data = self.queue.get()
            with open(self.fname, 'a', newline='', encoding="utf-8") as f:
                csv_w = csv.writer(f)
                csv_w.writerow(data)
