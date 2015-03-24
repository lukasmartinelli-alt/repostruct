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
from multiprocessing.dummy import Pool as ThreadPool

from redis import Redis
from docopt import docopt

from repo import clone, GitRepo


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
                sys.stdout.write(local_repo.name + " " + path + "\n")

            return file_paths
    except Exception as e:
        sys.stderr.write(str(e) + '\n')
        return []


def fetch_jobs_stdin():
    for line in sys.stdin:
        yield GitRepo(line.strip())


def fetch_jobs_redis(redis, list_name):
    while redis.llen(list_name) > 0:
        repo_name = redis.lpop(list_name).decode("utf-8")
        yield GitRepo(repo_name)


if __name__ == '__main__':
    args = docopt(__doc__)
    thread_count = int(args["-t"])
    if args["--rq"]:
        list_name = args["--rq"]
        redis = Redis(host=os.environ.get("RQ_HOST", "localhost"),
                      port=os.environ.get("RQ_PORT", "6379"))
        for repo in fetch_jobs_redis(redis, list_name):
            analyze_repo(repo)
    else:
        with ThreadPool(thread_count) as pool:
            jobs = fetch_jobs_stdin()
            pool.map(analyze_repo, jobs)
            pool.close()
            pool.join()
