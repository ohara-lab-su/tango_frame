from typing import Dict, List


class TestDevice:
    def __init__(self) -> None:
        self._position = 0.0
        self._enabled = True
        self._samples = [1.0, 2.0, 3.0]

    def add(self, value: float) -> float:
        self._position += value
        return self._position

    def move(self, position: float, speed: float = 1.0, wait: bool = True) -> bool:
        self._position = position
        return wait

    def get_name(self) -> str:
        return "test-device"

    def get_samples(self) -> List[float]:
        return list(self._samples)

    def configure(self, name: str, values: List[float]) -> Dict[str, float]:
        return {name: sum(values)}

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

    @property
    def samples(self) -> List[float]:
        return list(self._samples)


if __name__ == "__main__":
    device = TestDevice()

    print("name:", device.get_name())
    print("position:", device.position)
    print("enabled:", device.enabled)
    print("samples:", device.samples)

    print("add:", device.add(2.5))
    print("position:", device.position)

    print("move:", device.move(12.5, speed=3.0, wait=False))
    print("position:", device.position)

    device.position = 20.0
    print("position:", device.position)

    print("get_samples:", device.get_samples())
    print("configure:", device.configure("axis-x", [1.0, 2.0, 3.0]))

    device.reset()
    print("position:", device.position)
