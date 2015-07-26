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
import json
import shutil
import subprocess
from contextlib import contextmanager

from docopt import docopt
import pika

GIT_CLONE_TIMEOUT = 10
RESULTS_QUEUE = 'repos:results'
JOBS_QUEUE = 'repos:jobs'
FAILED_QUEUE = 'repos:failed'
GIT_ERROR_QUEUE = 'repos:git_error'
GIT_TIMEOUT_QUEUE = 'repos:timeout'


def configure_rabbitmq(channel):

    def queue_declare(queue):
        return channel.queue_declare(queue=queue, durable=True)

    queue_declare(JOBS_QUEUE)
    queue_declare(RESULTS_QUEUE)
    queue_declare(FAILED_QUEUE)
    queue_declare(GIT_TIMEOUT_QUEUE)
    queue_declare(GIT_ERROR_QUEUE)


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
                              stdout=FNULL, stderr=subprocess.STDOUT,
                              timeout=GIT_CLONE_TIMEOUT)
    yield temp_dir
    shutil.rmtree(temp_dir)


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
        body = json.loads(body.decode('UTF-8'))
        repo = Repo(body['repo'])

        def publish(queue, body):
            ch.basic_publish(exchange='', routing_key=queue, body=body)

        def reject():
            ch.basic_reject(delivery_tag=method.delivery_tag, requeue=False)

        def error_body(err):
            return json.dumps({
                "repo": repo.name,
                "error": str(err)
            })

        try:
            file_paths = write_repo_structure(repo)
            payload = {
                "repo": repo.name,
                "file_paths": file_paths
            }
            ch.basic_publish(exchange='', routing_key=RESULTS_QUEUE,
                             body=json.dumps(payload))
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except subprocess.CalledProcessError as e:
            sys.stderr.write(str(e) + '\n')
            publish(GIT_ERROR_QUEUE, error_body(e))
            reject()
        except subprocess.TimeoutExpired as e:
            sys.stderr.write(str(e) + '\n')
            publish(GIT_TIMEOUT_QUEUE, error_body(e))
            reject()
        except Exception as e:
            sys.stderr.write(str(e) + '\n')
            publish(FAILED_QUEUE, error_body(e))
            reject()


    channel.basic_consume(callback, queue=JOBS_QUEUE)
    channel.start_consuming()


if __name__ == '__main__':
    args = docopt(__doc__)
    rabbitmq_url = args['--rabbitmq']

    if rabbitmq_url:
        process_jobs_rabbitmq(rabbitmq_url)
    else:
        process_jobs_stdin()
