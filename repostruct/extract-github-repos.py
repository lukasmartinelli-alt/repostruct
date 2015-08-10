#!/usr/bin/env python
"""
Read a GithubArchive JSON file and
find out the created and updated
repositories from the events.

Usage:
    extract-github-repos.py <year>
    extract-github-repos.py <year> <month>
    extract-github-repos.py <year> <month> <day>
    extract-github-repos.py <year> <month> <day> <hour>
    extract-github-repos.py -h | --help

Options:
    -h --help     Show help.
"""
import sys
import json
import fileinput
import urllib.request
import gzip
import io
import calendar

from docopt import docopt


def archive_url(year, month, day, hour):
    url = 'http://data.githubarchive.org/{0}-{1:0>2d}-{2:0>2d}-{3}.json.gz'
    return url.format(year, month, day, hour)


def extract_repos_from_archive_file(archive_url):
    try:
        response = urllib.request.urlopen(archive_url)
        with gzip.GzipFile(fileobj=response, mode='r') as archive_file:
            for line in archive_file:
                event = json.loads(line.decode('UTF-8'))
                repo_name = event['repo']['name']
                yield repo_name
    except urllib.error.HTTPError as err:
        # 404 Errors happen because some months do not have 31 days
        if err.code != 404:
            raise


if __name__ == '__main__':
    args = docopt(__doc__)
    unique_events = {}

    def expand_date_args(date_type):
        date_arg = args['<' + date_type + '>']
        if date_arg:
            return [int(date_arg)]
        else:
            if date_type == 'month':
                return [x for x in range(1,12)]
            elif date_type == 'day':
                return [x for x in range(1,31)]
            elif date_type == 'hour':
                return [x for x in range(0, 23)]

    def unique_repos(year, month, day, hour):
        url = archive_url(year, month, day, hour)

        try:
            repos = extract_repos_from_archive_file(url)
        except Exception as e:
            sys.stderr.write(str(e) + '\n')

        for repo_name in repos:
            if repo_name not in unique_events:
                unique_events[repo_name] = True
                yield repo_name

    years = expand_date_args('year')
    months = expand_date_args('month')
    days = expand_date_args('day')
    hours = expand_date_args('hour')

    for year in years:
        for month in months:
            for day in days:
                for hour in hours:
                    for repo_name in unique_repos(year, month, day, hour):
                        print(repo_name)
