from pathlib import Path
from typing import Dict, List


class DeviceClass(object):
    def __init__(self) -> None:
        self._position = 0.0
        self._enabled = True

    def add(self, value: float) -> float:
        self._position += value
        return self._position

    def move(
        self,
        position: float,
        speed: float = 1.0,
        wait: bool = True,
    ) -> bool:
        self._position = position
        return wait

    def get_samples(self) -> List[float]:
        return [1.0, 2.0, 3.0]

    def get_data(self) -> bytes:
        text = "position={0}\\nenabled={1}\\n".format(
            self._position,
            self._enabled,
        )
        return text.encode("utf-8")

    def configure(self, name: str, value: float) -> Dict[str, float]:
        return {name: value}

    def save(self, path: str) -> str:
        Path(path).write_bytes(self.get_data())
        return path

    def reset(self) -> None:
        self._position = 0.0

    @property
    def position(self) -> float:
        return self._position

    @position.setter
    def position(self, value: float) -> None:
        self._position = value

    @property
    def enabled(self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        self._enabled = value


def run_example(device: object, output_path: str) -> None:
    print("position:", device.position)
    print("enabled:", device.enabled)
    print("add:", device.add(2.5))
    print("move:", device.move(12.5, speed=3.0, wait=False))
    print("position:", device.position)
    device.position = 20.0
    print("position:", device.position)
    print("samples:", device.get_samples())
    print("configure:", device.configure("axis-x", 6.0))
    print("save:", device.save(output_path))
    device.reset()
    print("position:", device.position)


if __name__ == "__main__":
    run_example(DeviceClass(), "device_output.txt")
