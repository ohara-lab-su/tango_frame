from tango_frame import TangoClient

DEVICE_URL = "tango://127.0.0.1:10000/test/tango_frame/device#dbase=no"


if __name__ == "__main__":
    device = TangoClient(DEVICE_URL)

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
