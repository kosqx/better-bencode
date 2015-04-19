#!/usr/bin/env python
# -*- coding: utf-8 -*-


from cStringIO import StringIO


import pytest


import better_bencode_fast as fast
import better_bencode._pure as pure
import better_bencode as auto


TEST_DATA = [
    ('de', {}),
    ('le', []),
    ('i0e', 0),
    ('i42e', 42),
    ('i-42e', -42),
    ('0:', ''),
    ('4:spam', 'spam'),
    ('l4:spami42ee', ['spam', 42]),
    ('d3:fooi42ee', {'foo': 42}),
    ('d' '3:bar' '4:spam' '3:foo' 'i42e' 'e', {'bar': 'spam', 'foo': 42}),
    ('d' '1:a' 'i1e' '1:b' 'i2e' '1:c' 'i3e' 'e', {'a': 1, 'b': 2, 'c': 3}),

    # extra types
    ('n', None),
    ('f', False),
    ('t', True),
]
TESTS = [
    (module,) + test
    for module in [auto, fast, pure]
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
