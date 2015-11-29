#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from better_bencode._fast import dump, dumps, load, loads
    from better_bencode._fast import BencodeValueError, BencodeTypeError
except ImportError:
    from better_bencode._pure import dump, dumps, load, loads
    from better_bencode._pure import BencodeValueError, BencodeTypeError