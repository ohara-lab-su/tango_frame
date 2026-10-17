from pathlib import Path

from tango_frame import AutoDispatchClient

from device.device_class import DeviceClass


class DeviceClient(AutoDispatchClient):
    device_class = DeviceClass

    def save(self, path: str) -> str:
        data = self.get_data()
        Path(path).write_bytes(data)
        return path
