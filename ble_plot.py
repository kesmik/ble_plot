from multiprocessing import Queue, Manager, freeze_support
from ble_scanner import BleScanner
from csv_writer import CSVWriter
from ble_plotter import Plotter
from config import Config
from ble_uuid import BLE_UUID

from time import sleep
import sys, os, signal

def os_clear_console():
    os.system('cls' if os.name in ('nt', 'dos') else 'clear')

def handle_process_err(p_key, p_dict):
    p_dict[p_key].join()
    del p_dict[p_key]
    terminate_processes(p_dict)
    sys.exit(1)

def terminate_processes(p_dict):
    print('Terminating all processes')
    for key in p_dict.keys():
        p_dict[key].terminate()

if __name__ == "__main__":
    freeze_support()
    processes = {}
    def exit_handler(*args, **kwargs):
        os_clear_console()
        terminate_processes(processes)
        exit(0)

    signal.signal(signal.SIGINT, exit_handler)
    q = Queue()
    filters = Config().get_settings()['BLE_FILTERS']
    rssi_vals = Manager().dict({
        **{k:0 for k, v in filters['MAC'].items()},
        **{BLE_UUID(k):0 for k, v in filters['UUID'].items()}
        })
    processes['BLE SCANNER'] = BleScanner(rssi_vals)
    processes['CSV_WRITER'] = CSVWriter(q)
    processes['PLOTTER'] = Plotter(q, rssi_vals)
    for p in processes.keys():
        processes[p].start()

    while len(processes) > 0:
        for key in list(processes):
            p = processes[key]
            if p.exitcode is None and not p.is_alive():
                 print(f'{key} is gone as if never born!')
                 handle_process_err(key, processes)
            elif p.exitcode is not None:
                print (f'{key} finished with exit code: {p.exitcode}')
                handle_process_err(key, processes)
            else:
                print(f'{key} is running')
        sleep(0.5)