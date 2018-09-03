# backend.py - compile LaTeX to PDF, optionally open in viewer, count PDF pages

import os
import re
import errno
import platform
import subprocess

from ._compat import apply

from . import tools

__all__ = ['compile', 'Npages']

PLATFORM = platform.system().lower()

OPTS = {
    'latexmk': ['-silent'],
    'texify': ['--batch', '--verbose', '--quiet'],
    'dvvips': ['-q'],
    'ps2pdf': [],
}


if PLATFORM == 'windows':
    def get_startupinfo():
        """Return subprocess.STARTUPINFO instance hiding the console window."""
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
        return startupinfo
else:
    def get_startupinfo():
        """Return None for startupinfo argument of ``subprocess.Popen``."""
        return None


def compile(filename, dvips=False, view=False, engine=None, options=None):
    """Compile LaTeX file to PDF using either latexmk.pl or texify.exe."""
    compile_funcs = {
        'latexmk': latexmk_compile,
        'texify': texify_compile,
        None: default_compile,
    }
    if engine not in compile_funcs:
        raise ValueError('unknown engine: %r' % (engine,))
    compile_funcs[engine](filename, dvips, view, options)


def no_compile(filename, dvips=False, view=False, options=None):
    raise NotImplementedError('platform not supported')


def latexmk_compile(filename, dvips=False, view=False, options=None):
    """Compile LaTeX file with the latexmk perl script."""
    compile_dir, filename = os.path.split(filename)

    if options is None:
        options = OPTS

    latexmk = ['latexmk'] + options['latexmk']
    if dvips:
        latexmk += ['-dvi', '-ps', '-pdfps']
    else:
        latexmk.append('-pdf')
    if view:
        latexmk.append('-pv')
    latexmk.append(filename)

    with tools.chdir(compile_dir):
        try:
            subprocess.call(latexmk, startupinfo=get_startupinfo())
        except OSError as e:
            if e.errno == errno.ENOENT:
                raise RuntimeError('failed to execute %r, '
                    'make sure the latexmk executable '
                    'is on your systems\' path' % latexmk)
            else:
                raise


def texify_compile(filename, dvips=False, view=False, options=None):
    """Compile LaTeX file using MikTeX's texify utility."""
    compile_dir, filename = os.path.split(filename)

    if options is None:
        options = OPTS

    texify = ['texify'] + options['texify']
    if not dvips:
        texify.append('--pdf')
    if view:
        texify.append('--run-viewer')
    texify.append(filename)

    with tools.chdir(compile_dir):
        try:
            subprocess.call(texify, startupinfo=get_startupinfo())
        except OSError as e:
            if e.errno == errno.ENOENT:
                raise RuntimeError('failed to execute %r, '
                    'make sure the MikTeX executables '
                    'are on your systems\' path' % texify)
            else:
                raise

        if dvips:
            dvips = ['dvips', '-P', 'pdf'] + options['dvips']
            dvips.append(tools.swapext(filename, 'dvi'))
            subprocess.call(dvips, startupinfo=get_startupinfo())

            ps2pdf = ['ps2pdf'] + options['ps2pdf']
            ps2pdf.append(tools.swapext(filename, 'ps'))
            subprocess.call(ps2pdf, startupinfo=get_startupinfo())


@apply
def default_compile(platform=PLATFORM):
    compile_funcs = {
        'darwin': latexmk_compile,
        'linux': latexmk_compile,
        'windows': texify_compile,
    }
    return compile_funcs.get(platform, no_compile)


class Npages(object):

    _cache = None

    @classmethod
    def get_func(cls):
        if cls._cache is not None:
            return cls._cache

        tried = []
        for subcls in cls.__subclasses__():
            try:
                subprocess.check_call(subcls.check_cmd, startupinfo=get_startupinfo())
            except OSError as e:
                if e.errno == errno.ENOENT:
                    tried.append(subcls.check_cmd)
                else:
                    raise
            except subprocess.CalledProcessError:
                raise RuntimeError
            else:
                break
        else:
            tried = ' and '.join(repr(check_cmd) for check_cmd in tried)
            raise RuntimeError('failed to execute %s, '
                'make sure the pdfinfo or pdftk executable '
                'is on your systems\' path' % tried)

        result = cls._cache = subcls()
        return result

    def __init__(self):
        self.pattern = re.compile(self.result_pattern, re.MULTILINE)

    def __call__(self, filename):
        """Return the number of pages of a PDF by asking pdfinfo/pdftk."""
        cmd = self.make_cmd(filename)
        try:
            result = subprocess.check_output(cmd,
                stderr=subprocess.STDOUT, startupinfo=get_startupinfo(),
                universal_newlines=True)
        except OSError as e:
            if e.errno == errno.ENOENT:
                raise RuntimeError('failed to execute %r, '
                    'make sure the pdfinfo or pdftk executable '
                    'is on your systems\' path' % cmd)
            else:
                raise

        match = self.pattern.search(result)
        if match is None:
            raise RuntimeError
        return int(match.group(1))


class PDFInfo(Npages):

    check_cmd = ['pdfinfo', '-v']
    make_cmd = staticmethod(lambda filename: ['pdfinfo', filename])
    result_pattern = r'^Pages: +(\d+)'


class PDFTk(Npages):

    check_cmd = ['pdftk', '--version']
    make_cmd = staticmethod(lambda filename: ['pdftk', filename, 'dump_data'])
    result_pattern = r'^NumberOfPages: (\d+)'
