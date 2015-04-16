#!/usr/bin/env python
# -*- coding: utf-8 -*-


from distutils.core import setup, Extension


setup(
    name='cBencode',
    version='0.1',
    description='Bencode implemented as Python C  Extension',
    ext_modules=[
        Extension('cBencode', sources=['cBencode.c']),
    ],
)
