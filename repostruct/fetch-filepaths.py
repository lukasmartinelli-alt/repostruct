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
import csv
import traceback

import requests
import pika
from docopt import docopt
from lxml import html
from fake_useragent import UserAgent
from rabbitmq import (configure_rabbitmq, METADATA_QUEUE,
                      FILEPATHS_QUEUE, FAILED_QUEUE)


class RepoNotExistsException(Exception):
    pass


def fetch_filepaths(repo, url, parent_directory=''):
    ua = UserAgent()
    headers = {
        'User-Agent': ua.random
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise RepoNotExistsException('Repo {} does not exist'.format(repo))

    tree = html.fromstring(response.text)

    rows = tree.cssselect('table.files tr')
    for row in rows:

        if ('warning' in row.get('class', '') or
            'up-tree' in row.get('class', '')):
            continue

        folder_icon = row.cssselect('.octicon-file-directory')
        is_folder = len(folder_icon) > 0
        link = row.cssselect('td.content a')[0]
        if not link.text:
            continue

        basename = link.text.strip()
        path_url = 'https://github.com' + link.attrib['href']

        if is_folder:
            subdirectories = fetch_filepaths(repo, path_url,
                                             parent_directory + '/' + basename)
            for subdir in subdirectories:
                yield subdir
        else:
            yield parent_directory + '/' + basename


def process_jobs_stdin():
    writer = csv.writer(sys.stdout, delimiter=' ', quoting=csv.QUOTE_ALL)
    for line in sys.stdin:
        repo = line.strip()

        try:
            url = 'https://github.com/' + repo
            filepaths = fetch_filepaths(repo, url)

            for filepath in filepaths:
                writer.writerow([
                    repo,
                    filepath
                ])
        except RepoNotExistsException as e:
            pass
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
        repo = body['repo']
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
                "repo": repo,
                "error": str(err)
            })

        try:
            url = 'https://github.com/' + repo
            filepaths = []
            for filepath in fetch_filepaths(repo, url):
                writer.writerow([
                    repo,
                    filepath
                ])
                filepaths.append(filepath)

            payload = {
                "repo": repo,
                "filepaths": filepaths,
                "metadata": metadata
            }
            print('Published filepaths for {}'.format(repo)) 
            publish(FILEPATHS_QUEUE, json.dumps(payload))
            ch.basic_ack(delivery_tag=method.delivery_tag)
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
