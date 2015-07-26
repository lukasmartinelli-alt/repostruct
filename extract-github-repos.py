#!/usr/bin/env python
"""
Read a GithubArchive JSON file and
find out the created and updated
repositories from the events.

Usage:
    extract-github-repos.py <json-file>
"""
import json
import fileinput


if __name__ == '__main__':
    repos = []
    for line in fileinput.input():
        event = json.loads(line)
        repo_name = event['repo']['name']
        repos.append(repo_name)

    unique_repos = set(repos)
    for repo_name in unique_repos:
        print(repo_name)

