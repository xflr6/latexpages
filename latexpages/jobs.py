# jobs.py - parse .ini-style config file into function call args

import os

from ._compat import ConfigParser

from . import tools

__all__ = ['Job']


class Job(object):
    """INI-file giving the document collection parts and how to combine them."""

    _defaults = tools.current_path('settings.ini')

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

    def __init__(self, filename, engine=None, cleanup=True):
        cfg = ConfigParser()
        if not os.path.exists(filename):
            raise ValueError('file not found: %r' % filename)
        parsed = cfg.read([self._defaults, filename])
        assert len(parsed) == 2

        self.config_dir = os.path.dirname(filename)

        string, lst = self._get_string, self._get_list

        self.name = string(cfg, 'make', 'name')
        self.directory = string(cfg, 'make', 'directory')
        self.two_up = string(cfg, 'make', 'two_up', optional=True)
        self.make_two_up = cfg.getboolean('make', 'make_two_up')

        front = lst(cfg, 'parts', 'frontmatter', optional=True)
        front_name = string(cfg, 'make', 'frontmatter')

        main = lst(cfg, 'parts', 'mainmatter')
        main_name = string(cfg, 'make', 'mainmatter')

        extras = lst(cfg, 'parts', 'extras', optional=True)
        extras_name = string(cfg, 'make', 'extras')

        dvips = set(lst(cfg, 'parts', 'use_dvips', optional=True))

        dirs = front + main + extras
        unknown = sorted(dvips.difference(dirs))
        if unknown:
            raise ValueError(unknown)
        files = [os.path.join(self.config_dir, d, d + '.tex') for d in dirs]
        notfound = [f for f in files if not os.path.isfile(f)]
        if notfound:
            raise ValueError(notfound)

        self._groups = [(front, front_name), (main, main_name), (extras, extras_name)]
        self._dvips = dvips
        self._first_to_front = cfg.getboolean('parts', 'first_to_front')

        template = string(cfg, 'template', 'filename', optional=True)
        if template:
            template = os.path.realpath(template)
        self.template = template

        self.documentclass = string(cfg, 'template', 'class')
        self.documentopts = {
            False: string(cfg, 'template', 'options', optional=True, default=''),
            True: string(cfg, 'template', 'options_two_up', optional=True, default=''),
        }

        self.includepdfopts = {
            False: string(cfg, 'template', 'include', optional=True, default=''),
            True: string(cfg, 'template', 'include_two_up', optional=True, default=''),
        }

        self.context = {k: v.strip() for k, v in cfg.items('substitute')}

        self.engine = engine
        self.cleanup = cleanup

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
        yield self, outname, prelims, filenames, False

        if self.make_two_up:
            outname = self.two_up
            prelims = []
            filenames = [name for _, name in self._iter_parts(self._groups[:-1])]
            yield self, outname, prelims, filenames, True
