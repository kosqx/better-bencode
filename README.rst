==============
Better Bencode
==============

:author: Krzysztof Kosyl
:version: 0.1.0
:date: 2015-04-20

Still alpha!


Install
-------

::

   $ pip install better-bencode


Example
-------

.. code-block:: pycon

    >>> import better_bencode
    >>> dumped = better_bencode.dumps(['spam', 42])
    >>> better_bencode.loads(dumped)
    ['spam', 42]
