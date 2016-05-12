#!/usr/bin/env python
# -*- coding: utf-8 -*-


import io
import codecs
import os
import sys

from setuptools import setup, Extension
from distutils.command.build_ext import build_ext
from distutils.errors import \
    CCompilerError, DistutilsExecError, DistutilsPlatformError


def read(filename):
    with io.open(filename, encoding='utf-8') as f:
        data = f.read()
    return data


class BuildFailed(Exception):
    pass


class SafeBuildExt(build_ext):
    def run(self):
        try:
            build_ext.run(self)
        except DistutilsPlatformError:
            raise BuildFailed()

    def build_extension(self, ext):
        try:
            build_ext.build_extension(self, ext)
        except (CCompilerError, DistutilsExecError, DistutilsPlatformError):
            raise BuildFailed()


def run_setup(with_binary):
    if with_binary:
        ext_modules = [
            Extension(
                'better_bencode._fast',
                sources=['better_bencode/_fast.c'],
            ),
        ]
        cmdclass = dict(build_ext=SafeBuildExt)
    else:
        ext_modules = []
        cmdclass = dict()

    setup(
        name='better-bencode',
        version='0.2.1',
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
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: Implementation :: CPython',
            'Programming Language :: Python :: Implementation :: PyPy',
        ],
        ext_modules=ext_modules,
        cmdclass=cmdclass,
    )


try:
    run_setup(not hasattr(sys, 'pypy_version_info'))
except BuildFailed:
    print('*' * 75)
    print("WARNING: The C extension could not be compiled.")
    print("Module better_bencode will work correctly, but will be slower.")
    print('*' * 75)

    run_setup(False)
