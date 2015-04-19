#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO


def _dump_implementation(obj, write):
    t = type(obj)

    if obj is None or obj is False or obj is True:
        write({None: 'n', False: 'f', True: 't'}[obj])
    elif t is int or t is long:
        #write('i%de' % obj)
        write('i')
        write(str(obj))
        write('e')
    elif t is str:
        write(str(len(obj)))
        write(':')
        write(obj)
    elif t is list:
        write('l')
        for item in obj:
            _dump_implementation(item, write)
        write('e')
    elif t is dict:
        write('d')
        # for key in sorted(obj.keys()):
        #         # if not isinstance(key, str):
        #         #         raise ValueError, 'dictionary key must be a str, %r is not' % key
        #         _dump_implementation(key, write)
        #         _dump_implementation(obj[key], write)

        data = obj.items()
        data.sort()
        for key, val in data:
            # if not isinstance(key, str):
            #         raise ValueError, 'dictionary key must be a str, %r is not' % key
            _dump_implementation(key, write)
            _dump_implementation(val, write)
        write('e')
    else:
        raise ValueError, ('unsuported value %r' % (obj, ))


def dump(obj, fp):
    _dump_implementation(obj, fp.write)


def dumps(obj):
    fp = []
    _dump_implementation(obj, fp.append)
    return ''.join(fp)


def read_until(delimiter, read):
    result = ''
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
    special = {'n': None, 'f': False, 't': True}

    first = read(1)
    # if not first:
    #         raise ValueError('unexpected end of data (cmd)')

    if first == 'e':
        return StopIteration
    elif first in special:
        return special[first]
    elif first == 'i':
        return int(read_until('e', read))
    elif '0' <= first <= '9':
        size = int(first + read_until(':', read))
        data = read(size)
        # if len(data) != size:
        #         raise ValueError('unexpected end of data (str)')
        return data
    elif first == 'l':
        result = []
        while True:
            val = _load_implementation(read)
            if val is StopIteration:
                return result
            result.append(val)
    elif first == 'd':
        result = {}
        while True:
            # key = _load_implementation(read)
            # if key is StopIteration:
            #         return result
            this = read(1)
            if this == 'e':
                return result
            size = int(this + read_until(':', read))
            key = read(size)
            val = _load_implementation(read)
            result[key] = val
    else:
        raise ValueError, 'unsuported value %r' % first


def load(fd):
    return _load_implementation(fd.read)


def loads(data):
    fp = StringIO(data)
    return _load_implementation(fp.read)
