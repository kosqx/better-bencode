#!/usr/bin/env python
# -*- coding: utf-8 -*-


import time
from cStringIO import StringIO

import cBencode

import json
import marshal
import pickle
import cPickle
import msgpack



EXAMPLES = [
    range(100),
    ["zero", 0, "one", 1, "two", 2],
    {"zero": 0, "one": 1, "two": 2},
]





class Empty(object):
    __name__ = 'Empty'
    def dump(self, value, fp): return ''
    def dumps(self, value): return ''
    def load(self, fp): return None
    def loads(self, value): return None


print '%-10s  %10s  %10s  %10s  %10s' % ('MODULE', 'dump', 'dumps', 'load', 'loads')
for module in [Empty(), cBencode, json, marshal, pickle, cPickle, msgpack]:
    time_start = time.time()
    for example in EXAMPLES:
        for i in xrange(10000 * (module != marshal)):
            fp = StringIO()
            module.dump(example, fp)
            fp.getvalue()
    dump_duration = time.time() - time_start

    time_start = time.time()
    for example in EXAMPLES:
        for i in xrange(10000):
            module.dumps(example)
    dumps_duration = time.time() - time_start

    time_start = time.time()
    for example in EXAMPLES:
        example_encoded = module.dumps(example)
        for i in xrange(10000 * (module != marshal)):
            fp = StringIO(example_encoded)
            module.load(fp)
    load_duration = time.time() - time_start

    time_start = time.time()
    for example in EXAMPLES:
        example_encoded = module.dumps(example)
        for i in xrange(10000):
            module.loads(example_encoded)
    loads_duration = time.time() - time_start

    print '%-10s  %8.3fms  %8.3fms  %8.3fms  %8.3fms' % (
        module.__name__,
        dump_duration * 1000.0, dumps_duration * 1000.0,
        load_duration * 1000.0, loads_duration * 1000.0
    )
