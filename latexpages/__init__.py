# latexpages - compile and combine latex docs into a single file

"""Combine a collection of LaTeX documents into a single PDF file."""

__title__ = 'latexpages'
__version__ = '0.1'
__author__ = 'Sebastian Bank <sebastian.bank@uni-leipzig.de>'
__license__ = 'MIT, see LICENSE'
__copyright__ = 'Copyright (c) 2014 Sebastian Bank'

from .build import make

__all__ = ['make']


def main():
    """Run the command-line interface."""
    import argparse

    parser = argparse.ArgumentParser(prog='latexpages',
        description='Compiles and combines LaTeX docs into a single PDF file')

    parser.add_argument('--version', action='version',
        version='%%(prog)s %s' % __version__)

    parser.add_argument('-c', dest='engine', metavar='latexmk|texify', default=None,
        help='use latexmk.pl or texify (default: guess from platform)')

    parser.add_argument('--keep', dest='cleanup', action='store_false',
        help='keep combination document(s) and their auxiliary files')

    parser.add_argument('filename',
        help='.ini-style file configuring the parts and output options')

    parser.add_argument('processes', nargs='?', type=int, default=None,
        help='number of parallel processes to use (default: one per core)')

    args = parser.parse_args()
    make(args.filename, args.processes, args.engine, args.cleanup)
