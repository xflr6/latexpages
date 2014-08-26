# render.py - compile latex to PDF, optionally open in viewer

import sys
import os
import errno
import subprocess

from ._compat import apply

from . import tools

__all__ = ['compile']

OPTS = {
    'latexmk': ['-silent'],
    'texify': ['--batch', '--verbose', '--quiet'],
    'dvvips': ['-q'],
    'ps2pdf': [],
}


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
            subprocess.Popen(latexmk).wait()
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
            subprocess.Popen(texify).wait()
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
            subprocess.Popen(dvips).wait()

            ps2pdf = ['ps2pdf'] + options['ps2pdf']
            ps2pdf.append(tools.swapext(filename, 'ps'))
            subprocess.Popen(ps2pdf).wait()


@apply
def default_compile(platform=sys.platform):
    compile_funcs = {
        'darwin': latexmk_compile,
        'linux2': latexmk_compile,
        'win32': texify_compile,
    }
    return compile_funcs.get(platform, no_compile)
