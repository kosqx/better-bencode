import cBencode, sys

import json, time, marshal

from cStringIO import StringIO

class Out(object):
	def write(self, value):
		print '>>', repr(value)

# out = Out()
# cBencode.dump({"a": 1, "b": 1234567891234567891234567}, out)
# print


EXAMPLES = [
	#'foo bar baz',
	#1,
	range(100),
	["zero", 0, "one", 1, "two", 2],
	{"zero": 0, "one": 1, "two": 2},
]

fp = StringIO()
cBencode.dump(EXAMPLES[0], fp)
print len(fp.getvalue())


def test_bencode(N):
	for i in xrange(N):
		for ex in EXAMPLES:
			fp = StringIO()
			cBencode.dump(ex, fp)
			fp.getvalue()


def _test_json(N):
	for i in xrange(N):
		for ex in EXAMPLES:
			fp = StringIO()
			json.dump(ex, fp)
			fp.getvalue()

# def test_marshal(N):
# 	for i in xrange(N):
# 		for ex in EXAMPLES:
# 			fp = StringIO()
# 			marshal.dump(ex, fp)
# 			fp.getvalue()

def test_repr(N):
	for i in xrange(N):
		for ex in EXAMPLES:
			fp = StringIO()
			fp.write(repr(ex))
			fp.getvalue()


g = globals()
for name, code in g.items():
	if name.startswith('test_'):
		start = time.time()
		code(1000)
		stop  = time.time()

		print '%15s  %5.3f' % (name, (stop - start) * 1000)

print '-' * 100

print cBencode.loads('n')
print cBencode.loads('f')
print cBencode.loads('t')
print cBencode.loads('i123e')
print repr(cBencode.loads('3:foo'))

