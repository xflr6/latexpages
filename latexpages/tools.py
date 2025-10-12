"""Generic path and filename manipulations."""

from collections.abc import Iterator
import contextlib
import os
import signal
import sys

__all__ = ['swapext', 'current_path', 'chdir',
           'confirm',
           'ignore_sigint', 'NullPool']


def swapext(filename: str, extension: str, *, delimiter: str = '.') -> str:
    """Return filename replacing its extension, adding if it has none.

    >>> swapext('spam.eggs', 'ham')
    'spam.ham'

    >>> swapext('spam', 'ham')
    'spam.ham'
    """
    (name, delim, ext) = filename.rpartition(delimiter)
    if not delim:
        name = ext
    return f'{name}{delimiter}{extension}'


def current_path(*names: os.PathLike[str] | str) -> str:
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
def chdir(*paths: os.PathLike[str] | str | None) -> Iterator[str | None]:
    """Change the current working directory, restore on context exit."""
    path_parts: list[os.PathLike[str] | str]
    path_parts = [p if p is not None else '' for p in paths]
    path = os.path.join(*path_parts)
    if not path:
        yield None
        return

    oldwd = os.getcwd()
    os.chdir(path)
    try:
        yield os.fspath(path)
    finally:
        os.chdir(oldwd)


def confirm(question: str, *, default: bool = False) -> bool:
    """Prompt the user to confirm an action."""
    hint = {True: 'Y/n', False: 'y/N', None: 'y/n'}[default]
    while True:
        answer = input(f'{question} [{hint}] ').strip().lower()
        if answer in ('y', 'yes'):
            return True
        elif answer in ('n', 'no'):
            return False
        elif not answer and default is not None:
            return default
        print("Please answer '(y)es' or '(n)o'.")


def ignore_sigint() -> None:
    """Ignore KeyboardInterrupt, initializer for multiprocessing.Pool."""
    signal.signal(signal.SIGINT, signal.SIG_IGN)


class NullPool(object):
    """No-subprocess replacement for multiprocessing.Pool."""

    def __init__(self, processes=None, initializer=None):
        if processes not in (1, None):
            raise ValueError(f'{self} with {processes=}')
        assert initializer in (ignore_sigint, None)

    def map(self, func, iterable, *, chunksize=None):
        if chunksize not in (1, None):
            raise ValueError(f'{self}.map() with {chunksize=}')
        return list(map(func, iterable))

    def terminate(self):
        pass

    def close(self):
        pass

    def join(self):
        pass
