#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
Pure Python implementation of Bencode serialization format.
To be used when fast C Extension cannot be compiled.
"""


import sys


if sys.version_info[0] == 2:
    try:
        from cStringIO import StringIO
    except ImportError:
        from StringIO import StringIO
else:
    from io import BytesIO as StringIO


if sys.version_info[0] == 2:
    INTEGER_TYPES = (int, long)
    BINARY_TYPES = (str, )
    int_to_binary = lambda val: str(val)
    binary_return = lambda val: val
else:
    INTEGER_TYPES = (int,)
    BINARY_TYPES = (bytes, str)
    int_to_binary = lambda val: bytes(str(val), 'ascii')
    def binary_return(val):
        try:
            return val.decode("utf")
        except UnicodeDecodeError:
            return val


class BencodeValueError(ValueError):
    pass


class BencodeTypeError(TypeError):
    pass


def _dump_implementation(obj, write, path, cast):
    """ dump()/dumps() implementation """

    t = type(obj)

    if id(obj) in path:
        raise BencodeValueError('circular reference detected')

    if t in INTEGER_TYPES:
        write(b'i')
        write(int_to_binary(obj))
        write(b'e')
    elif t in BINARY_TYPES:
        if t is str and sys.version_info[0] == 3:
            utf_bytes = obj.encode("utf8")
            write(int_to_binary(len(utf_bytes)))
            write(b':')
            write(utf_bytes)
        else:
            write(int_to_binary(len(obj)))
            write(b':')
            write(obj)
    elif t is list or (cast and issubclass(t, (list, tuple))):
        write(b'l')
        for item in obj:
            _dump_implementation(item, write, path + [id(obj)], cast)
        write(b'e')
    elif t is dict:
        write(b'd')

        data = sorted(obj.items())
        for key, val in data:
            _dump_implementation(key, write, path + [id(obj)], cast)
            _dump_implementation(val, write, path + [id(obj)], cast)
        write(b'e')
    elif cast and t is bool:
        write(b'i')
        write(int_to_binary(int(obj)))
        write(b'e')
    else:
        raise BencodeTypeError(
            'type %s is not Bencode serializable' % type(obj).__name__
        )


def dump(obj, fp, cast=False):
    """Serialize ``obj`` as a Bencode formatted stream to ``fp``."""

    _dump_implementation(obj, fp.write, [], cast)


def dumps(obj, cast=False):
    """Serialize ``obj`` to a Bencode formatted ``str``."""

    fp = []
    _dump_implementation(obj, fp.append, [], cast)
    return b''.join(fp)


def _read_until(delimiter, read):
    """ Read char by char until ``delimiter`` occurs. """

    result = b''
    ch = read(1)
    if not ch:
        raise BencodeValueError('unexpected end of data')
    while ch != delimiter:
        result += ch
        ch = read(1)
        if not ch:
            raise BencodeValueError('unexpected end of data')
    return result


def _load_implementation(read):
    """ load()/loads() implementation """

    first = read(1)

    if first == b'e':
        return StopIteration
    if first == b'i':
        value = b''
        ch = read(1)
        while (b'0' <= ch <= b'9') or (ch == b'-'):
            value += ch
            ch = read(1)
        if ch == b'' or (ch == b'e' and value in (b'', b'-')):
            raise BencodeValueError('unexpected end of data')
        if ch != b'e':
            raise BencodeValueError('unexpected byte 0x%.2x' % ord(ch))
        return int(value)
    if b'0' <= first <= b'9':
        size = 0
        while b'0' <= first <= b'9':
            size = size * 10 + (ord(first) - ord('0'))
            first = read(1)
            if first == b'':
                raise BencodeValueError('unexpected end of data')
        if first != b':':
            raise BencodeValueError('unexpected byte 0x%.2x' % ord(first))
        data = read(size)
        if len(data) != size:
            raise BencodeValueError('unexpected end of data')
        return binary_return(data)
    if first == b'l':
        result = []
        while True:
            val = _load_implementation(read)
            if val is StopIteration:
                return result
            result.append(val)
    elif first == b'd':
        result = {}
        while True:
            this = read(1)
            if this == b'e':
                return result
            if this == b'':
                raise BencodeValueError('unexpected end of data')
            if not this.isdigit():
                raise BencodeValueError('unexpected byte 0x%.2x' % ord(this))
            size = int(this + _read_until(b':', read))
            key = read(size)
            val = _load_implementation(read)
            result[key] = val
    elif first == b'':
        raise BencodeValueError('unexpected end of data')
    else:
        raise BencodeValueError('unexpected byte 0x%.2x' % ord(first))


def load(fp):
    """Deserialize ``fp`` to a Python object."""

    return _load_implementation(fp.read)


def loads(data):
    """Deserialize ``s`` to a Python object."""

    fp = StringIO(data)
    return _load_implementation(fp.read)
