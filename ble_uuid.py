from uuid import UUID

class BLE_UUID(UUID):
    def __init__(self, hex) -> None:
        try:
            if len(bytes.fromhex(hex)) == 2:
                hex = f"0000{hex}-0000-1000-8000-00805f9b34fb"
            elif len(bytes.fromhex(hex)) == 4:
                hex = f"{hex}-0000-1000-8000-00805f9b34fb"
        except ValueError:
            pass

        super().__init__(hex)