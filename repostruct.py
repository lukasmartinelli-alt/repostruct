#!/usr/bin/env python
"""
Fetch repo and write directory structure

Usage:
    repostruct.py [-t THREADS]
    repostruct.py [--rq]
    repostruct.py (-h | --help)

Options:
    -h --help         Show this screen
    -t THREADS        How many threads to use in ThreadPool [default: 4]
    --rq              Use Redis Queue from REPOSTRUCT_RQ env to fetch jobs
"""
import os
import sys
from multiprocessing.dummy import Pool as ThreadPool

from docopt import docopt

from rq import RedisQueue
from repo import clone, GitRepo

VERBOSE = "REPOSTRUCT_VERBOSE" in os.environ


def file_structure(repo_path):
    for path, dirs, files in os.walk(repo_path):
        for f in files:
            full_path = os.path.join(path, f)
            rel_path = os.path.relpath(full_path, repo_path)
            if not rel_path.startswith('.git'):
                yield rel_path


def analyze_repo(repo):
    try:
        with clone(repo) as local_repo:
            file_paths = list(file_structure(local_repo.dir))

            for path in file_paths:
                sys.stdout.write(path + "\n")

            return file_paths
    except Exception as e:
        sys.stderr.write(str(e) + '\n')
        return []


def fetch_jobs_stdin():
    for line in sys.stdin:
        yield GitRepo(line.strip())


if __name__ == '__main__':
    args = docopt(__doc__)
    thread_count = int(args["-t"])

    if args["--rq"]:
        rq = RedisQueue.from_config()
        for repo in rq.fetch_jobs():
            analyze_repo(repo)
    else:
        with ThreadPool(thread_count) as pool:
            jobs = fetch_jobs_stdin()
            pool.map(analyze_repo, jobs)
            pool.close()
            pool.join()
