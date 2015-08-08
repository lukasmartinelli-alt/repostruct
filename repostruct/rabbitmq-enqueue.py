#!/usr/bin/env python
"""
Read repos from stdin and enqueue them on
RabbitMQ queue.

Usage:
    rabbitmq-enqueue.py
    rabbitmq-enqueue.py (-h | --help)

Options:
    -h --help               Show this screen
"""
import os
import sys
import json
from contextlib import contextmanager

from docopt import docopt
import pika

from rabbitmq import configure_rabbitmq, REPOS_QUEUE


if __name__ == '__main__':
    args = docopt(__doc__)

    rabbitmq_url = os.getenv('RABBITMQ_URL')
    if not rabbitmq_url:
        sys.exit('You need to specify the RABBITMQ_URL env var')
    connection = pika.BlockingConnection(pika.URLParameters(rabbitmq_url))
    channel = connection.channel()
    configure_rabbitmq(channel)

    def publish(repo_name):
        body = {
            "repo": repo_name
        }
        channel.basic_publish(exchange='', routing_key=REPOS_QUEUE,
                              body=json.dumps(body),
                              properties=pika.BasicProperties(
                                delivery_mode = 2     
                              ))

    for line in sys.stdin:
        repo_name = line.strip()
        if repo_name:
            publish(repo_name)
            print(repo_name)
