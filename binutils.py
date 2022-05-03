# Original code by Daniel Brodie, modified by didim99
# See: https://code.activestate.com/recipes/576666/

import struct


def hexify(data, sep=' '):
    return sep.join([format(x, '02x') for x in data])


def preargs(cls):
    def _pre_init(*args1, **kwargs1):
        def _my_init(*args2, **kwargs2):
            args = args1 + args2
            kwargs1.update(kwargs2)
            return cls(*args, **kwargs1)
        return _my_init
    return _pre_init


class BinaryMetaType(type):
    def __getitem__(self, val):
        return Array(self, val)


class BinaryType(metaclass=BinaryMetaType):
    def __init__(self, **kwargs):
        self._kwargs = kwargs

    def to_binary(self, val):
        pass

    def from_binary(self, binary):
        pass


class SimpleBinaryType(BinaryType):
    def __init__(self, fmt, **kwargs):
        super().__init__(**kwargs)
        self._struct = struct.Struct(fmt)

    def to_binary(self, val):
        return self._struct.pack(val)

    def from_binary(self, binary):
        return (self._struct.size,
                self._struct.unpack(binary[:self._struct.size])[0])


@preargs
class Array(BinaryType):
    def __init__(self, arr_type, arr_len, **kwargs):
        super().__init__(**kwargs)
        self._arr_type, self._arr_len = arr_type(**kwargs), arr_len

    def to_binary(self, val):
        res = []
        for i, v in enumerate(val):
            res.append(self._arr_type.to_binary(v))
            if i+1 == self._arr_len:
                break
        return b''.join(res)

    def from_binary(self, binary):
        res = []
        ssum = 0
        for i in range(self._arr_len):
            s, v = self._arr_type.from_binary(binary[ssum:])
            ssum += s
            res.append(v)
        return ssum, res


class Byte(SimpleBinaryType):
    def __init__(self, **kwargs):
        super().__init__('B', **kwargs)


class Word(SimpleBinaryType):
    def __init__(self, **kwargs):
        super().__init__('H', **kwargs)


class Dword(SimpleBinaryType):
    def __init__(self, **kwargs):
        super().__init__('I', **kwargs)


class Float(SimpleBinaryType):
    def __init__(self, **kwargs):
        super().__init__('f', **kwargs)


class BinaryBuilder(dict):
    def __init__(self, **kwargs):
        super().__init__()
        self.members = []
        self._kwargs = kwargs

    def __setitem__(self, key, value):
        if key.startswith('__'):
            return
        if not callable(value):
            return
        if key not in self:
            self.members.append((key, value(**self._kwargs)))
        super().__setitem__(key, value)


class Binary(type):
    @classmethod
    def __prepare__(mcs, cls, bases, **kwargs):
        # In the future kwargs can contain things such as endianity
        # and alignment
        return BinaryBuilder(**kwargs)

    def __new__(mcs, name, bases, class_dict):
        # There are nicer ways of doing this, but as a hack it works
        def fixupdict(d):
            @classmethod
            def to_binary(clas, datadict):
                res = []
                for k, v in clas.members:
                    res.append(v.to_binary(datadict[k]))
                return b''.join(res)

            @classmethod
            def from_binary(cls, bytes_in):
                res = {}
                ssum = 0
                for k, v in cls.members:
                    i, _d = v.from_binary(bytes_in[ssum:])
                    ssum += i
                    res[k] = _d
                return ssum, res

            nd = {'to_binary': to_binary,
                  'from_binary': from_binary,
                  'members': d.members}
            return nd

        return super().__new__(mcs, name, bases, fixupdict(class_dict))
