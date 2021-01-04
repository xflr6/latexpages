# pdfpages.py - concatenate pdf files with the latex pdfpages package

import glob
import os
import string

from . import backend
from . import tools

__all__ = ['Source']


class Template(object):
    """Skeleton for the combining pdfpages document."""

    _filename = tools.current_path('template.tex')

    _encoding = 'utf-8'

    def __init__(self, filename=None):
        if filename is None:
            filename = self._filename

        with open(filename, encoding=self._encoding) as fd:
            data = fd.read()

        self._template = string.Template(data)

    def substitute(self, context):
        return self._template.safe_substitute(context)


class Document(object):
    r"""Document body with \includepdfmerge commands."""

    _pagenumbering = r'\pagenumbering{%s}'

    _includepdf = r'\includepdfmerge[%s]{%s}'

    _includepdfopts = {False: 'fitpaper',
                       True: 'nup=2x1,openright'}

    def __init__(self, includepdfopts=None):
        if includepdfopts is not None:
            self._includepdfopts = includepdfopts

    def _include(self, filenames, two_up):
        opts = self._includepdfopts[two_up]
        args = ','.join(f'{f},-' for f in filenames)
        return self._includepdf % (opts, args)

    def _document(self, two_up):
        if two_up:
            if self._frontmatter:
                raise NotImplementedError
            yield self._include(self._mainmatter, True)
            return
        if self._frontmatter:
            yield self._pagenumbering % 'roman'
            yield self._include(self._frontmatter, False)
            yield self._pagenumbering % 'arabic'
        yield self._include(self._mainmatter, False)

    def document(self, two_up=False):
        return '\n'.join(self._document(two_up))


class Source(Document, Template):
    """LaTeX document to combine PDFs with pdfpages."""

    _documentclass = 'scrartcl'

    _documentopts = {False: 'paper=a5',
                     True: 'paper=a4,landscape'}

    def __init__(self, frontmatter, mainmatter, context=None, template=None,
                 includepdfopts=None, documentclass=None, documentopts=None):
        self._frontmatter = list(frontmatter)
        self._mainmatter = list(mainmatter)

        if context is None:
            context = {}
        self._context = {k.upper(): v for k, v in context.items()}

        Template.__init__(self, template)

        Document.__init__(self, includepdfopts)

        if documentclass is not None:
            self._documentclass = documentclass
        if documentopts is not None:
            self._documentopts = documentopts

    def __setitem__(self, key, value):
        self._context[key.upper()] = value

    def source(self, two_up=False):
        context = self._context.copy()
        context['__CLASS__'] = self._documentclass
        context['__OPTIONS__'] = self._documentopts[two_up]
        context['__DOCUMENT__'] = self.document(two_up)
        return self.substitute(context)

    def render(self, filename, two_up=False, view=False, engine=None,
               options=None, cleanup=False):
        source = self.source(two_up)

        with open(filename, 'w', encoding=self._encoding) as fd:
            fd.write(source)

        backend.compile(filename, view=view, engine=engine, options=options)

        if cleanup:
            self.cleanup(filename)

    def cleanup(self, filename):
        namefiles = glob.glob(tools.swapext(filename, '*'))
        remove = set(namefiles) - {tools.swapext(filename, 'pdf')}
        for filename in remove:
            os.remove(filename)
