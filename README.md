# COMET-Farm &middot; [![Build Status](https://img.shields.io/travis/npm/npm/latest.svg?style=flat-square)](https://travis-ci.org/npm/npm) [![npm](https://img.shields.io/npm/v/npm.svg?style=flat-square)](https://www.npmjs.com/package/npm) [![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com) [![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square)](https://github.com/your/your-project/blob/master/LICENSE)
> Place to collect docs, scripts, notes, and deadlines for our work with the COMET-Farm stuff

COMET-Farm API scripts &mdot; use an Excel template and GIS data export to create an XML file for feeding into the COMET-Farm API, then reformat COMET-Farm API results.

### Setting up Environment

**Get the repo**

1. Open a terminal window
2. Navigate to or create a directory you would like to use.
  ```shell
  cd projects/
  mkdir comet
  ```
3. Clone the repo  
  ```shell
  git clone https://github.com/Ecotrust/COMET-Farm.git
  cd COMET-Farm/
  ```

## Installing / Getting started

**Dependencies**
  * Python 3
  * pip3
  * openpyxl

**Install Dependencies**

1. Check if you have Python 3 installed
  ```shell
  python3
  ```
  
  This should active a python interpreter, otherwise you need to install python3.

  Download at https://www.python.org/downloads/

2. pip3 should come installed with Python 3, but run the following to get the latest version
  ```shell
  pip install -U pip
  ```

3. install openpyxl
  ```shell
  pip3 install openpyxl
  ```


# Create Cropland Data

## Generate API input XML file

### How to generate a COMET-Farm API input XML file:  

1. Open template_v2 Excel spreadsheet

2. Save a copy of template_v2 for each field you have a scenario for

  * Save the file using whatever naming convention make sense to you

3. Add scenario data to each field's spreadsheet

  * Input information in column B for rows 2 - 4

  * Current field practices go in row 17 - 36 columns B - Q

  * In column B row 38 name your scenario, then add data in rows 40 - 48 columns B - Q

  * If you have a second scenario for the field name it in B51 and fill out rows 53 - 62 columns B - Q

  * Save the file

4. Export field data from GIS software in a comma separated format (CSV or TXT)

5. Combine GIS CSV data and .xlsx template file into XML:

  ```shell
    python3 create_api_input.py <GIS data location> <spreadsheet location>
  ```

  * `<GIS data location>` = system location of comma separated data from GIS
    * *e.g.*, `/usr/local/name/comet/data.csv`

  * `<spreadsheet locatiion>` = system location of spreadsheet to add GIS data
    * *e.g.*, `/usr/local/name/comet/data.xml`

## Generate CSV from COMET-Farm API Output

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
  Results_***.aggregate.csv
```

### How to generate results CSVs from E-mail results

1. Unzipped the compressed results  
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
