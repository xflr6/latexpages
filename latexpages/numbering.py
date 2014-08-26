# numbering.py - update start pages, update table of contents (8-bit safe)

import re
import errno
import subprocess

from . import jobs, tools

__all__ = ['paginate']

NPAGES = r'^NumberOfPages: (\d+)'


def paginate(config):
    """Compute and update start page numbers as instructed in config file."""
    job = jobs.Job(config)
    with tools.chdir(job.config_dir):
        updated, pages = startpages(job.paginate_update, job.to_update())
        changed = write_contents(job.paginate_target, job.paginate_replace, pages)
    return updated or changed


def startpages(pattern, parts):
    pattern = re.compile(pattern.encode('ascii'))
    modified = False
    result = []
    thepage = 1
    for source, pdf in parts:
        repl = ('%d' % thepage).encode('ascii')
        differed = replace(source, pattern, repl)
        if differed:
            modified = True
        result.append(thepage)
        thepage += npages(pdf)
    return modified, result


def replace(filename, pattern, repl, verbose=True):
    with open(filename, 'rb') as fd:
        old = fd.read()

    def repl_func(match):
        start = match.start(1) - match.start(0)
        end = match.end(1) - match.end(0)
        group = match.group(0)
        result = group[:start] + repl + group[end:]
        if verbose:
            print('%s\t%s' % (filename, result.decode('ascii')))
        return result

    new, subn = pattern.subn(repl_func, old, 1)
    if not subn:
        raise RuntimeError

    if new != old:
        with open(filename, 'wb') as fd:
            fd.write(new)
        return True
    else:
        return False


def npages(filename, pattern=re.compile(NPAGES, re.MULTILINE)):
    """Return the number of pages of a PDF by asking pdftk."""
    pdftk = ['pdftk', filename, 'dump_data']
    try:
        metadata = subprocess.check_output(pdftk, universal_newlines=True)
    except OSError as e:
        if e.errno == errno.ENOENT:
            raise RuntimeError('failed to execute %r, '
                'make sure the pdftk executable '
                'is on your systems\' path' % pdftk)
        else:
            raise

    match = pattern.search(metadata)
    if match:
        return int(match.group(1))
    else:
        raise RuntimeError


def write_contents(filename, pattern, pages, verbose=True):
    if not filename:
        return False

    pattern = re.compile(pattern.encode('ascii'))

    with open(filename, 'rb') as fd:
        old = fd.read()

    def repl_func(match, pg=iter(pages)):
        start = match.start(1) - match.start(0)
        end = match.end(1) - match.end(0)
        group = match.group(0)
        repl = ('%d' % next(pg)).encode('ascii')
        result = group[:start] + repl + group[end:]
        if verbose:
            print('%s\t%s' % (filename, result.decode('ascii')))
        return result

    new, subn = pattern.subn(repl_func, old)
    if subn != len(pages):
        raise RuntimeError

    if new != old:
        with open(filename, 'wb') as fd:
            fd.write(new)
        return True
    else:
        return False
