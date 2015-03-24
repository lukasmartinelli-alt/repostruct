#!/usr/bin/env python
"""
Find the top repos for a programming language on Github
with the Github Search API.
"""
import sys

import requests


def get_top_repositories(language):
    """Search for the top 1000 cpp repos in github and return their git url"""
    url = "https://api.github.com/search/repositories"
    params = {
        'q': 'language:{0}'.format(language),
        'sort': 'star',
        'order': 'desc',
        'per_page': '100'
    }
    headers = {"Accept": "application/vnd.github.v3+json"}
    response = requests.get(url, headers=headers, params=params)

    while "next" in response.links.keys():
        url = response.links["next"]["url"]
        response = requests.get(url, headers=headers)

        if response.status_code == requests.codes.ok:
            for repo in response.json()["items"]:
                yield repo["full_name"]
        else:
            sys.stderr.write("Request " + url + " was not successful.")
            sys.exit(1)


if __name__ == '__main__':
    try:
        language = sys.argv[1]
    except IndexError:
        language = 'cpp'

    for repo in get_top_repositories(language):
        sys.stdout.write(repo + "\n")
