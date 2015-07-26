# repostruct

Collect the folder structures for all Github Repositories
of the major programming languages.

## Dataset

The list of the 614k analyzed repos are in the folder `repo`.
You can download the datasets for the individual languages here:

- [x] [Javascript](https://s3-eu-west-1.amazonaws.com/repostruct/javascript.tar.gz)
- [x] [Java](https://s3-eu-west-1.amazonaws.com/repostruct/java.tar.gz)
- [x] [Python](https://s3-eu-west-1.amazonaws.com/repostruct/python.tar.gz)
- [x] [Ruby](https://s3-eu-west-1.amazonaws.com/repostruct/ruby.tar.gz)
- [x] [PHP](https://s3-eu-west-1.amazonaws.com/repostruct/php.tar.gz)
- [x] [C++](https://s3-eu-west-1.amazonaws.com/repostruct/c%2B%2B.tar.gz)
- [x] [C](https://s3-eu-west-1.amazonaws.com/repostruct/c.tar.gz)
- [x] [C#](https://s3-eu-west-1.amazonaws.com/repostruct/csharp.tar.gz)
- [x] [Objective-C](https://s3-eu-west-1.amazonaws.com/repostruct/obj-c.tar.gz)
- [x] [Go](https://s3-eu-west-1.amazonaws.com/repostruct/go.tar.gz)

You can also [download a PostgreSQL database backup](https://s3-eu-west-1.amazonaws.com/repostruct/repostruct_backup.tar) and import it for further analysis.
But be warned, It takes along time even with a 250GB Memory machine.

## Questions

Folder structures are pretty boring you think?
This dataset could help to answer questions like below:

- [x] [Which Languages use CI Services on Github?](http://lukasmartinelli.ch/cloud/2015/04/04/github-ci-services.html)
- [ ] How many people use Makefiles?
- [ ] What is the most common folder structure for node projects?
- [ ] Which languages adopt Docker the most (check for `Dockerfile`)
- [ ] What is the most popular Javascript build tool (check for `Gruntfile.js` or `Gulpfile.js`)
- [ ] What is the most popular Java build tool (check for `pom.xml` or `build.gradle`)
- [ ] How many files are in a repo on average?
- [ ] What programming languages are mixed together in a project most common?
- [ ] Do people prefer naming the folders `css` or `stylesheets`?
- [ ] Which programming languages have the deepest folder hierarchies (I guess Java?)
- [ ] Do people keep executables or build artifacts in their repos?

I blogged

## Data sample

The data is stored as a csv file with `,` as delimiter and `"` as quote character.
The columns contain the full Github repository name, the relative filepath
and the filesize.

```
"abergen84/Robot-Missions","css/style.css",2255
"abergen84/Robot-Missions","js/app.js",629
"abergen84/Robot-Missions","js/RobotWars.js",5599
"abergen84/Robot-Missions","test.html",942
"abergen84/Robot-Missions","package.json",840
"abergen84/Robot-Missions","server.js",1429
"abergen84/Robot-Missions","index.html",2654
"abergen84/Robot-Missions","gulpfile.js",607
"abergen84/Robot-Missions","Procfile",27
"abergen84/Robot-Missions","heroku-server.js",37
```

## Run it yourself

### Fetch top C++ repos on Github

Find the top Github repos and store them in a file.

```
./top-github-repos.py cpp > cpp_repos.txt
./top-github-repos.py js > js_repos.txt
```

### Fetch repos from Github Archive

Find all repos that were created or modified in January 2015.

```
./extract-github-repos.py 2015 1 >> 2015_jan.txt
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
