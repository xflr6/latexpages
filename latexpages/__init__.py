# latexpages - compile and combine latex docs into a single file

"""Combine a collection of LaTeX documents into a single PDF file."""

from .building import make
from .numbering import paginate
from .cleaning import clean

__all__ = ['make', 'paginate', 'clean']

__title__ = 'latexpages'
__version__ = '0.6.4.dev0'
__author__ = 'Sebastian Bank <sebastian.bank@uni-leipzig.de>'
__license__ = 'MIT, see LICENSE'
__copyright__ = 'Copyright (c) 2014-2017 Sebastian Bank'
