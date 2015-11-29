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


if hasattr(sys, 'pypy_version_info'):
    ext_modules = []
else:
    ext_modules = [
        Extension('better_bencode._fast', sources=['better_bencode/_fast.c']),
    ]


setup(
    name='better-bencode',
    version='0.2.0',
    url='https://github.com/kosqx/better-bencode',
    license='BSD',
    author='Krzysztof Kosyl',
    install_requires=[],
    author_email='krzysztof.kosyl@gmail.com',
    description='Fast, standard compliant Bencode serialization',
    long_description=read('README.rst'),
    packages=['better_bencode'],
    include_package_data=True,
    platforms='any',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',

        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
    ext_modules=ext_modules,
)
