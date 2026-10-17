from tango_frame import create_device_server_class, run_device_server
from test_device import TestDevice

SERVER_NAME = "TangoFrameTestServer"
INSTANCE_NAME = "test"
DEVICE_NAME = "test/tango_frame/device"
HOST = "127.0.0.1"
PORT = 10000

TangoTestDevice = create_device_server_class(TestDevice)


if __name__ == "__main__":
    run_device_server(
        device_class=TangoTestDevice,
        server_name=SERVER_NAME,
        instance_name=INSTANCE_NAME,
        extra_args=[
            "-ORBendPoint",
            "giop:tcp:" + HOST + ":" + str(PORT),
            "-nodb",
            "-dlist",
            DEVICE_NAME,
        ],
    )
