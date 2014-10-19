# tools.py - path and filename manipulations

import sys
import os
import contextlib

__all__ = ['swapext', 'current_path', 'chdir', 'confirm']


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


def confirm(question, default=False):
    """Prompt the user to confirm an action."""
    hint = {True: 'Y/n', False: 'y/N', None: 'y/n'}[default]
    while True:
        answer = raw_input('%s [%s] ' % (question, hint)).strip().lower()
        if answer in ('y', 'yes'):
            return True
        elif answer in ('n', 'no'):
            return False
        elif not answer and default is not None:
            return default
        print("Please answer '(y)es' or '(n)o'.")
