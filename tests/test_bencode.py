#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import os.path


# remove top repository dir to avoid importing local code
sys.path = [
    directory
    for directory in sys.path
    if not os.path.exists(os.path.join(directory, 'README.rst'))
]


if sys.version_info[0] == 2:
    try:
        from cStringIO import StringIO
    except ImportError:
        from StringIO import StringIO
else:
    from io import BytesIO as StringIO


import pytest


import better_bencode._pure as pure
import better_bencode as auto
try:
    import better_bencode._fast as fast
except ImportError as e:
    print(e)
    fast = None


MODULES = [module for module in [auto, fast, pure] if module is not None]


@pytest.mark.parametrize('module', MODULES)
def test_error_load(module):
    assert hasattr(module, 'BencodeValueError')
    assert issubclass(module.BencodeValueError, ValueError)


@pytest.mark.parametrize('module', MODULES)
def test_error_dump(module):
    assert hasattr(module, 'BencodeTypeError')
    assert issubclass(module.BencodeTypeError, TypeError)


TEST_DATA = [
    (b'de', {}),
    (b'le', []),
    (b'i0e', 0),
    (b'i42e', 42),
    (b'i-42e', -42),
    (b'i9223372036854775807e', 2**63-1),
    (b'i-9223372036854775808e', -(2**63)),
    (b'0:', b''),
    (b'4:spam', b'spam'),
    (b'l4:spami42ee', [b'spam', 42]),
    (b'd3:fooi42ee', {b'foo': 42}),
    (b'd3:bar4:spam3:fooi42ee', {b'bar': b'spam', b'foo': 42}),
    (b'd1:ai1e1:bi2e1:ci3ee', {b'a': 1, b'b': 2, b'c': 3}),
    (b'd1:a1:be', {b'a': b'b'}),
    (b'3:\x00\x01\x02', bytearray([0, 1, 2])),
    (b'3:abc', bytearray('abc', 'ascii'))
]
TESTS = [
    (module,) + test
    for module in MODULES
    for test in TEST_DATA
]


@pytest.mark.parametrize(('module', 'binary', 'struct'), TESTS)
def test_loads(module, binary, struct):
    assert module.loads(binary) == struct


@pytest.mark.parametrize(('module', 'binary', 'struct'), TESTS)
def test_load(module, binary, struct):
    fp = StringIO(binary)
    assert module.load(fp) == struct


@pytest.mark.parametrize(('module', 'binary', 'struct'), TESTS)
def test_dumps(module, binary, struct):
    assert module.dumps(struct) == binary


@pytest.mark.parametrize(('module', 'binary', 'struct'), TESTS)
def test_dump(module, binary, struct):
    fp = StringIO()
    module.dump(struct, fp)
    assert fp.getvalue() == binary


#####################################################################
# dump TypeError tests


TESTS_TYPEERROR = [
    (module,  test)
    for module in MODULES
    for test in [
        (), set(), frozenset(),
        len, TypeError,
        True, False, None, 1.0,
    ]
]


@pytest.mark.parametrize(('module', 'struct'), TESTS_TYPEERROR)
def test_dump_typeerror(module, struct):
    with pytest.raises(TypeError) as excinfo:
        fp = StringIO()
        module.dump(struct, fp)
    assert type(struct).__name__ in str(excinfo.value)


@pytest.mark.parametrize(('module', 'struct'), TESTS_TYPEERROR)
def test_dump_dumperror(module, struct):
    with pytest.raises(module.BencodeTypeError) as excinfo:
        fp = StringIO()
        module.dump(struct, fp)
    assert type(struct).__name__ in str(excinfo.value)


@pytest.mark.parametrize(('module', 'struct'), TESTS_TYPEERROR)
def test_dumps_typeerror(module, struct):
    with pytest.raises(TypeError) as excinfo:
        module.dumps(struct)
    assert type(struct).__name__ in str(excinfo.value)


@pytest.mark.parametrize(('module', 'struct'), TESTS_TYPEERROR)
def test_dumps_dumperror(module, struct):
    with pytest.raises(module.BencodeTypeError) as excinfo:
        module.dumps(struct)
    assert type(struct).__name__ in str(excinfo.value)



@pytest.mark.parametrize('module', MODULES)
def test_dumps_reference_list(module):
    a = [[]]
    a[0].append(a)

    with pytest.raises(ValueError) as excinfo:
        module.dumps(a)
    assert str(excinfo.value) == 'circular reference detected'

@pytest.mark.parametrize('module', MODULES)
def test_dumps_reference_list_deep(module):
    a = [[[[[[[[[[[[[[[]]]]]]]]]]]]]]]
    a[0][0][0][0][0][0][0][0][0][0][0][0][0].append(a)

    with pytest.raises(ValueError) as excinfo:
        module.dumps(a)
    assert str(excinfo.value) == 'circular reference detected'


@pytest.mark.parametrize('module', MODULES)
def test_dumps_reference_dict(module):
    a = {b'a': {b'b': {}}}
    a[b'a'][b'b'][b'c'] = a

    with pytest.raises(ValueError) as excinfo:
        module.dumps(a)
    assert str(excinfo.value) == 'circular reference detected'


#####################################################################
# load ValueError tests


TESTS_VALUEERROR = [
    (module,  binary, msg)
    for module in MODULES
    for binary, msg in [
        (b'<', 'unexpected byte 0x3c'),
        (b' ', 'unexpected byte 0x20'),
        (b'x', 'unexpected byte 0x78'),
        (b'', 'unexpected end of data'),

        (b'1', 'unexpected end of data'),
        (b'1:', 'unexpected end of data'),
        (b'1x', 'unexpected byte 0x78'),

        (b'i', 'unexpected end of data'),
        (b'ie', 'unexpected end of data'),
        (b'i-e', 'unexpected end of data'),
        (b'ixe', 'unexpected byte 0x78'),

        (b'l', 'unexpected end of data'),
        (b'lx', 'unexpected byte 0x78'),
        (b'lxe', 'unexpected byte 0x78'),
        (b'l1:a', 'unexpected end of data'),
        (b'l1:ax', 'unexpected byte 0x78'),

        (b'd', 'unexpected end of data'),
        (b'dx', 'unexpected byte 0x78'),
        (b'dxe', 'unexpected byte 0x78'),
        (b'd1:a', 'unexpected end of data'),
        (b'd1:ax', 'unexpected byte 0x78'),
        (b'd1:a1:b', 'unexpected end of data'),
        (b'd1:a1:bx', 'unexpected byte 0x78'),
    ]
]


@pytest.mark.parametrize(('module', 'binary', 'msg'), TESTS_VALUEERROR)
def test_load_valueerror(module, binary, msg):
    with pytest.raises(ValueError) as excinfo:
        fp = StringIO(binary)
        module.load(fp)
    assert str(excinfo.value) == msg


@pytest.mark.parametrize(('module', 'binary', 'msg'), TESTS_VALUEERROR)
def test_loads_valueerror(module, binary, msg):
    with pytest.raises(ValueError) as excinfo:
        module.loads(binary)
    assert str(excinfo.value) == msg


#####################################################################
# docstrings


@pytest.mark.parametrize('module', MODULES)
def test_docstrings_dump(module):
    assert module.dump.__doc__ == "Serialize ``obj`` as a Bencode formatted stream to ``fp``."


@pytest.mark.parametrize('module', MODULES)
def test_docstrings_dumps(module):
    assert module.dumps.__doc__ == "Serialize ``obj`` to a Bencode formatted ``str``."


@pytest.mark.parametrize('module', MODULES)
def test_docstrings_load(module):
    assert module.load.__doc__ == "Deserialize ``fp`` to a Python object."


@pytest.mark.parametrize('module', MODULES)
def test_docstrings_loads(module):
    assert module.loads.__doc__ == "Deserialize ``s`` to a Python object."


#####################################################################
# cast


from collections import namedtuple
Point = namedtuple('Point', 'x y')


class MyList(list):
    def __init__(self, *data):
        list.__init__(self, data)


CAST_TEST_DATA = [
    (False, b'i0e', 0),
    (True,  b'i1e', 1),

    ((),  b'le', []),
    ((1,),  b'li1ee', [1]),

    (Point(-1, 1),  b'li-1ei1ee', [-1, 1]),
    (MyList(-1, 1),  b'li-1ei1ee', [-1, 1]),

]
CAST_TESTS = [
    (module,) + test
    for module in MODULES
    for test in CAST_TEST_DATA
]

@pytest.mark.parametrize(('module', 'indata', 'binary', 'outdata'), CAST_TESTS)
def test_cast_dumps_ok(module, indata, binary, outdata):
    dumped = module.dumps(indata, cast=True)
    assert dumped == binary
    assert module.loads(dumped) == outdata


@pytest.mark.parametrize(('module', 'indata', 'binary', 'outdata'), CAST_TESTS)
def test_cast_dumps_error(module, indata, binary, outdata):
    with pytest.raises(TypeError) as excinfo:
        module.dumps(indata)
