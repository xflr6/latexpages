# __main__.py - entry points for the latexpages commands

"""Command-line interface."""

import os
import sys
import argparse

from . import __version__, make, paginate, clean

__all__ = ['main', 'main_paginate', 'main_clean']

INIFILE = 'latexpages.ini'


def main():
    """Run the command-line interface."""
    parser = ArgumentParser(prog='latexpages',
        description='Compiles and combines LaTeX docs into a single PDF file')

    parser.add_argument('--version', action='version',
        version='%%(prog)s %s' % _version())

    parser.add_argument('-c', dest='engine', choices=['latexmk', 'texify'], default=None,
        help='use latexmk.pl or texify (default: guess from platform)')

    parser.add_argument('--keep', dest='cleanup', action='store_false',
        help='keep combination document(s) and their auxiliary files')

    parser.add_argument('--only', dest='only', metavar='<part>', default=None,
        help='compile the given part without combining')

    parser.add_argument('--processes', dest='processes', metavar='<n>', type=int,  default=None,
        help='number of parallel processes (default: one per core)')

    parser.add_argument('filename', nargs='?', default=None,
        help='INI file configuring the parts and output options '
             '(default: %s in the current directory)' % INIFILE)

    args = parser.parse_args_default_filename()

    if (__name__ == '__main__' and sys.platform == 'win32' and
        sys.version_info[:2] < (3, 2) and args.processes != 1):
        # http://bugs.python.org/issue17101
        # http://bugs.python.org/issue10845
        raise NotImplementedError('__main__.py invocation is not compatible with '
            'multiprocessing in Python %d.%d under Windows. '
            'Use the latexpages command from the Python "Scripts" directory instead. '
            'To disable multiprocessing, pass "--processes 1" as command-line argument.'
            % sys.version_info[:2])

    make(args.filename, args.processes, args.engine, args.cleanup, args.only)


def main_paginate():
    """Run the command-line interface for the paginate utility."""
    parser = ArgumentParser(prog='latexpages-paginate',
        description='Computes and updates start page numbers in compiled parts and contents')

    parser.add_argument('--version', action='version',
        version='%%(prog)s %s' % _version())

    parser.add_argument('filename', nargs='?', default=None,
        help='INI file configuring the parts and paginate options '
             '(default: %s in the current directory)' % INIFILE)

    args = parser.parse_args_default_filename()
    paginate(args.filename)


def main_clean():
    """Run the command-line interface for the clean utility."""
    parser = ArgumentParser(prog='latexpages-clean',
        description='')

    parser.add_argument('--version', action='version',
        version='%%(prog)s %s' % _version())

    parser.add_argument('filename', nargs='?', default=None,
        help='INI file configuring the parts and clean options '
             '(default: %s in the current directory)' % INIFILE)

    parser.add_argument('clean_output', nargs='?', choices=['yes', 'no'], default=None,
        help='also delete the output directory (overrides INI file)')

    args = parser.parse_args_default_filename()
    clean(args.filename, {'yes': True, 'no': False, None: None}[args.clean_output])


def _version():
    pkg_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return '%s from %s (python %s)' % (__version__, pkg_dir, sys.version[:3])


class ArgumentParser(argparse.ArgumentParser):

    def parse_args_default_filename(self):
        args = self.parse_args()
        if args.filename is None:
            if os.path.exists(INIFILE):
                args.filename = INIFILE
            else:
                self.error('too few arguments')
        return args


if __name__ == '__main__':
    main()
