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


class Command:
    DAT_RECV = 0x1a     # Data packet received


class MetaData(metaclass=Binary):
    size = 52           # Offset     Size         Description
    offPer = Byte       # 0x00 (0)   1  (int8)    Unknown data
    offHour = Byte      # 0x01 (1)   1  (int8)    Unknown data
    recmA = Word        # 0x02 (2)   2  (uint16)  Minimal recorded current
    ah = Float          # 0x04 (4)   4  (float)   Accumulated capacity (Ah)
    wh = Float          # 0x08 (8)   4  (float)   Accumulated energy (Wh)
    recTime = Dword     # 0x0c (12)  4  (uint32)  Time since record start (sec)
    runTime = Dword     # 0x10 (16)  4  (uint32)  Time since boot (sec)
    dp = Float          # 0x14 (20)  4  (float)   USB D+ voltage (V)
    dn = Float          # 0x18 (24)  4  (float)   USB D- voltage (V)
    tempIn = Float      # 0x1c (28)  4  (float)   Inner temperature (degC)
    tempOut = Float     # 0x20 (32)  4  (float)   External temperature (degC)
    voltage = Float     # 0x24 (36)  4  (float)   USB V_BUS voltage (V)
    current = Float     # 0x28 (40)  4  (float)   USB V_BUS current (A)
    recGrp = Byte       # 0x2c (44)  1  (int8)    Current recording group num
    reserved = Byte[7]  # 0x3d (45)  7  (???)     Reserved bytes, unknown data


class Payload(metaclass=Binary):
    size = 55           # Offset     Size         Description
    command = Byte      # 0x00 (0)   1  (int8)    Command number
    length = Byte       # 0x01 (1)   1  (int8)    Data length (always zero?)
    data = Byte[52]     # 0x02 (2)   52 (struct)  MetaData structure
    verify = Byte       # 0x02 (54)  1  (int8)    Checksum byte


class Packet(metaclass=Binary):
    size = 64           # Offset     Size         Description
    start = Byte        # 0x00 (0)   1  (int8)    Packet start byte
    head = Byte         # 0x01 (1)   1  (int8)    Packet header byte
    idx1 = Byte         # 0x02 (2)   1  (int8)    Unknown data
    idx2 = Byte         # 0x03 (3)   1  (int8)    Unknown data
    needAck = Byte      # 0x04 (4)   1  (int8)    ACK request flag
    free = Byte[3]      # 0x05 (5)   3  (???)     Unknown data
    payload = Byte[55]  # 0x08 (8)   55 (struct)  Payload structure
    verify = Byte       # 0x3f (63)  1  (int8)    Checksum byte


def parse_packet(data) -> MetaData:
    _, packet = Packet.from_binary(data)
    _, payload = Payload.from_binary(bytes(packet['payload']))
    _, data = MetaData.from_binary(bytes(payload['data']))
    return data
