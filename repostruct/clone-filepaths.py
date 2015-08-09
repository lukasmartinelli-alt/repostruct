#!/usr/bin/env python
"""
Fetch filepaths.

Usage:
    fetch-filepaths.py [--rabbitmq]
    fetch-filepaths.py (-h | --help)

Options:
    -h --help    Show this screen
    --rabbitmq   Use RabbitMQ for distributing jobs
"""
import sys
import time
import os
import json
import traceback
import csv
import shutil
import subprocess
import tempfile
from contextlib import contextmanager

import requests
import pika
from docopt import docopt
from lxml import html
from rabbitmq import (configure_rabbitmq, METADATA_QUEUE, GIT_ERROR_QUEUE,
                      FILEPATHS_QUEUE, FAILED_QUEUE, GIT_TIMEOUT_QUEUE)


GIT_CLONE_TIMEOUT = 10


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

            if not rel_path.startswith('.git'):
                yield rel_path


def analyze_repo_structure(repo):
    """
    Clone repo locally and write repo name, relative filepath and
    filesize to stdout.
    """
    with clone(repo) as repo_path:
        return list(file_structure(repo_path))


def process_jobs_stdin():
    writer = csv.writer(sys.stdout, delimiter=' ', quoting=csv.QUOTE_ALL)
    for line in sys.stdin:
        repo = Repo(line.strip())

        try:
            filepaths = analyze_repo_structure(repo)

            for filepath in filepaths:
                writer.writerow([
                    repo.name,
                    filepath
                ])
        except Exception as e:
            print(traceback.format_exc(), file=sys.stderr)


def process_jobs_rabbitmq(rabbitmq_url):
    connection = pika.BlockingConnection(pika.URLParameters(rabbitmq_url))
    channel = connection.channel()
    channel.basic_qos(prefetch_count=1)
    configure_rabbitmq(channel)
    writer = csv.writer(sys.stdout, delimiter=' ', quoting=csv.QUOTE_ALL)

    def callback(ch, method, properties, body):
        body = json.loads(body.decode('UTF-8'))
        repo = Repo(body['repo'])
        metadata = body['metadata']

        def publish(queue, body):
            ch.basic_publish(exchange='', routing_key=queue, body=body,
                             properties=pika.BasicProperties(
                                delivery_mode = 2
                             ))

        def reject():
            ch.basic_reject(delivery_tag=method.delivery_tag, requeue=False)

        def error_body(err):
            return json.dumps({
                "repo": repo.name,
                "error": str(err)
            })

        try:
            url = 'https://github.com/' + repo
            filepaths = analyze_repo_structure(repo, url)
            for filepath in filepaths:
                writer.writerow([
                    repo.name,
                    filepath
                ])

            payload = {
                "repo": repo,
                "filepaths": filepaths,
                "metadata": metadata
            }
            print('Published filepaths for {}'.format(repo))
            publish(FILEPATHS_QUEUE, json.dumps(payload))
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


    channel.basic_consume(callback, queue=METADATA_QUEUE)

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()

    connection.close()

if __name__ == '__main__':
    args = docopt(__doc__)

    if args['--rabbitmq']:
        rabbitmq_url = os.getenv('RABBITMQ_URL')
        if not rabbitmq_url:
            sys.exit('You need to specify the RABBITMQ_URL env var')
        process_jobs_rabbitmq(rabbitmq_url)
    else:
        process_jobs_stdin()
