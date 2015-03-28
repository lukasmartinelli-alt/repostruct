# repostruct

Collect the folder structures for all Github Repositories
of the major programming languages.

## Dataset

The analyzed repos are in the folder `repo`.

You can download the results here:

- [x] [Go (18270 repos)](https://s3-eu-west-1.amazonaws.com/repostruct/go.tar.gz)
- [x] [Objective-C (35302 repos)](https://s3-eu-west-1.amazonaws.com/repostruct/obj-c.tar.gz)
- [ ] Java
- [ ] C#
- [ ] Javascript
- [ ] C++ (51852 repos)
- [ ] C
- [ ] PHP
- [ ] Ruby
- [ ] Python

## Questions

Folder structures are pretty boring you think?
This dataset could help to answer questions like below:

- [ ] How many people use Makefiles?
- [ ] What is the most common folder structure for node projects?
- [ ] Which languages adopt Docker the most (check for `Dockerfile`)
- [ ] What is the most popular Javascript build tool (check for `Gruntfile.js` or `Gulpfile.js`)
- [ ] What is the most popular Java build tool (check for `pom.xml` or `build.gradle`)
- [ ] How many files are in a repo on average?
- [ ] What programming languages are mixed together in a project most common?
- [ ] Do people prefer naming the folders `css` or `stylesheets`?
- [ ] How many people use travis?
- [ ] Which programming languages have the deepest folder hierarchies (I guess Java?)
- [ ] Do people keep executables or build artifacts in their repos?

## Run it yourself

### Fetch top C++ repos on Github

Find the top Github repos and store them in a file.

```
./top-github-repos.py cpp > cpp_repos.txt
./top-github-repos.py js > js_repos.txt
```

### Use redis-pipe for distributing work

Run redis

```
docker run --name redis -p 6379:6379 -d redis
```

I use my other Project [redis-pipe](https://github.com/lukasmartinelli/redis-pipe)
for distributing jobs via a Redis List.

Install

```
wget https://github.com/lukasmartinelli/redis-pipe/releases/download/v1.4/redis-pipe
```

Enqueue repos to analyze

```
cat js_repos.txt | ./redis-pipe repostruct:repos
```

Analyze repo folder structure and put results into another list.
I normally do this in batches of 100.

```
./redis-pipe --count 100 repostruct:repos | ./repostruct.py | ./redis-pipe repostruct:results
```

## Analyze

How many Go projects use Makefiles?

```
cat go.txt | grep "Makefile " | sort -k 1 | cut -d " " -f 1 | uniq | wc -l
```
