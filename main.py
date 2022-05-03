import sys
import time
from datetime import timedelta
from driver import USBMeter
from protocol import KnownDevice, HIDPacket, Command


class Main:
    millis: int
    packet_cnt: int
    time_start: float
    last_packet: float

    running: bool

    def on_packet(self, packet: HIDPacket) -> None:
        if not self.running:
            return
        if packet.payload.command != Command.DAT_RECV:
            return

        now = time.time()
        total = (now - self.time_start) * 1000.0
        delta = int(round((now - self.last_packet) * 1000.0))
        self.last_packet = time.time()
        self.millis += delta
        if self.millis > 999:
            self.millis = 0

        self.packet_cnt += 1
        data = packet.payload.data
        run_time = str(timedelta(seconds=data.runTime))
        total = str(timedelta(milliseconds=total))[:-3]
        sys.stdout.write(
            "\r{:>8d} | {:>12s} | {:>8s}.{:03.0f} | {:6.3f} {:6.3f} | {:6.3f} {:6.3f}"
            .format(self.packet_cnt, total, run_time, self.millis,
                    data.voltage, data.current, data.dp, data.dn))
        sys.stdout.flush()

    def on_error(self, error: Exception) -> None:
        print("\nError: " + str(error))
        self.running = False
        exit()

    def start(self) -> None:
        input("Connect your device and press Enter")

        try:
            meter = USBMeter(KnownDevice.A2)
            meter.recv_callback(self.on_packet)
            meter.error_callback(self.on_error)
            meter.connect()
        except Exception as e:
            print("Failed to connect: " + str(e))
            return

        print("Press Enter to stop reading\n")
        time.sleep(1)

        print("{:>8s} | {:>12s} | {:>12s} | {:>6s} {:>6s} | {:>6s} {:>6s}"
              .format('packets', 'rectime', 'uptime', 'V', 'A', 'D+', 'D-'))

        self.running = True
        meter.start_read()
        self.last_packet = time.time()
        self.time_start = time.time()
        self.packet_cnt = 0
        self.millis = 0

        input()
        self.running = False
        meter.stop_read()
        time.sleep(0.5)
        print("\nGood bye!")


if __name__ == '__main__':
    Main().start()
