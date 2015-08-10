#!/usr/bin/env python
"""
Iterate through all repositories from GitHub
that are not forks.
If the program times out due to API limitations you can simply
continue with the last repository id you fetched.

Usage:
    fetch-latest-github-repos.py <last-repo-id>

Options:
    -h --help     Show help.
"""
import os
import sys

from docopt import docopt
from github3 import login


GITHUB_ACCESS_TOKEN = os.getenv('GITHUB_ACCESS_TOKEN')
REPOS_PER_PAGE = int(os.getenv('REPOS_PER_PAGE', '200'))
LAST_REPO_ID = int(os.getenv('LAST_REPO_ID', '-1'))

if __name__ == '__main__':
    args = docopt(__doc__)

    if not GITHUB_ACCESS_TOKEN:
        sys.exit('You need to specify the GITHUB_ACCESS_TOKEN env var')

    last_repo_id = int(args.get('<last-repo-id>', '-1'))

    gh = login(token=GITHUB_ACCESS_TOKEN)
    for repo in gh.iter_all_repos(per_page=REPOS_PER_PAGE, since=last_repo_id):
        if not repo.fork:
            print(repo.id, repo.full_name)
