#!/usr/bin/env python
"""
Iterate through all repositories from GitHub
that are not forks.
"""
import os

from github3 import login


GITHUB_ACCESS_TOKEN = os.getenv('GITHUB_ACCESS_TOKEN')
LAST_REPO_ID = int(os.getenv('LAST_REPO_ID', '-1'))

if __name__ == '__main__':
    gh = login(token=GITHUB_ACCESS_TOKEN)
    for repo in gh.iter_all_repos(per_page=200, since=LAST_REPO_ID):
        if not repo.fork:
            print(repo.id, repo.full_name)
