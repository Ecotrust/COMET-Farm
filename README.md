# COMET-Farm &middot; [![Build Status](https://img.shields.io/travis/npm/npm/latest.svg?style=flat-square)](https://travis-ci.org/npm/npm) [![npm](https://img.shields.io/npm/v/npm.svg?style=flat-square)](https://www.npmjs.com/package/npm) [![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com) [![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square)](https://github.com/your/your-project/blob/master/LICENSE)
> Place to collect docs, scripts, notes, and deadlines for our work with the COMET-Farm stuff

COMET-Farm API scripts &mdot; merge Excel template and CSV into a XML for feeding into the COMET-Farm API

### Setting up Environment

Here's a brief intro about what a developer must do in order to start developing
the project further:

```shell
git clone https://github.com/your/your-project.git
cd your-project/
packagemanager install
```

And state what happens step-by-step. If there is any virtual environment, local server or database feeder needed, explain here.

## Installing / Getting started

A quick introduction of the minimal setup you need to get a hello world up &
running.

Combine GIS CSV data and .xlsx template file into xls:

  - <GIS data location> = system location of comma separated data from GIS
    - *e.g.*, `/usr/local/name/comet/data.csv`
  - <spreadsheet locatiion> = system location of spreadsheet to add GIS data
    - *e.g.*, `/usr/local/name/comet/data.xml`

```shell
python3 script generate_comet_input_file.py <GIS data path> <spreadsheet path>
```

Generate XML file from CSV of GIS data and .xlsx file:

  - <spreadsheet locatiion> = system location of spreadsheet with input data
    - *e.g.*, `/usr/local/name/comet/data.xml`
```shell
python3 script generate_comet_input_file.py <spreadsheet location>
```
