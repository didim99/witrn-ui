import time
from datetime import timedelta
from driver import USBMeter
from protocol import KnownDevice, MetaData


def on_packet(data: MetaData):
    data['runTime'] = str(timedelta(seconds=data['runTime']))
    print("{:>8s} | V: {:6.3f} A: {:6.3f}".format(
        data['runTime'], data['voltage'], data['current']))


def start():
    meter = USBMeter(KnownDevice.A2)
    meter.recv_callback(on_packet)
    meter.connect()
    print("Press Enter to stop reading")
    time.sleep(3)

    meter.start_read()
    input()
    meter.stop_read()


if __name__ == '__main__':
    start()
