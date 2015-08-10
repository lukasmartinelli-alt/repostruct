#!/usr/bin/env python
"""
Fetch filepaths by cloning them and counting the paths.
This is faster than accessing the repo via API!

Usage:
    fetch-filepaths.py [--rabbitmq]
    fetch-filepaths.py (-h | --help)

Options:
    -h --help    Show this screen
    --rabbitmq   Use RabbitMQ for distributing jobs
"""
import sys
import os
import json
import traceback
import csv
import shutil
import subprocess
import tempfile
from contextlib import contextmanager

import pika
from docopt import docopt
from rabbitmq import (durable_publish, reject, configure_rabbitmq,
                      METADATA_QUEUE, GIT_ERROR_QUEUE,
                      FILEPATHS_QUEUE, FAILED_QUEUE, GIT_TIMEOUT_QUEUE)


GIT_CLONE_TIMEOUT = int(os.getenv('GIT_CLONE_TIMEOUT', '120'))


class Repo(object):
    """A repository on Github"""
    def __init__(self, name):
        self.name = name

    def url(self):
        return "https://nouser:nopass@github.com/" + self.name + ".git"


@contextmanager
def clone(repo):
    """
    Clone a repository into a temporary directory which gets cleaned
    up afterwards.  This only makes a shallow clone of the last revision
    to save bandwidth.
    """
    temp_dir = tempfile.mkdtemp(suffix=repo.name.split("/")[1])

    with open(os.devnull, "w") as FNULL:
        subprocess.check_call(["git", "clone", "-q", "--depth", "1",
                              repo.url(), temp_dir],
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
                writer.writerow([repo.name, filepath])
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

        def error_body(err):
            return json.dumps({
                "repo": repo.name,
                "error": str(err)
            })

        try:
            filepaths = analyze_repo_structure(repo)
            for filepath in filepaths:
                writer.writerow([repo.name, filepath])

            payload = {
                "repo": repo.name,
                "filepaths": filepaths,
                "metadata": metadata
            }
            durable_publish(channel, FILEPATHS_QUEUE, json.dumps(payload))
            print('Published filepaths for {}'.format(repo.name))
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except subprocess.CalledProcessError as e:
            sys.stderr.write(str(e) + '\n')
            durable_publish(GIT_ERROR_QUEUE, error_body(e))
            reject(channel, method)
        except subprocess.TimeoutExpired as e:
            sys.stderr.write(str(e) + '\n')
            durable_publish(channel, GIT_TIMEOUT_QUEUE, error_body(e))
            reject(channel, method)
        except Exception as e:
            sys.stderr.write(str(e) + '\n')
            durable_publish(channel, FAILED_QUEUE, error_body(e))
            reject(channel, method)

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
