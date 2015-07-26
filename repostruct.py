#!/usr/bin/env python
"""
Fetch repo and write directory structure

Usage:
    repostruct.py [--rabbitmq=<ampq-url>]
    repostruct.py (-h | --help)

Options:
    -h --help               Show this screen
    --rabbitmq=<ampq-url>   Connection string for RabbitMQ 
"""
import os
import sys
import tempfile
import shutil
import subprocess
from contextlib import contextmanager
from multiprocessing.dummy import Pool as ThreadPool

from docopt import docopt
import pika

from .rabbitmq import configure_rabbitmq


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


def configure_rabbitmq(channel):

    def queue_declare(queue)
        return channel.queue_declare(queue=queue, durable=True)

    queue_declare(JOBS_QUEUE)
    queue_declare(FAILED_QUEUE)
    queue_declare(DELETED_QUEUE)
    queue_declare(TOO_BIG_QUEUE)


def file_structure(repo_path):
    """Returns all relative file paths and filesize of a directory"""
    for path, dirs, files in os.walk(repo_path):
        for f in files:
            full_path = os.path.join(path, f)
            rel_path = os.path.relpath(full_path, repo_path)

            try:
                filesize = os.path.getsize(full_path)
            except Exception:
                filesize = 0

            if not rel_path.startswith('.git'):
                yield rel_path, filesize


def write_repo_structure(repo):
    """
    Clone repo locally and write repo name, relative filepath and
    filesize to stdout.
    """
    with clone(repo) as repo_path:
        file_paths = list(file_structure(repo_path))

        for path, filesize in file_paths:
            sys.stdout.write("{0} {1} {2}\n"
                             .format(repo.name, path, filesize))
        return file_paths


def process_jobs_stdin():
    for line in sys.stdin:
        repo = Repo(line.strip())

        try:
            write_repo_structure(repo)
        except Exception as e:
            sys.stderr.write(str(e) + '\n')


def process_jobs_rabbitmq(rabbitmq_url):
    connection = pika.BlockingConnection(pika.URLParameters(rabbitmq_url))
    channel = connection.channel()
    configure_rabbitmq(channel)

    def callback(ch, method, properties, body):
        repo = Repo(body)

        try:
            write_repo_structure(repo)
        except Exception as e:
            channel.basic_publish(exchange='', routing_key=FAILED_QUEUE,
                                  body=repo.name)

        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(callback, queue=JOBS_QUEUE)
    channel.start_consuming()


if __name__ == '__main__':
    args = docopt(__doc__)
    rabbitmq_url = args['<ampq-url>']

    if rabbitmq_url:
        process_jobs_rabbitmq(rabbitmq_url)
    else:
        process_jobs_stdin()
