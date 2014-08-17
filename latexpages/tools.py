# tools.py - path and filename manipulations

import sys
import os
import contextlib

__all__ = ['swapext', 'chdir', 'current_path']


def swapext(filename, extension, delimiter='.'):
    """Return filename replacing its extension, adding if it has none.

    >>> swapext('spam.eggs', 'ham')
    'spam.ham'

    >>> swapext('spam', 'ham')
    'spam.ham'
    """
    name, delim, ext = filename.rpartition(delimiter)
    if not delim:
        name = ext
    return '%s%s%s' % (name, delimiter, extension)


def current_path(*names):
    """Return the path to names relative to the current module."""
    depth = 0 if __name__ == '__main__' else 1

    frame = sys._getframe(depth)

    try:
        path = os.path.dirname(frame.f_code.co_filename)
    finally:
        del frame

    if names:
        path = os.path.join(path, *names)

    return os.path.realpath(path)


@contextlib.contextmanager
def chdir(*paths):
    """Change the current working directory, restore on context exit."""
    paths = ['' if p is None else p for p in paths]
    path = os.path.join(*paths)
    if not path:
        try:
            yield
        finally:
            pass
        return

    oldwd = os.getcwd()
    os.chdir(path)
    try:
        yield path
    finally:
        os.chdir(oldwd)
