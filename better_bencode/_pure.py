#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys


if sys.version_info[0] == 2:
    try:
        from cStringIO import StringIO
    except ImportError:
        from StringIO import StringIO
else:
    from io import BytesIO as StringIO


if sys.version_info[0] == 2:
    integer_types = (int, long)
    binary_type = str
    int_to_binary = lambda val: str(val)
else:
    integer_types = (int,)
    binary_type = bytes
    int_to_binary = lambda val: bytes(str(val), 'ascii')

def _dump_implementation(obj, write):
    t = type(obj)

    if obj is None or obj is False or obj is True:
        write({None: b'n', False: b'f', True: b't'}[obj])
    elif t in integer_types:
        #write('i%de' % obj)
        write(b'i')
        write(int_to_binary(obj))
        write(b'e')
    elif t is binary_type:
        write(int_to_binary(len(obj)))
        write(b':')
        write(obj)
    elif t is list:
        write(b'l')
        for item in obj:
            _dump_implementation(item, write)
        write(b'e')
    elif t is dict:
        write(b'd')
        # for key in sorted(obj.keys()):
        #         # if not isinstance(key, str):
        #         #         raise ValueError, 'dictionary key must be a str, %r is not' % key
        #         _dump_implementation(key, write)
        #         _dump_implementation(obj[key], write)

        data = sorted(obj.items())
        for key, val in data:
            # if not isinstance(key, str):
            #         raise ValueError, 'dictionary key must be a str, %r is not' % key
            _dump_implementation(key, write)
            _dump_implementation(val, write)
        write(b'e')
    else:
        raise TypeError(
            'type %s is not Bencode serializable' % type(obj).__name__
        )


def dump(obj, fp):
    _dump_implementation(obj, fp.write)


def dumps(obj):
    fp = []
    _dump_implementation(obj, fp.append)
    return b''.join(fp)


def read_until(delimiter, read):
    result = b''
    ch = read(1)
    # if not ch:
    #     raise ValueError('unexpected end of data (until)')
    while ch != delimiter:
        result += ch
        ch = read(1)
        # if not ch:
        #     raise ValueError('unexpected end of data (until)')
    return result


def _load_implementation(read):
    special = {b'n': None, b'f': False, b't': True}

    first = read(1)
    # if not first:
    #         raise ValueError('unexpected end of data (cmd)')

    if first == b'e':
        return StopIteration
    elif first in special:
        return special[first]
    elif first == b'i':
        return int(read_until(b'e', read))
    elif b'0' <= first <= b'9':
        size = int(first + read_until(b':', read))
        data = read(size)
        # if len(data) != size:
        #         raise ValueError('unexpected end of data (str)')
        return data
    elif first == b'l':
        result = []
        while True:
            val = _load_implementation(read)
            if val is StopIteration:
                return result
            result.append(val)
    elif first == b'd':
        result = {}
        while True:
            # key = _load_implementation(read)
            # if key is StopIteration:
            #         return result
            this = read(1)
            if this == b'e':
                return result
            elif this == b'':
                raise ValueError('unexpected end of data')
            elif not this.isdigit():
                raise ValueError('unexpected byte 0x%.2x' % ord(this))
            size = int(this + read_until(b':', read))
            key = read(size)
            val = _load_implementation(read)
            result[key] = val
    elif first == b'':
        raise ValueError('unexpected end of data')
    else:
        raise ValueError('unexpected byte 0x%.2x' % ord(first))


def load(fd):
    return _load_implementation(fd.read)


def loads(data):
    fp = StringIO(data)
    return _load_implementation(fp.read)
