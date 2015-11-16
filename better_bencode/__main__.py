#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
Commandline tool to validate and pretty-print Bencode::

    $ echo 'li12e3:fooe' | python -m better_bencode
    [12L, 'foo']
"""


import sys
import pprint


import better_bencode


def main(argv):
    """ Validate and pretty-print Bencode """

    if len(argv) == 2:
        fin = open(argv[1], 'rb')
    else:
        fin = sys.stdin

    try:
        data = better_bencode.load(fin)
        pprint.pprint(data)
        return 0
    except ValueError as exc:
        sys.stderr.write('Error: %s\n' % exc)
        return 1
    finally:
        fin.close()


sys.exit(main(sys.argv))
