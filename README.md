# repostruct

Collect the folder structures for all Github Repositories
of the major programming languages.

## Dataset

The list of the 400k analyzed repos are in the folder `repo`.
You can download the datasets for the individual languages here:

- [ ] Javascript
- [x] [Java (626 MB)](https://s3-eu-west-1.amazonaws.com/repostruct/java.tar.gz)
- [x] [Python (381 MB)](https://s3-eu-west-1.amazonaws.com/repostruct/python.tar.gz)
- [ ] Ruby
- [ ] PHP
- [x] [C++ (394MB)](https://s3-eu-west-1.amazonaws.com/repostruct/c%2B%2B.tar.gz)
- [ ] C
- [ ] C#
- [x] [Objective-C (85MB)](https://s3-eu-west-1.amazonaws.com/repostruct/obj-c.tar.gz)
- [x] [Go (39MB)](https://s3-eu-west-1.amazonaws.com/repostruct/go.tar.gz)

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

## Data sample

The data is a flat file separated by spaces.
The columns contain the full Github repository name, the relative filepath
and the filesize.

```
abergen84/Robot-Missions bower_components/chai/README.md 4691
abergen84/Robot-Missions bower_components/chai/sauce.browsers.js 1798
abergen84/Robot-Missions bower_components/chai/ReleaseNotes.md 23405
abergen84/Robot-Missions bower_components/chai/CONTRIBUTING.md 8289
abergen84/Robot-Missions bower_components/chai/chai.js 121651
abergen84/Robot-Missions bower_components/chai/package.json 1133
abergen84/Robot-Missions bower_components/chai/.bower.json 788
abergen84/Robot-Missions bower_components/chai/bower.json 529
abergen84/Robot-Missions bower_components/chai/karma.conf.js 625
abergen84/Robot-Missions bower_components/chai/karma.sauce.js 1201
abergen84/Robot-Missions bower_components/chai/component.json 1500
abergen84/Robot-Missions css/style.css 2255
abergen84/Robot-Missions js/app.js 629
abergen84/Robot-Missions js/RobotWars.js 5599
abergen84/Robot-Missions test.html 942
abergen84/Robot-Missions package.json 840
abergen84/Robot-Missions server.js 1429
abergen84/Robot-Missions index.html 2654
abergen84/Robot-Missions gulpfile.js 607
abergen84/Robot-Missions Procfile 27
abergen84/Robot-Missions heroku-server.js 37
```

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
