#!/usr/bin/env python
"""
Fetch repo and write directory structure

Usage:
    repostruct.py [-t THREADS]
    repostruct.py (-h | --help)

Options:
    -h --help         Show this screen
    -t THREADS        How many threads to use in ThreadPool [default: 4]
"""
import os
import sys
import tempfile
import shutil
import subprocess
from contextlib import contextmanager
from multiprocessing.dummy import Pool as ThreadPool

from docopt import docopt


class Repo(object):
    """A repository on Github"""
    def __init__(self, name):
        self.name = name

    def url(self):
        return "https://nouser:nopass@github.com/" + self.name + ".git"


@contextmanager
def clone(repo):
    """Clone a repository into a temporary directory which gets cleaned
    up afterwards"""
    temp_dir = tempfile.mkdtemp(suffix=repo.name.split("/")[1])

    with open(os.devnull, "w") as FNULL:
        subprocess.check_call(["git", "clone", "-q", repo.url(), temp_dir],
                              stdout=FNULL, stderr=subprocess.STDOUT)
    yield temp_dir
    shutil.rmtree(temp_dir)


def file_structure(repo_path):
    """Returns all relative file paths and filesize of a directory"""
    for path, dirs, files in os.walk(repo_path):
        for f in files:
            full_path = os.path.join(path, f)
            rel_path = os.path.relpath(full_path, repo_path)
            filesize = os.path.getsize(full_path)
            if not rel_path.startswith('.git'):
                yield rel_path, filesize


def write_repo_structure(repo):
    """
    Clone repo locally and write repo name, relative filepath and
    filesize to stdout.
    """
    try:
        with clone(repo) as repo_path:
            file_paths = list(file_structure(repo_path))

            for path, filesize in file_paths:
                sys.stdout.write("{0} {1} {2}\n"
                                 .format(repo.name, path, filesize))
            return file_paths
    except Exception as e:
        sys.stderr.write(str(e) + '\n')
        return []


def fetch_jobs_stdin():
    for line in sys.stdin:
        yield Repo(line.strip())


if __name__ == '__main__':
    args = docopt(__doc__)
    thread_count = int(args["-t"])
    with ThreadPool(thread_count) as pool:
        jobs = fetch_jobs_stdin()
        pool.map(write_repo_structure, jobs)
        pool.close()
        pool.join()
