"""Combine a collection of LaTeX documents into a single PDF file."""

from .cleaning import clean
from .building import make
from .numbering import paginate

__all__ = ['make', 'paginate', 'clean']

__title__ = 'latexpages'
__version__ = '0.8.1.dev0'
__author__ = 'Sebastian Bank <sebastian.bank@uni-leipzig.de>'
__license__ = 'MIT, see LICENSE.txt'
__copyright__ = 'Copyright (c) 2014-2025 Sebastian Bank'
