==============
Better Bencode
==============

:author: Krzysztof Kosyl
:version: 0.2.1
:date: 2016-05-12


Why use ``better_bencode``?
---------------------------

* standard Python object serialization functions: ``load()``, ``loads()``, ``dump()``, ``dumps()``
* works with Python 2.6, 2.7, 3.3, 3.4, 3.5 and PyPy
* 4.5 times faster than ``bencode`` module, thanks to C Extension
* well tested


Installation
------------

::

   $ pip install better-bencode


Example
-------

.. code-block:: pycon

    >>> import better_bencode
    >>> dumped = better_bencode.dumps(['spam', 42])
    >>> better_bencode.loads(dumped)
    ['spam', 42]
