"""Remove intermediate and/or output files."""

from collections.abc import Iterable, Iterator, Sequence
import fnmatch
import functools
import os
import shutil

from . import jobs
from . import tools

__all__ = ['clean']


def clean(config, *, clean_output: bool | None = None) -> None:
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
                remove(in_parts, directory=job.directory)
        elif in_parts:
            print('\n'.join(in_parts))
            if tools.confirm(f'...delete {len(in_parts)} files matched in parts?'):
                remove(in_parts)


def matched_files(dirs: Sequence[os.PathLike[str] | str],
                  patterns: Sequence[str],
                  except_patterns: Sequence[str]) -> Iterator[str]:
    for d in dirs:
        if os.path.isabs(d):
            raise ValueError(f'non-relative path: {d!r}')

        for f in sorted(os.listdir(d)):
            path = os.path.join(d, f)
            if not os.path.isfile(path):
                continue

            path_matches = functools.partial(fnmatch.fnmatch, path)
            match = (any(map(path_matches, patterns))
                     and not any(map(path_matches, except_patterns)))
            if match:
                yield path


def output_files(directory: os.PathLike[str] | str) -> Iterator[str]:
    if os.path.isabs(directory):
        raise ValueError(f'non-relative path: {directory!r}')

    for root, dirs, files in os.walk(directory):
        for f in sorted(files):
            yield os.path.join(root, f)


def remove(files: Sequence[os.PathLike[str] | str], *,
           directory: os.PathLike[str] | str | None = None) -> None:
    for f in files:
        os.remove(f)
    if directory is not None:
        shutil.rmtree(directory)
