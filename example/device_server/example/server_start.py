from pathlib import Path
import sys


SRC_DIR = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(SRC_DIR))

from tango_frame import run_device_server
from device.server_tango.tango_ds import TangoDevice


SERVER_INSTANCE = "example"
DEVICE_NAME = "test/tango/device"
HOST = "127.0.0.1"
PORT = 10000


if __name__ == "__main__":
    run_device_server(
        TangoDevice,
        args=[
            "TangoDevice",
            SERVER_INSTANCE,
            "-nodb",
            "-dlist",
            DEVICE_NAME,
            "-ORBendPoint",
            "giop:tcp:{0}:{1}".format(HOST, PORT),
        ],
    )
