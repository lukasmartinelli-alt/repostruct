# repostruct  [![Code Health](https://landscape.io/github/lukasmartinelli/repostruct/master/landscape.svg?style=flat)](https://landscape.io/github/lukasmartinelli/repostruct/master) [![Scrutinizer Code Quality](https://scrutinizer-ci.com/g/lukasmartinelli/repostruct/badges/quality-score.png?b=master)](https://scrutinizer-ci.com/g/lukasmartinelli/repostruct/?branch=master) [![Dependency Status](https://gemnasium.com/lukasmartinelli/repostruct.svg)](https://gemnasium.com/lukasmartinelli/repostruct) [![Code Issues](http://www.quantifiedcode.com/api/v1/project/3bf206116bdd4d1e893c78ab8d93c4dc/badge.svg)](http://www.quantifiedcode.com/app/project/3bf206116bdd4d1e893c78ab8d93c4dc)

**I am currently rebuilding the whole dataset. Check back in a week and you
have the filepaths of more than 6 million repos instead of 614k.**

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

## New Dataset

Each set is a 300MB compressed JSON file (2GB uncompressed) of repo samples.
The entire data set contains about 6 million repositories.

```bash
wget https://s3-eu-west-1.amazonaws.com/repostruct/filepaths-{1..18}.json.tar.gz
```

- https://s3-eu-west-1.amazonaws.com/repostruct/filepaths-1.json.tar.gz
- https://s3-eu-west-1.amazonaws.com/repostruct/filepaths-2.json.tar.gz
- https://s3-eu-west-1.amazonaws.com/repostruct/filepaths-3.json.tar.gz
- https://s3-eu-west-1.amazonaws.com/repostruct/filepaths-4.json.tar.gz
- https://s3-eu-west-1.amazonaws.com/repostruct/filepaths-5.json.tar.gz
- https://s3-eu-west-1.amazonaws.com/repostruct/filepaths-6.json.tar.gz
- https://s3-eu-west-1.amazonaws.com/repostruct/filepaths-7.json.tar.gz
- https://s3-eu-west-1.amazonaws.com/repostruct/filepaths-8.json.tar.gz
- https://s3-eu-west-1.amazonaws.com/repostruct/filepaths-9.json.tar.gz
- https://s3-eu-west-1.amazonaws.com/repostruct/filepaths-10.json.tar.gz
- https://s3-eu-west-1.amazonaws.com/repostruct/filepaths-11.json.tar.gz
- https://s3-eu-west-1.amazonaws.com/repostruct/filepaths-12.json.tar.gz
- https://s3-eu-west-1.amazonaws.com/repostruct/filepaths-13.json.tar.gz
- https://s3-eu-west-1.amazonaws.com/repostruct/filepaths-14.json.tar.gz
- https://s3-eu-west-1.amazonaws.com/repostruct/filepaths-15.json.tar.gz
- https://s3-eu-west-1.amazonaws.com/repostruct/filepaths-16.json.tar.gz
- https://s3-eu-west-1.amazonaws.com/repostruct/filepaths-17.json.tar.gz
- https://s3-eu-west-1.amazonaws.com/repostruct/filepaths-18.json.tar.gz

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

## Data sample

The data is stored as a JSON file (like the GitHub archive logs)
with a single JSON object per line.

Below is an example how the data is structured
(for clarity I split it up on multiple lines).


```json
{

  "repo":"aelydens/ruby-ridb",
  "metadata":{
    "repo":"aelydens/ruby-ridb",
    "social_counts":{
      "watchers":"1",
      "forks":"0",
      "stars":"0"
    },
    "language_statistics":[
      ["Ruby", "100.0"]
    ],
    "summary":{
      "commits":"9",
      "branches":"1",
      "contributors":"0",
      "releases":"0"
    }
  },
  "filepaths":[
    "ruby-ridb-0.1.0.gem",
    "ridb.gemspec",
    "Gemfile.lock",
    "README.md",
    "Gemfile",
    ".env",
    ".rspec",
    "lib/ridb/campsite.rb",
    "lib/ridb/search.rb",
    "lib/ridb/recarea.rb",
    "lib/ridb/facility.rb",
    "lib/ridb/client.rb",
    "lib/ridb/organization.rb",
    "spec/spec_helper.rb"
  ]
}
```

The `language_statistics` contains the percentage of the languages found
in the repository.

## Run it yourself

### Fetch latest GitHub repos

Iterate through all repositories from GitHub
that are not forks.
If the program times out due to API limitations you can simply
continue with the last repository id you fetched.

```
export GITHUB_ACCESS_TOKEN="adsf24.."
./fetch-latest-github-repos.py <last-repo-id>
```

### Fetch repos from Github Archive

Find all repos that were created or modified in January 2015.

```
./extract-github-repos.py 2015 1 >> 2015_jan.txt
```
