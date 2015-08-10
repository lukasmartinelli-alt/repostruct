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

from docopt import docopt
import pika

from rabbitmq import configure_rabbitmq, durable_publish, REPOS_QUEUE


if __name__ == '__main__':
    args = docopt(__doc__)

    rabbitmq_url = os.getenv('RABBITMQ_URL')
    if not rabbitmq_url:
        sys.exit('You need to specify the RABBITMQ_URL env var')
    connection = pika.BlockingConnection(pika.URLParameters(rabbitmq_url))
    channel = connection.channel()
    configure_rabbitmq(channel)

    for line in sys.stdin:
        repo_name = line.strip()
        if repo_name:
            body = {
                "repo": repo_name
            }
            durable_publish(REPOS_QUEUE, body)
            publish(repo_name)
            print(repo_name)
