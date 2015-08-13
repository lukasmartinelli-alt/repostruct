#!/usr/bin/env python
"""
Export repo filepaths data to a flat file

Usage:
    export-data.py
    export-data.py (-h | --help)

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
from rabbitmq import (durable_publish, configure_rabbitmq,
                      FILEPATHS_QUEUE, FILEPATHS_ARCHIVE_QUEUE)


def export_filepaths(rabbitmq_url):
    connection = pika.BlockingConnection(pika.URLParameters(rabbitmq_url))
    channel = connection.channel()
    channel.basic_qos(prefetch_count=1)
    configure_rabbitmq(channel)

    def callback(ch, method, properties, body):
        body = json.loads(body.decode('UTF-8'))
        print(json.dumps(body))

        try:
            durable_publish(channel, FILEPATHS_ARCHIVE_QUEUE,
                            json.dumps(body))
            channel.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            channel.basic_reject(delivery_tag=method.delivery_tag, requeue=True)
            raise

    channel.basic_consume(callback, queue=FILEPATHS_QUEUE)

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        requeued_messages = channel.cancel()
        channel.stop_consuming()

    connection.close()


if __name__ == '__main__':
    args = docopt(__doc__)

    rabbitmq_url = os.getenv('RABBITMQ_URL')
    if not rabbitmq_url:
        sys.exit('You need to specify the RABBITMQ_URL env var')

    export_filepaths(rabbitmq_url)
