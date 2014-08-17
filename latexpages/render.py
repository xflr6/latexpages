# render.py - compile latex to PDF, optionally open in viewer

import sys
import os
import subprocess

from ._compat import apply

from . import tools

__all__ = ['compile']


def compile(filename, dvips=False, view=False, engine=None):
    """Compile LaTeX file to PDF using either latexmk.pl or texify.exe."""
    compile_funcs = {
        'latexmk': latexmk_compile,
        'texify': texify_compile,
        None: default_compile,
    }
    compile_funcs[engine](filename, dvips, view)


def no_compile(filename, view=False):
    raise NotImplementedError('platform not supported')


def latexmk_compile(filename, dvips=False, view=False):
    """Compile LaTeX file with the latexmk perl script."""
    compile_dir, filename = os.path.split(filename)

    latexmk = ['latexmk', '-silent']
    if dvips:
        latexmk += ['-dvi', '-ps', '-pdfps']
    else:
        latexmk.append('-pdf')
    if view:
        latexmk.append('-pv')
    latexmk.append(filename)

    with tools.chdir(compile_dir):
        subprocess.Popen(latexmk).wait()


def texify_compile(filename, dvips=False, view=False):
    """Compile LaTeX file using MikTeX's texify utility."""
    compile_dir, filename = os.path.split(filename)

    texify = ['texify', '--batch', '--verbose', '--quiet']
    if not dvips:
        texify.append('--pdf')
    if view:
        texify.append('--run-viewer')
    texify.append(filename)

    with tools.chdir(compile_dir):
        subprocess.Popen(texify).wait()

        if dvips:
            dvips = ['dvips', '-P', 'pdf', '-q']
            dvips.append(tools.swapext(filename, 'dvi'))
            subprocess.Popen(dvips).wait()

            ps2pdf = ['ps2pdf', tools.swapext(filename, 'ps')]
            subprocess.Popen(ps2pdf).wait()


@apply
def default_compile(platform=sys.platform):
    compile_funcs = {
        'darwin': latexmk_compile,
        'linux2': latexmk_compile,
        'win32': texify_compile,
    }
    return compile_funcs.get(platform, no_compile)
