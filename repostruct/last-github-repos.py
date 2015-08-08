#!/usr/bin/env python
"""
Iterate through all repositories from GitHub
that are not forks.
"""
import sys
import time
import os
import csv

from github3 import login
from requests_futures.sessions import FuturesSession
from lxml import html


GITHUB_ACCESS_TOKEN = os.getenv('GITHUB_ACCESS_TOKEN')
LAST_REPO_ID = int(os.getenv('LAST_REPO_ID', '-1'))


def write_repo(page):
    tree = html.fromstring(page.text)
    numbers = tree.xpath('//span[@class="num text-emphasized"]')
    
    commits = numbers[0].text.strip()
    branches = numbers[1].text.strip()
    releases = numbers[2].text.strip()
    contributors = numbers[3].text.strip()

    def parse_language_statistics():
        for lang_stat in tree.cssselect('ol.repository-lang-stats-numbers li'):
            lang = lang_stat.cssselect('span.lang')[0].text.strip()
            percent = lang_stat.cssselect('span.percent')[0].text.strip()
            yield lang, percent.replace('%', '')

    stats = [lang + ':' + percent for lang, percent in parse_language_statistics()]
    stats = ','.join(stats)

    social_counts = [sc.text.strip() for sc in tree.cssselect('a.social-count')]
    watchers = social_counts[0].replace(',','')
    stars = social_counts[1].replace(',','')
    forks = social_counts[2].replace(',','')

    repo_id = tree.cssselect('#repository_id')[0]


if __name__ == '__main__':
    gh = login(token=GITHUB_ACCESS_TOKEN)
    writer = csv.writer(sys.stdout, delimiter=' ', quoting=csv.QUOTE_ALL)
    session = FuturesSession()

    #def scrape_repo(response):
    #    writer.writerow([repo.id, repo.full_name, repo.fork])

    for repo in gh.iter_all_repos(per_page=200, since=LAST_REPO_ID):
        url = 'https://github.com/' + repo.full_name
        future = session.get(url)
        page = future.result()
        parse_repo_page(page)
 
        writer.writerow([repo.id, repo.full_name, repo.fork])


