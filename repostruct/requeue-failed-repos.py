#!/usr/bin/env python
"""
Requeue repositories that failed
because of network timeouts or other reasons.
Fetch repository metadata

Usage:
    requeue-failed-repos.py <queue>
    requeue-failed-repos.py (-h | --help)

Options:
    -h --help    Show this screen
"""
import sys
import os
import csv
import traceback
import json

import pika
from docopt import docopt
from rabbitmq import (durable_publish, reject, configure_rabbitmq,
                      REPOS_QUEUE, METADATA_QUEUE, FAILED_QUEUE,
                      GIT_TIMEOUT_QUEUE, GIT_ERROR_QUEUE, NO_METADATA_QUEUE,
                      NOT_EXISTS_QUEUE)


def process_fails(rabbitmq_url, queue):
    connection = pika.BlockingConnection(pika.URLParameters(rabbitmq_url))
    channel = connection.channel()
    channel.basic_qos(prefetch_count=1)
    configure_rabbitmq(channel)

    def callback(ch, method, properties, body):
        body = json.loads(body.decode('UTF-8'))
        repo = body['repo']
        err = body['error']
        delivery_queue = REPOS_QUEUE

        if 'has no metadata' in err:
            delivery_queue = NO_METADATA_QUEUE

        if 'does not exist' in err:
            delivery_queue = NOT_EXISTS_QUEUE

        print('{} {}'.format(repo, body))

        try:
            payload = {
                "repo": repo
            }
            durable_publish(channel, delivery_queue, json.dumps(payload))
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            sys.stderr.write(str(e) + '\n')
            channel.basic_reject(delivery_tag=method.delivery_tag, requeue=True)
            raise

    channel.basic_consume(callback, queue=queue)

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()

    connection.close()


if __name__ == '__main__':
    args = docopt(__doc__)
    queue = args['<queue>']

    rabbitmq_url = os.getenv('RABBITMQ_URL')
    if not rabbitmq_url:
        sys.exit('You need to specify the RABBITMQ_URL env var')

    process_fails(rabbitmq_url, queue)
