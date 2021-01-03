# __main__.py - entry points for the latexpages commands

"""Command-line interface."""

import argparse
import os
import sys

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

    parser.add_argument('--processes', dest='processes', metavar='<n>', type=int, default=None,
        help='number of parallel processes (default: one per core)')

    parser.add_argument('filename', nargs='?', default=None,
        help='INI file configuring the parts and output options '
             '(default: %s in the current directory)' % INIFILE)

    args = parser.parse_args_default_filename()

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
        description='Lists intermediate files to delete and deletes them on confirmation.')

    parser.add_argument('--version', action='version',
        version='%%(prog)s %s' % _version())

    parser.add_argument('--output', dest='clean_output', action='store_true',
        help='also delete the output directory (overrides INI file)')

    parser.add_argument('filename', nargs='?', default=None,
        help='INI file configuring the parts and clean options '
             '(default: %s in the current directory)' % INIFILE)

    args = parser.parse_args_default_filename()
    clean(args.filename, args.clean_output)


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
