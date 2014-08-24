# jobs.py - parse .ini-style config file into function call args

import os
import shlex
from functools import partial

from ._compat import ConfigParser

from . import tools

__all__ = ['Job']


class Job(object):
    """INI-file giving the document collection parts and how to combine them."""

    _defaults = tools.current_path('settings.ini')

    _sections = ('make', 'parts', 'template', 'substitute', 'compile', 'paginate')

    @staticmethod
    def _get_string(config, section, option, optional=False, default=None):
        if config.has_option(section, option):
            value = config.get(section, option).strip()
        else:
            value = ''
        if not value:
            value = default
        if not optional and not value:
            raise ValueError('empty %s option in %s section'
                % (option, section))
        return value

    @staticmethod
    def _get_list(config, section, option, optional=False):
        if config.has_option(section, option):
            value = config.get(section, option).strip().split()
        else:
            value = []
        if not optional and not value:
            raise ValueError('empty %s option in %s section'
                % (option, section))
        return value

    def _get_path(self, filename, default=None):
        if filename:
            filepath = os.path.join(self.config_dir, filename)
            return os.path.realpath(filepath)
        else:
            return default

    def __init__(self, filename, engine=None, cleanup=True):
        cfg = ConfigParser()
        if not os.path.exists(filename):
            raise ValueError('file not found: %r' % filename)
        parsed = cfg.read([self._defaults, filename])
        assert len(parsed) == 2

        self.config_dir = os.path.dirname(filename)

        for section in self._sections:
            getters = {
                'string': partial(self._get_string, cfg, section),
                'lst': partial(self._get_list, cfg, section),
                'boolean': partial(cfg.getboolean, section),
                'items': partial(cfg.items, section),
            }
            getattr(self, '_parse_%s' % section)(**getters)

        self.engine = engine
        self.cleanup = cleanup

    def _parse_make(self, string, boolean, **kwargs):
        self.name = string('name')
        self.directory = string('directory')

        self.two_up = string('two_up', optional=True)
        self.make_two_up = boolean('make_two_up')

        self._front_name = string('frontmatter')
        self._main_name = string('mainmatter')
        self._extras_name = string('extras')

    def _parse_parts(self, lst, boolean, **kwargs):
        front = lst('frontmatter', optional=True)
        main = lst('mainmatter')
        extras = lst('extras', optional=True)

        dirs = front + main + extras

        dvips = set(lst('use_dvips', optional=True))

        unknown = sorted(dvips.difference(dirs))
        if unknown:
            raise ValueError(unknown)

        files = [os.path.join(self.config_dir, d, d + '.tex') for d in dirs]
        notfound = [f for f in files if not os.path.isfile(f)]
        if notfound:
            raise ValueError(notfound)

        self._groups = [(front, self._front_name),
            (main, self._main_name), (extras, self._extras_name)]
        self._dvips = dvips
        self._first_to_front = boolean('first_to_front')

    def _parse_template(self, string, **kwargs):
        self.template = self._get_path(string('filename', optional=True))
        self.template_two_up = self._get_path(
            string('filename_two_up', optional=True), self.template)

        self.documentclass = string('class')

        self.documentopts = {
            False: string('options', optional=True, default=''),
            True: string('options_two_up', optional=True, default=''),
        }

        self.includepdfopts = {
            False: string('include', optional=True, default=''),
            True: string('include_two_up', optional=True, default=''),
        }

    def _parse_substitute(self, items, **kwargs):
        self.context = {k: v.strip() for k, v in items()}

    def _parse_compile(self, string, **kwargs):
        split = lambda key: shlex.split(string(key, optional=True, default=''))
        self.compile_opts = {
            'latexmk': split('latexmk'),
            'texify': split('texify'),
            'dvips': split('dvips'),
            'ps2pdf': split('ps2pdf'),
        }

    def _parse_paginate(self, string, **kwargs):
        self.paginate_update = string('update')

        target = string('contents', optional=True)
        if target:
            self.paginate_target = os.path.join(target, '%s.tex' % target)
        else:
            self.paginate_target = ''

        self.paginate_replace = string('replace')

    def _iter_parts(self, groups):
        for parts, tmpl in groups:
            for i, part in enumerate(parts):
                context = {
                    'name': self.name,
                    'part': part,
                    'index0': i,
                    'index1': i + 1,
                }
                name = tmpl % context
                yield part, name

    def to_compile(self):
        for part, _ in self._iter_parts(self._groups):
            filename = '%s.tex' % part
            dvips = part in self._dvips
            yield self, part, filename, dvips

    def to_update(self):
        mainmatter = self._groups[1][0]
        parts = mainmatter[1:] if self._first_to_front else mainmatter
        for part in parts:
            source = os.path.join(part, '%s.tex' % part)
            pdf = os.path.join(part, '%s.pdf' % part)
            yield source, pdf

    def to_copy(self):
        for part, name in self._iter_parts(self._groups):
            source = os.path.join(part, '%s.pdf' % part)
            target = os.path.join(self.directory, tools.swapext(name, 'pdf'))
            yield source, target

    def to_combine(self):
        outname = self.name
        prelims = [name for _, name in self._iter_parts(self._groups[:1])]
        filenames = [name for _, name in self._iter_parts(self._groups[1:-1])]
        if self._first_to_front:
            prelims.append(filenames.pop(0))
        yield self, outname, self.template, prelims, filenames, False

        if self.make_two_up:
            outname = self.two_up
            prelims = []
            filenames = [name for _, name in self._iter_parts(self._groups[:-1])]
            yield self, outname, self.template_two_up, prelims, filenames, True
