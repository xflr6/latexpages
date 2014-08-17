# _compat.py - Python 2/3 compatibility

import sys

PY2 = sys.version_info[0] == 2


if PY2:
    apply = apply

    def iteritems(d):
        return d.iteritems()

    from ConfigParser import SafeConfigParser as ConfigParser


else:
    def apply(object, args=(), kwargs=None):
        if kwargs is None:
            kwargs = {}
        return object(*args, **kwargs)

    def iteritems(d):
        return iter(d.items())

    from configparser import ConfigParser
