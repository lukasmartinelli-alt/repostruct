#!/usr/bin/env python
"""
Read repos from stdin and enqueue them on
RabbitMQ queue.

Usage:
    rabbitmq-enqueue.py [--rabbitmq=<ampq-url>]
    rabbitmq-enqueue.py (-h | --help)

Options:
    -h --help               Show this screen
    --rabbitmq=<ampq-url>   Connection string for RabbitMQ
"""
import os
import sys
import json
from contextlib import contextmanager

from docopt import docopt
import pika

JOBS_QUEUE = 'repos:jobs'


if __name__ == '__main__':
    args = docopt(__doc__)
    rabbitmq_url = args['--rabbitmq']

    if rabbitmq_url:
        connection = pika.BlockingConnection(pika.URLParameters(rabbitmq_url))
        channel = connection.channel()
        channel.queue_declare(queue=JOBS_QUEUE, durable=True)

        def publish(repo_name):
            body = {
                "repo": repo_name
            }
            channel.basic_publish(exchange='', routing_key=JOBS_QUEUE,
                                  body=json.dumps(body))

        for line in sys.stdin:
            repo_name = line.strip()
            if repo_name:
                publish(repo_name)
