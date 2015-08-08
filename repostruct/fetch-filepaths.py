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
import csv
import traceback

import requests
import pika
from docopt import docopt
from lxml import html
from rabbitmq import (configure_rabbitmq, JOBS_QUEUE,
                      RESULTS_QUEUE, FAILED_QUEUE)


class RepoNotExistsException(Exception):
    pass


class RepoNoMetadata(Exception):
    pass


def fetch_filepaths(repo, url, parent_directory=''):
    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
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
   # for line in sys.stdin:
    for line in ['Sebubu/BringToAfrica']:
        repo = line.strip()

        try:
            url = 'https://github.com/' + repo
            filepaths = fetch_filepaths(repo, url)

            for filepath in filepaths:
                writer.writerow([
                    repo,
                    filepath
                ])
        except RepoNoMetadata as e:
            pass
        except RepoNotExistsException as e:
            pass
        except Exception as e:
            print(traceback.format_exc(), file=sys.stderr)


if __name__ == '__main__':
    args = docopt(__doc__)

    if args['--rabbitmq']:
        rabbitmq_url = os.getenv('RABBITMQ_URL')
        if not rabbitmq_url:
            sys.exit('You need to specify the RABBITMQ_URL env var')
        process_jobs_rabbitmq(rabbitmq_url)
    else:
        process_jobs_stdin()
