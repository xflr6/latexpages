# cleaning.py - remove intermediate and/or output files

from fnmatch import fnmatch
import os
import shutil

from . import jobs
from . import tools

__all__ = ['clean']


def clean(config, clean_output=None):
    job = jobs.Job(config)
    with tools.chdir(job.config_dir):
        in_parts = list(matched_files(job.to_clean(), job.clean_parts, job.clean_except))
        if job.clean_output or clean_output:
            in_output = list(output_files(job.directory))
            if not in_parts and not in_output:
                return
            print('\n'.join(in_parts))
            print('\n'.join(in_output))
            msg = (f'...delete {len(in_parts)} files matched in parts'
                   f' and {len(in_output)} files removing {job.directory}?')
            if tools.confirm(msg):
                remove(in_parts, job.directory)
        elif in_parts:
            print('\n'.join(in_parts))
            if tools.confirm(f'...delete {len(in_parts)} files matched in parts?'):
                remove(in_parts)


def matched_files(dirs, patterns, except_patterns):
    for d in dirs:
        if os.path.isabs(d):
            raise ValueError(f'non-relative path: {d!r}')

        for f in sorted(os.listdir(d)):
            path = os.path.join(d, f)
            if not os.path.isfile(path):
                continue

            match = any(fnmatch(path, p) for p in patterns)
            match = match and not any(fnmatch(path, e) for e in except_patterns)
            if match:
                yield path


def output_files(directory):
    if os.path.isabs(directory):
        raise ValueError(f'non-relative path: {directory!r}')

    for root, dirs, files in os.walk(directory):
        for f in sorted(files):
            yield os.path.join(root, f)


def remove(files, directory=None):
    for f in files:
        os.remove(f)
    if directory is not None:
        shutil.rmtree(directory)
