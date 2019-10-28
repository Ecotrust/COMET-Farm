# COMET-Farm &middot; [![Build Status](https://img.shields.io/travis/npm/npm/latest.svg?style=flat-square)](https://travis-ci.org/npm/npm) [![npm](https://img.shields.io/npm/v/npm.svg?style=flat-square)](https://www.npmjs.com/package/npm) [![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com) [![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square)](https://github.com/your/your-project/blob/master/LICENSE)
> Place to collect docs, scripts, notes, and deadlines for our work with the COMET-Farm stuff

COMET-Farm API scripts &mdot; merge Excel template and CSV into a XML for feeding into the COMET-Farm API

### Setting up Environment

Here's a brief intro about what a developer must do in order to start developing
the project further:

```shell
git clone https://github.com/Ecotrust/COMET-Farm.git
cd COMET-Farm/
```

And state what happens step-by-step. If there is any virtual environment, local server or database feeder needed, explain here.

## Installing / Getting started


## Generate Input XML

A quick introduction of the minimal setup you need to get a hello world up &
running.

Combine GIS CSV data and .xlsx template file into xls:

  - <GIS data location> = system location of comma separated data from GIS
    - *e.g.*, `/usr/local/name/comet/data.csv`
  - <spreadsheet locatiion> = system location of spreadsheet to add GIS data
    - *e.g.*, `/usr/local/name/comet/data.xml`

```shell
python3 script combine_data.py <GIS data location> <spreadsheet location>
```

Generate XML file from CSV of GIS data and .xlsx file:

  - <spreadsheet locatiion> = system location of spreadsheet with input data
    - *e.g.*, `/usr/local/name/comet/data.xml`
```shell
python3 script generate_comet_input_file.py <spreadsheet location>
```

## Output from COMET-Farm  

COMET-Farm API in its current state sends an email with model run results in XML format.

The xml2csv.py script will parse the model run results XML file and create a CSV file for each map unit within a model run scenario. Your final result should look something like:

```
results/
  16560/
    baseline.csv
    notill.csv
  16561/
    baseline.csv
    notill.csv
  16564/
    baseline.csv
    notill.csv
```

How to use model run XML:  
  * save XML from COMET-Farm results email to somewhere on your local machine
    (*e.g.,* `COMET-Farm/results/<model_output.xml>`)
  * open a terminal window
  * navigate to the saved XML file
    `cd COMET-Farm/results/`
  * run the script
    `python3 COMET-Farm/scripts/xml2csv.py COMET-Farm/results/<model_output.xml>`  
     

## Caveats

Gotcas and some other things to be aware of:  

  * COMET-Farm parameter values in output XML have a trailing comma
    (*e.g.,* `<agcprd>2000,765.234,2001,86.234,...,2028,76.212,</agcprd>`)
  * COMET-Farm output XML returns the current year twice in each parameter value
    (*e.g.,* `<agcprd>2000,765.234,2001,86.234,...,2019,55.328,2019,55.328,2020,450,230,...</agcprd`)
    * sometimes on of the parameter values for the current year is 0
      (*e.g.,* `<agcprd>2000,765.234,2001,86.234,...,2019,0,2019,55.328,2020,450,230,...</agcprd`)
