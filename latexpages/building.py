# building.py - compile parts, copy to output, combine, combine two_up

import multiprocessing
import os
import shutil

from . import backend
from . import jobs
from . import pdfpages
from . import tools

__all__ = ['make']


def make(config, *, processes=None, engine=None, cleanup=True, only=None):
    """Compile parts, copy, and combine as instructed in config file."""
    job = jobs.Job(config, processes=processes, engine=engine, cleanup=cleanup)

    if only is not None:
        args = job.to_compile_only(only)
        compile_part(args)
        return

    pool_cls = multiprocessing.Pool if job.processes != 1 else tools.NullPool
    pool = pool_cls(job.processes, tools.ignore_sigint)

    try:
        pool.map(compile_part, job.to_compile(), chunksize=1)
        copy_parts(job)
        pool.map(combine_parts, job.to_combine(), chunksize=1)
    except KeyboardInterrupt:  # https://bugs.python.org/issue8296
        pool.terminate()
    else:
        pool.close()
    finally:
        pool.join()


def compile_part(args):
    """Compile part LaTeX document to PDF."""
    job, part, filename, dvips = args
    with tools.chdir(job.config_dir, part):
        backend.compile(filename, dvips=dvips, engine=job.engine,
                        options=job.compile_opts)


def copy_parts(job):
    """Copy part PDFs to the output directory."""
    with tools.chdir(job.config_dir):
        if not os.path.isdir(job.directory):
            os.mkdir(job.directory)
        for source, target in job.to_copy():
            shutil.copyfile(source, target)


def combine_parts(args):
    """Combine output PDFs with pdfpages."""
    job, outname, template, prelims, filenames, two_up = args
    with tools.chdir(job.config_dir, job.directory):
        document = pdfpages.Source(prelims, filenames,
                                   context=job.context, template=template,
                                   includepdfopts=job.includepdfopts,
                                   documentclass=job.documentclass,
                                   documentopts=job.documentopts)
        document.render(tools.swapext(outname, 'tex'),
                        two_up=two_up, engine=job.engine,
                        options=job.compile_opts, cleanup=job.cleanup)
