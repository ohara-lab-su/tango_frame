from pathlib import Path
import sys


SRC_DIR = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(SRC_DIR))

from device.device_class import run_example
from device.server_tango.device_client import DeviceClient


DEVICE_URL = "tango://127.0.0.1:10000/test/tango/device#dbase=no"


if __name__ == "__main__":
    device = DeviceClient(DEVICE_URL)
    print("ping:", device._transport.ping())
    run_example(device, "client_output.txt")
