==================================================
Send2Trash -- Send files to trash on all platforms
==================================================

This is a Python 3 package. The Python 2 package is at http://pypi.python.org/pypi/Send2Trash .

Send2Trash is a small package that sends files to the Trash (or Recycle Bin) *natively* and on
*all platforms*. On OS X, it uses native ``FSMoveObjectToTrashSync`` Cocoa calls, on Windows, it uses native (and ugly) ``SHFileOperation`` win32 calls. On other platforms, it follows the trash specifications from freedesktop.org.

``ctypes`` is used to access native libraries, so no compilation is necessary.

Installation
------------

Download the source from http://hg.hardcoded.net/send2trash and install it with::

>>> python setup.py install

Usage
-----

>>> from send2trash import send2trash
>>> send2trash('some_file')

When there's a problem ``OSError`` is raised.