from threading import Thread, Event
from typing import Callable
import usb.core
import usb.util
from usb.core import USBError, Device as USBDevice
from protocol import DeviceInfo, KnownDevice, HIDPacket


class USBMeter:
    _info: DeviceInfo
    _device: USBDevice

    _running: Event
    _recv_thread: Thread
    _recv_cb: Callable
    _error_cb: Callable

    def __init__(self, _info: KnownDevice):
        self._info = _info.value
        self._running = Event()

    def recv_callback(self, callback: Callable):
        self._recv_cb = callback

    def error_callback(self, callback: Callable):
        self._error_cb = callback

    def connect(self):
        self._device = usb.core.find(idVendor=self._info.idVendor,
                                     idProduct=self._info.idProduct)
        if self._device is None:
            raise IOError(f"Device {self._info} not found!")

        if self._device.is_kernel_driver_active(0):
            try:
                self._device.detach_kernel_driver(0)
                print("Kernel driver detached")
            except USBError as e:
                raise IOError("Could not detach kernel driver") from e
        else:
            print("No kernel driver attached")
        try:
            usb.util.claim_interface(self._device, 0)
            print("Claimed device")
        except USBError as e:
            raise IOError("Could not claim the device") from e
        try:
            self._device.reset()
        except usb.core.USBError as e:
            raise IOError("Could not set configuration") from e

    def start_read(self):
        self._running.set()
        name = self._info.devName + " reader thread"
        self._recv_thread = Thread(name=name, target=self._reader_loop)
        self._recv_thread.start()

    def stop_read(self):
        self._running.clear()

    def _reader_loop(self):
        while self._running.is_set():
            try:
                data = self._device.read(self._info.endpoint, 64)
                if not data:
                    continue

                data = HIDPacket(data)
                if self._recv_cb is not None:
                    self._recv_cb(data)
            except USBError as e:
                self._running.clear()
                if self._error_cb is not None:
                    self._error_cb(e)
                break
