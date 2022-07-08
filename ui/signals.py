from typing import Type, TypeVar, Callable
from PyQt5.QtCore import pyqtBoundSignal, QObject


__ObjType = TypeVar("__ObjType")
__FuncType = TypeVar("__FuncType")


def signalhandler(name: str) -> Callable:
    def wrap(func: __FuncType) -> __FuncType:
        func.__signal_name = name
        return func
    return wrap


def map_signals(target: QObject, interface: Type[__ObjType]) -> __ObjType:
    cls = type(target).__name__
    interface = interface()

    for k in dir(interface):
        item = getattr(interface, k)
        if not callable(item):
            continue
        if not hasattr(item, '__signal_name'):
            continue

        # noinspection PyUnresolvedReferences
        signal_name = item.__signal_name
        if not hasattr(target, signal_name):
            raise AttributeError(f"Target object '{cls}' has no attribute: {signal_name}")

        signal = getattr(target, signal_name)
        if type(signal) is not pyqtBoundSignal:
            raise TypeError(f"The attribute '{signal_name}' of '{cls}' is not a QT signal")

        def emitter(sig):
            return lambda *args: sig.emit(*args)

        setattr(interface, k, emitter(signal))

    return interface


def connect_signals(target: QObject):
    attrs = dir(target)
    signals = {}
    slots = {}

    for k in attrs:
        item = getattr(target, k)
        if type(item) is pyqtBoundSignal:
            signals[k] = item
            continue

        if not callable(item):
            continue
        if not hasattr(item, '__signal_name'):
            continue

        # noinspection PyUnresolvedReferences
        signal_name = item.__signal_name
        slots[signal_name] = item

    for name in signals:
        if name in slots:
            signals[name].connect(slots[name])
