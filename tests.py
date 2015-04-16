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
]


@pytest.mark.parametrize(('binary', 'struct'), TEST_DATA)
def test_loads(binary, struct):
    cBencode.loads(binary) == struct


@pytest.mark.parametrize(('binary', 'struct'), TEST_DATA)
def test_dumps(binary, struct):
    assert cBencode.dumps(struct) == binary


@pytest.mark.parametrize(('binary', 'struct'), TEST_DATA)
def test_dump(binary, struct):
    fp = StringIO()
    cBencode.dump(struct, fp)
    assert fp.getvalue() == binary
