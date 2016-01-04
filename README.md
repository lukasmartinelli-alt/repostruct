# repostruct  [![Code Health](https://landscape.io/github/lukasmartinelli/repostruct/master/landscape.svg?style=flat)](https://landscape.io/github/lukasmartinelli/repostruct/master) [![Scrutinizer Code Quality](https://scrutinizer-ci.com/g/lukasmartinelli/repostruct/badges/quality-score.png?b=master)](https://scrutinizer-ci.com/g/lukasmartinelli/repostruct/?branch=master) [![Dependency Status](https://gemnasium.com/lukasmartinelli/repostruct.svg)](https://gemnasium.com/lukasmartinelli/repostruct)

Collect the folder structures for all Github Repositories of the major programming languages.
Contains 1.5 billion filepaths from 7 million repos as of August 2015.

## Dataset

You can download the dataset (13.5GB) from AWS S3.

```bash
wget -c https://s3-eu-west-1.amazonaws.com/repostruct/repos.json.gz
tar -xvz repos.json
```

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
