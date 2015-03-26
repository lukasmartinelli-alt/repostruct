#!/usr/bin/env python
"""
Fetch repo and write directory structure

Usage:
    repostruct.py [-t THREADS] [--rq=<list_name>]
    repostruct.py (-h | --help)

Options:
    -h --help         Show this screen
    -t THREADS        How many threads to use in ThreadPool [default: 4]
    --rq=<list_name>  Read input from redis list
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
    """Returns all relative file paths of a directory"""
    for path, dirs, files in os.walk(repo_path):
        for f in files:
            full_path = os.path.join(path, f)
            rel_path = os.path.relpath(full_path, repo_path)
            if not rel_path.startswith('.git'):
                yield rel_path


def write_repo_structure(repo):
    try:
        with clone(repo) as local_repo:
            file_paths = list(file_structure(local_repo.dir))

            for path in file_paths:
                sys.stdout.write(local_repo.name + " " + path + "\n")

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
