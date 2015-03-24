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

### Use Redis List for distributing work

I use my other Project [pusred](https://github.com/lukasmartinelli/pusred)
for distributing jobs via a Redis List.

Install

```
wget https://github.com/lukasmartinelli/pusred/releases/download/v0.9/pusred
```

Enqueue repos to analyze

```
export RQ_HOST="localhost"
export RQ_PORT="6379"
cat js_repos.txt | ./pusred lpush repostruct:repos
```
