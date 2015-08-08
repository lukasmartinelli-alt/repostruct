#!/usr/bin/env python
"""
Fetch repository metadata

Usage:
    fetch-metadata.py [--rabbitmq]
    fetch-metadata.py (-h | --help)

Options:
    -h --help    Show this screen
    --rabbitmq   Use RabbitMQ for distributing jobs
"""
import sys
import time
import os
import csv

import requests
from docopt import docopt
from lxml import html


def fetch_metadata(repo):
    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
    }
    url = 'https://github.com/' + repo
    response = requests.get(url, headers=headers)
    tree = html.fromstring(response.text)

    def extract_summary_numbers():
        numbers = tree.cssselect('.numbers-summary span.text-emphasized')
        commits = numbers[0].text
        branches = numbers[1].text
        releases = numbers[2].text
        contributors = numbers[3].text

        if not contributors:
            contributors = '0'

        return {
            "commits": commits.strip(),
            "branches": branches.strip(),
            "releases": releases.strip(),
            "contributors": contributors.strip(),
        }

    def extract_social_counts():
        links = tree.cssselect('a.social-count')
        social_counts = [sc.text.strip() for sc in links]
        watchers = social_counts[0].replace(',','')
        stars = social_counts[1].replace(',','')
        forks = social_counts[2].replace(',','')

        return {
            "watchers": watchers,
            "stars": stars,
            "forks": forks
        }

    def parse_language_statistics():
        for li in tree.cssselect('ol.repository-lang-stats-numbers li'):
            lang = li.cssselect('span.lang')[0].text.strip()
            percent = li.cssselect('span.percent')[0].text.strip()
            yield lang, percent.replace('%', '')

    return {
        "repo": repo,
        "summary": extract_summary_numbers(),
        "social_counts": extract_social_counts(),
        "language_statistics": list(parse_language_statistics()),
    }


def process_jobs_stdin():
    writer = csv.writer(sys.stdout, delimiter=' ', quoting=csv.QUOTE_ALL)
    for line in sys.stdin:
        repo = line.strip()

        try:
            metadata = fetch_metadata(repo)
            stats = [l + ':' + p for l, p in metadata["language_statistics"]]

            writer.writerow([
                repo,
                metadata["summary"]["commits"],
                metadata["summary"]["branches"],
                metadata["summary"]["releases"],
                metadata["summary"]["contributors"],
                metadata["social_counts"]["watchers"],
                metadata["social_counts"]["stars"],
                metadata["social_counts"]["forks"],
                ','.join(stats)
            ])
        except Exception as e:
            raise e
            #print(e, file=sys.stderr)


if __name__ == '__main__':
    args = docopt(__doc__)

    if args['--rabbitmq']:
        rabbitmq_url = os.getenv('RABBITMQ_URL')
        if not rabbitmq_url:
            sys.exit('You need to specify the RABBITMQ_URL env var')
        process_jobs_rabbitmq(rabbitmq_url)
    else:
        process_jobs_stdin()
