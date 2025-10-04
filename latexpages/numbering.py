"""Update start pages, update table of contents (8-bit safe)."""

import os
import re
import string

from . import backend
from . import jobs
from . import tools

__all__ = ['paginate']


def paginate(config) -> bool:
    """Compute and update start page numbers as instructed in config file."""
    job = jobs.Job(config)
    with tools.chdir(job.config_dir):
        parts = list(job.to_update())
        updated, pages = startpages(job.paginate_update, parts)
        if job.paginate_template:
            contexts = list(template_contexts(parts, pages,
                                              job.paginate_author_extract,
                                              job.paginate_title_extract))
            changed = write_contents_template(job.paginate_target, job.paginate_replace,
                                              job.paginate_template, contexts)
        else:
            changed = write_contents(job.paginate_target, job.paginate_replace,
                                     pages)
    return updated or changed


def startpages(pattern: str, parts):
    npages = backend.Npages.get_func()
    pattern = re.compile(pattern.encode('ascii'))
    modified = False
    result = []
    thepage = 1
    for source, pdf in parts:
        repl = (f'{thepage:d}').encode('ascii')
        differed = replace(source, pattern, repl)
        if differed:
            modified = True
        result.append(thepage)
        thepage += npages(pdf)
    return modified, result


def replace(filename: os.PathLike[str] | str, pattern: str, repl: str, *,
            verbose: bool = True) -> bool:
    with open(filename, 'rb') as fd:
        old = fd.read()

    def repl_func(match):
        start = match.start(1) - match.start(0)
        end = match.end(1) - match.start(0)
        group = match.group(0)
        result = group[:start] + repl + group[end:]
        if verbose:
            print(filename, result.decode('ascii'), sep='\t')
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


def write_contents(filename: str, pattern: str, pages, *,
                   verbose: bool = True) -> bool:
    if not filename:
        return False

    pattern = re.compile(pattern.encode('ascii'))

    with open(filename, 'rb') as fd:
        old = fd.read()

    def repl_func(match, pg=iter(pages)):
        start = match.start(1) - match.start(0)
        end = match.end(1) - match.start(0)
        group = match.group(0)
        repl = (f'{next(pg):d}').encode('ascii')
        result = group[:start] + repl + group[end:]
        if verbose:
            print(filename, result.decode('ascii'), sep='\t')
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


def template_contexts(parts, pages, author_extract, title_extract, *,
                      encoding: str = 'utf-8'):
    assert len(parts) == len(pages)
    assert author_extract and title_extract
    pat_author = re.compile(author_extract)
    pat_title = re.compile(title_extract)
    for (source, pdf), startpage in zip(parts, pages, strict=True):
        with open(source, encoding=encoding) as fd:
            data = fd.read()
        author = title = ''
        for ma in pat_author.finditer(data):
            author = ma.group(1)
        for ma in pat_title.finditer(data):
            title = ma.group(1)
        yield {'author': author,
               'title': title,
               'startpage': startpage}


def write_contents_template(filename: str, pattern: str, template, contexts, *,
                            encoding: str = 'utf-8',
                            verbose: bool = True) -> bool:
    if not filename:
        return False

    pattern = re.compile(pattern, re.DOTALL)

    with open(filename, encoding=encoding) as fd:
        old = fd.read()

    substitute = string.Template(template).safe_substitute
    repl = '\n'.join(substitute(c) for c in contexts)

    def repl_func(match):
        start = match.start(1) - match.start(0)
        end = match.end(1) - match.start(0)
        group = match.group(0)
        result = group[:start] + repl + group[end:]
        if verbose:
            print(filename, result, sep='\t')
        return result

    new, subbed = pattern.subn(repl_func, old, 1)
    if not subbed:
        raise RuntimeError

    if new != old:
        with open(filename, 'w', encoding=encoding) as fd:
            fd.write(new)
        return True
    else:
        return False
