from threading import Thread, Event
from typing import Callable
import usb.core
import usb.util
from usb.core import Device, USBError
from protocol import *


class USBMeter:
    _info: DeviceInfo
    _device: Device

    _running: Event
    _recv_thread: Thread
    _recv_cb: Callable

    def __init__(self, _info: KnownDevice):
        self._info = _info.value
        self._running = Event()

    def recv_callback(self, callback: Callable):
        self._recv_cb = callback

    def connect(self):
        self._device = usb.core.find(idVendor=self._info.idVendor,
                                     idProduct=self._info.idProduct)
        if self._device.is_kernel_driver_active(0):
            try:
                self._device.detach_kernel_driver(0)
                print("kernel driver detached")
            except USBError as e:
                exit("Could not detach kernel driver: %s" % str(e))
        else:
            print("no kernel driver attached")
        try:
            usb.util.claim_interface(self._device, 0)
            print("claimed device")
        except USBError as e:
            exit("Could not claim the device: %s" % str(e))
        try:
            self._device.reset()
        except usb.core.USBError as e:
            exit("Could not set configuration: %s" % str(e))

    def start_read(self):
        self._running.set()
        name = self._info.devName + " reader thread"
        self._recv_thread = Thread(name=name, target=self._reader_loop)
        self._recv_thread.start()

    def stop_read(self):
        self._running.clear()

    def _reader_loop(self):
        while self._running.is_set():
            data = self._device.read(self._info.endpoint, 64)
            if not data:
                continue

            data = parse_packet(data)
            if self._recv_cb is not None:
                self._recv_cb(data)
