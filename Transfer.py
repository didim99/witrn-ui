import time
from datetime import timedelta
from driver import USBMeter
from protocol import KnownDevice, HIDPacket, Command
from PyQt5.QtCore import QThread, pyqtSignal


class Data(QThread):
    voltSG = pyqtSignal(str, str, float, float, float, float, float, float, float, float)

    def __init__(self, mainwind):
        super().__init__()
        QThread.__init__(self)
        self.Mainwi = mainwind

    millis: int
    packet_cnt: int
    time_start: float
    last_packet: float
    running: bool
    voltage: float
    current: float
    dp: float
    dn: float


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
        self.voltage = data.voltage
        self.voltSG.emit(total, run_time, data.voltage, data.current, data.dp, data.dn, data.wh, data.ah, data.tempOut, data.tempIn)



    def on_error(self, error: Exception) -> None:
        print("\nError: " + str(error))

    def runA2(self):
        meter = USBMeter(KnownDevice.A2)
        meter.recv_callback(self.on_packet)
        meter.error_callback(self.on_error)
        meter.connect()
        time.sleep(1)  # Without this delay, an error is output.
        self.running = True
        meter.start_read()
        self.last_packet = time.time()
        self.time_start = time.time()
        self.packet_cnt = 0
        self.millis = 0

    def runU3(self):
        meter = USBMeter(KnownDevice.U3)
        meter.recv_callback(self.on_packet)
        meter.error_callback(self.on_error)
        meter.connect()
        time.sleep(1)  # Without this delay, an error is output.
        self.running = True
        meter.start_read()
        self.last_packet = time.time()
        self.time_start = time.time()
        self.packet_cnt = 0
        self.millis = 0

    def runA2L(self):
        meter = USBMeter(KnownDevice.A2L)
        meter.recv_callback(self.on_packet)
        meter.error_callback(self.on_error)
        meter.connect()
        time.sleep(1)  # Without this delay, an error is output.
        self.running = True
        meter.start_read()
        self.last_packet = time.time()
        self.time_start = time.time()
        self.packet_cnt = 0
        self.millis = 0


if __name__ == '__main__':
    Data().run()


