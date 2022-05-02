from enum import Enum
from binutils import *


class DeviceInfo:
    devName: str
    idVendor: int
    idProduct: int
    endpoint: int

    def __init__(self, name, vid, pid, ep):
        self.devName = name
        self.idVendor = vid
        self.idProduct = pid
        self.endpoint = ep


class KnownDevice(Enum):
    A2 = DeviceInfo(name='A2', vid=0x0716, pid=0x5045, ep=0x81)
    A2L = DeviceInfo(name='A2L', vid=0x0716, pid=0x5050, ep=0x81)
    U3 = DeviceInfo(name='U3', vid=0x0716, pid=0x5044, ep=0x81)


class MetaData(metaclass=Binary):
    size = 52           # total size
    offPer = Byte       # offset:0x00 (0)  size:1  (int8)
    offHour = Byte      # offset:0x01 (1)  size:1  (int8)
    recmA = Word        # offset:0x02 (2)  size:2  (uint16)
    ah = Float          # offset:0x04 (4)  size:4  (float)
    wh = Float          # offset:0x08 (8)  size:4  (float)
    recTime = Dword     # offset:0x0c (12) size:4  (uint32)
    runTime = Dword     # offset:0x10 (16) size:4  (uint32)
    dp = Float          # offset:0x14 (20) size:4  (float)
    dn = Float          # offset:0x18 (24) size:4  (float)
    tempIn = Float      # offset:0x1c (28) size:4  (float)
    tempOut = Float     # offset:0x20 (32) size:4  (float)
    voltage = Float     # offset:0x24 (36) size:4  (float)
    current = Float     # offset:0x28 (40) size:4  (float)
    recGrp = Byte       # offset:0x2c (44) size:1  (int8)
    reserved = Byte[7]  # offset:0x3d (45) size:7  (unknown)


class Payload(metaclass=Binary):
    size = 55           # total size
    command = Byte      # offset:0x00 (0)  size:1  (int8)
    length = Byte       # offset:0x01 (1)  size:1  (int8)
    data = Byte[52]     # offset:0x02 (2)  size:52 (MetaData)
    verify = Byte       # offset:0x02 (54) size:1  (int8)


class Packet(metaclass=Binary):
    size = 64           # total size
    start = Byte        # offset:0x00 (0)  size:1  (int8)
    head = Byte         # offset:0x01 (1)  size:1  (int8)
    idx1 = Byte         # offset:0x02 (2)  size:1  (int8)
    idx2 = Byte         # offset:0x03 (3)  size:1  (int8)
    needAck = Byte      # offset:0x04 (4)  size:1  (int8)
    free = Byte[3]      # offset:0x05 (5)  size:3  (unknown)
    payload = Byte[55]  # offset:0x08 (8)  size:55 (Payload)
    verify = Byte       # offset:0x00 (0)  size:1  (int8)


def parse_packet(data) -> MetaData:
    _, packet = Packet.from_binary(data)
    _, payload = Payload.from_binary(bytes(packet['payload']))
    _, data = MetaData.from_binary(bytes(payload['data']))
    return data
