# cleaning.py - remove intermediate and/or output files

import os
import shutil
from fnmatch import fnmatch

from . import jobs, tools

__all__ = ['clean']


def clean(config, clean_output=None):
    job = jobs.Job(config)
    with tools.chdir(job.config_dir):
        in_parts = list(matched_files(job.to_clean(), job.clean_parts))
        if job.clean_output or clean_output:
            in_output = list(output_files(job.directory))
            if not in_parts and not in_output:
                return
            print('\n'.join(in_parts))
            print('\n'.join(in_output))
            msg = ('...delete %d files matched in parts and %d files '
                'removing %s?' % (len(in_parts), len(in_output), job.directory))
            if tools.confirm(msg):
                remove(in_parts, job.directory)
        elif in_parts:
            print('\n'.join(in_parts))
            if tools.confirm('...delete %d files matched in parts?' % len(in_parts)):
                remove(in_parts)


def matched_files(dirs, patterns):
    for d in dirs:
        if os.path.isabs(d):
            raise ValueError('non-relative path: %r' % d)

        for f in sorted(os.listdir(d)):
            path = os.path.join(d, f)
            if not os.path.isfile(path):
                continue

            if any(fnmatch(f, p) for p in patterns):
                yield path


def output_files(directory):
    if os.path.isabs(directory):
        raise ValueError('non-relative path: %r' % directory)

    for root, dirs, files in os.walk(directory):
        for f in sorted(files):
            yield os.path.join(root, f)


def remove(files, directory=None):
    for f in files:
        os.remove(f)
    if directory is not None:
        shutil.rmtree(directory)
