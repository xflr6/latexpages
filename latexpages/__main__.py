"""Entry points for command-line interface."""

import argparse
import os
import sys

from . import __version__, make, paginate, clean

__all__ = ['main', 'main_paginate', 'main_clean']

INIFILE = 'latexpages.ini'


def main() -> None:
    """Run the command-line interface."""
    parser = ArgumentParser(prog='latexpages',
        description='Compiles and combines LaTeX docs into a single PDF file')

    parser.add_argument('--version', action='version',
                        version=f'%(prog)s {_version()}')

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
             f'(default: {INIFILE} in the current directory)')

    args = parser.parse_args_default_filename()

    make(args.filename,
         processes=args.processes,
         engine=args.engine,
         cleanup=args.cleanup,
         only=args.only)


def main_paginate() -> None:
    """Run the command-line interface for the paginate utility."""
    parser = ArgumentParser(prog='latexpages-paginate',
        description='Computes and updates start page numbers in compiled parts and contents')

    parser.add_argument('--version', action='version',
                        version=f'%(prog)s {_version()}')

    parser.add_argument('filename', nargs='?', default=None,
        help='INI file configuring the parts and paginate options '
             f'(default: {INIFILE} in the current directory)')

    args = parser.parse_args_default_filename()
    paginate(args.filename)


def main_clean() -> None:
    """Run the command-line interface for the clean utility."""
    parser = ArgumentParser(prog='latexpages-clean',
        description='Lists intermediate files to delete and deletes them on confirmation.')

    parser.add_argument('--version', action='version',
                        version=f'%(prog)s {_version()}')

    parser.add_argument('--output', dest='clean_output', action='store_true',
        help='also delete the output directory (overrides INI file)')

    parser.add_argument('filename', nargs='?', default=None,
        help='INI file configuring the parts and clean options '
             f'(default: {INIFILE} in the current directory)')

    args = parser.parse_args_default_filename()
    clean(args.filename, clean_output=args.clean_output)


def _version() -> str:
    pkg_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return f'{__version__} from {pkg_dir} (python {sys.version[:3]})'


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
