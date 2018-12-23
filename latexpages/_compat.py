# _compat.py - Python 2/3 compatibility

import sys

PY2 = (sys.version_info.major == 2)


if PY2:
    input = raw_input

    apply = apply

    from itertools import imap as map, izip as zip

    def iteritems(d):
        return d.iteritems()

    from ConfigParser import SafeConfigParser as ConfigParser


else:
    input = input

    def apply(object, args=(), kwargs=None):
        if kwargs is None:
            kwargs = {}
        return object(*args, **kwargs)

    map = map
    zip = zip

    def iteritems(d):
        return iter(d.items())

    from configparser import ConfigParser
