#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
	from better_bencode_fast import dump, dumps, load, loads
except ImportError:
	from better_bencode._pure import dump, dumps, load, loads
