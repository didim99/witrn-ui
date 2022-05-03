import sys
import time
from datetime import timedelta
from driver import USBMeter
from protocol import KnownDevice, HIDPacket, Command


last_packet = 0
millis = 0


def on_packet(packet: HIDPacket):
    if packet.payload.command != Command.DAT_RECV:
        return

    global last_packet, millis
    delta = int(round((time.time() - last_packet) * 1000.0))
    last_packet = time.time()
    millis += delta
    if millis > 1000:
        millis = 0

    data = packet.payload.data
    run_time = str(timedelta(seconds=data.runTime))
    sys.stdout.write("\r{:>8s}.{:03.0f} | V: {:6.3f} A: {:6.3f} D+: {:6.3f} D-: {:6.3f}"
                     .format(run_time, millis, data.voltage, data.current, data.dp, data.dn))
    sys.stdout.flush()


def start():
    input("Connect your device and press Enter")

    meter = USBMeter(KnownDevice.A2)
    meter.recv_callback(on_packet)
    meter.connect()

    print("Press Enter to stop reading")
    time.sleep(3)

    meter.start_read()
    global last_packet
    last_packet = time.time()
    input()
    meter.stop_read()
    time.sleep(0.5)
    print("\nGood bye!")


if __name__ == '__main__':
    start()
