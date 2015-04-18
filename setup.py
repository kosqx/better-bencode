#!/usr/bin/env python
# -*- coding: utf-8 -*-


import io
import codecs
import os
import sys

from setuptools import setup, Extension


def read(filename):
    with io.open(filename, encoding='utf-8') as f:
        data = f.read()
    return data


setup(
    name='better-bencode',
    version='0.1',
    url='https://github.com/kosqx/better-bencode',
    license='BSD',
    author='Krzysztof Kosyl',
    tests_require=['pytest'],
    install_requires=[],
    author_email='krzysztof.kosyl@gmail.com',
    description='Bencode implemented as Python C Extension',
    long_description=read('README.rst'),
    packages=['better_bencode', 'better_bencode.tests'],
    include_package_data=True,
    platforms='any',
    test_suite='better_bencode.tests.test_bencode',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',

        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
    extras_require={
        'testing': ['pytest'],
    },
    ext_modules=[
        Extension('better_bencode_fast', sources=['better_bencode/_fast.c']),
    ],
)
