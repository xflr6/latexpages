# numbering.py - update start pages, update table of contents (8-bit safe)

import re
import errno
import string
import subprocess

from ._compat import zip

from . import jobs, tools

__all__ = ['paginate']

NPAGES = re.compile(r'^NumberOfPages: (\d+)', re.MULTILINE)
AUTHOR = re.compile(r'\\author\{([^}]*)\}'.encode('ascii'))
TITLE = re.compile(r'\\title\{([^}]*)\}'.encode('ascii'))


def paginate(config):
    """Compute and update start page numbers as instructed in config file."""
    job = jobs.Job(config)
    with tools.chdir(job.config_dir):
        parts = list(job.to_update())
        updated, pages = startpages(job.paginate_update, parts)
        if job.paginate_template:
            contexts = list(template_contexts(parts, pages))
            changed = write_contents_template(job.paginate_target, job.paginate_replace,
                                              job.paginate_template, contexts)
        else:
            changed = write_contents(job.paginate_target, job.paginate_replace,
                                     pages)
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
        end = match.end(1) - match.start(0)
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


def npages(filename, pattern=NPAGES):
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
    if match is None:
        raise RuntimeError
    return int(match.group(1))


def write_contents(filename, pattern, pages, verbose=True):
    if not filename:
        return False

    pattern = re.compile(pattern.encode('ascii'))

    with open(filename, 'rb') as fd:
        old = fd.read()

    def repl_func(match, pg=iter(pages)):
        start = match.start(1) - match.start(0)
        end = match.end(1) - match.start(0)
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


def template_contexts(parts, pages, pat_author=AUTHOR, pat_title=TITLE):
    assert len(parts) == len(pages)
    for (source, pdf), startpage in zip(parts, pages):
        with open(source, 'rb') as fd:
            data = fd.read()
        author = title = ''.encode('ascii')
        for ma in pat_author.finditer(data):
            author = ma.group(1)
        for ma in pat_title.finditer(data):
            title = ma.group(1)
        yield {
            'author': author,
            'title':  title,
            'startpage': startpage,
        }


def write_contents_template(filename, pattern, template, contexts, verbose=True):
    if not filename:
        return False

    pattern = re.compile(pattern.encode('ascii'), re.DOTALL)

    with open(filename, 'rb') as fd:
        old = fd.read()

    substitute = string.Template(template.encode('ascii')).safe_substitute
    repl = '\n'.join(substitute(c) for c in contexts)

    def repl_func(match):
        start = match.start(1) - match.start(0)
        end = match.end(1) - match.start(0)
        group = match.group(0)
        result = group[:start] + repl + group[end:]
        if verbose:
            print('%s\t%s' % (filename, result.decode('ascii')))
        return result

    new, subbed = pattern.subn(repl_func, old, 1)
    if not subbed:
        raise RuntimeError

    if new != old:
        with open(filename, 'wb') as fd:
            fd.write(new)
        return True
    else:
        return False
