# repostruct
Analyze folder structures of Github Repositories

##Usage

For best mode you should disable input and output buffering of Python.

``
export PYTHONUNBUFFERED=true
``

### Fetch top C++ repos on Github

Find the top Github repos and store them in a file.

```
./top-github-repos.py cpp > cpp_repos.txt
./top-github-repos.py js > js_repos.txt
```
