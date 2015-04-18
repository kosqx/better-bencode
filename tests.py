#!/usr/bin/env python
# -*- coding: utf-8 -*-


from cStringIO import StringIO


import pytest


import cBencode


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
]


@pytest.mark.parametrize(('binary', 'struct'), TEST_DATA)
def test_loads(binary, struct):
    cBencode.loads(binary) == struct


@pytest.mark.parametrize(('binary', 'struct'), TEST_DATA)
def test_load(binary, struct):
    fp = StringIO(binary)
    assert cBencode.load(fp) == struct


@pytest.mark.parametrize(('binary', 'struct'), TEST_DATA)
def test_dumps(binary, struct):
    assert cBencode.dumps(struct) == binary


@pytest.mark.parametrize(('binary', 'struct'), TEST_DATA)
def test_dump(binary, struct):
    fp = StringIO()
    cBencode.dump(struct, fp)
    assert fp.getvalue() == binary
