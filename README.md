# COMET-Farm &middot; [![Build Status](https://img.shields.io/travis/npm/npm/latest.svg?style=flat-square)](https://travis-ci.org/npm/npm) [![npm](https://img.shields.io/npm/v/npm.svg?style=flat-square)](https://www.npmjs.com/package/npm) [![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com) [![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square)](https://github.com/your/your-project/blob/master/LICENSE)

> :bellhop_bell:  >  **See [Offical API Docs on Gitlab](https://gitlab.com/comet-api/api-docs)**

COMET-Farm API scripts - use an Excel template and GIS data export to create an XML file for feeding into the COMET-Farm API, then reformat COMET-Farm API results.  

## Setting up Environment

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


## Create Cropland Data

### Generate API input XML file

**How to generate a COMET-Farm API input XML file:**

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

  * This script creates a new spreadsheet called combined_data.xls using the template_v*.xls scenario tab as a template

  * A new scenario tab is created in combined_data for each field_ID given in the GIS data CSV. The tab is named ready_<field_ID>

  * Once created the script executes generate_comet_input_file.py (formerly this step was done manually)

  * An XML file is created with a <cropland> scenario for each ready_* tab of combined_data.

  **The script makes assumptions and depends upon certain locations for cells of the template_v*. Any change to template layout, be sure to update both create_api_input.py and generate_comet_input_file.py**

\* use latest version

### Generate CSV from COMET-Farm API Output

COMET-Farm API in its current state sends an email with model run results in XML format.

The xml2csv.py script will parse the model run results of 3 XML file (baseline, baseline+14, and baseline-14) to create a CSV file that has a row for each mapunit id.  

Your final result will be in `./results/ghg_balance.csv` and look something like this:

| mapunit_id | baseline | baseline +14 | baseline -14 |
|------------|----------|--------------|--------------|
| 12345 | -123.56 | -122.90 | -119.884 |
| 43289 | 100.200 | 120.45 | 113.1232 |

**How to generate results CSVs from E-mail results:**

1. Unzipped the compressed results  
  * save XML from COMET-Farm results email to somewhere on your local machine
    (*e.g.,* `COMET-Farm/results/<model_output.xml>`)
  * open a terminal window
  * navigate to the saved XML file
    `cd COMET-Farm/results/`
  * run the script
    `python3 COMET-Farm/scripts/xml2csv.py COMET-Farm/results/<model_output_baseline.xml> COMET-Farm/results/<model_output_baseline_plus_14>.xml COMET-Farm/results/<model_output_baseline_minus_14.xml>`

**Overview of Script**  

This script takes as arguments XML files from a COMET-Farm results email, then outputs a CSV file containing a table with rows for mapunits and columns for CO2e formulas for CO2e:
    * area-weighted greenhouse gas balance (soil C stock change + N2O emissions + CH4 emissions)

Steps:
  * Do calculations for greenhouse gas balance in each mapunit
    `(soil C stock change + N2O emissions + CH4 emissions)`

  * Soil Carbon Stock Change (SCSC) - equation to evaluate changes in soil carbon (C change expressed in CO2e)

    * use `<somsc>` tag

    * units are grams of soil carbon per meter squared

    * `( ( somsc at beginning of model run – somsc at end of model run ) / time period in years of model run ) * ( size of parcel in ha ) * ( 10,000 m2/hectare ) * ( 1 Mg / 1,000,000 grams) * (44/12 C to CO2e conversion factor) = change in soil C (Mg CO2e/yr)`

    * a negative value indicates net soil carbon sequestration for this parcel

  * Direct Soil Nitrous Oxide (Direct Soil N2O) - (N2O expressed in CO2e)

    * use `<n2oflux>` tag

    * units are grams of N2O-N per meter squared per year

    * `( average DayCent yearly N2O emissions over the model run ) * ( 44 / 28 N2O-N to N2O conversion ) * ( 298 N2O to CO2e conversion) * ( size of parcel in ha ) * ( 10,000 m2/hectare ) * ( 1 Mg / 1,000,000 grams)`

  * Indirect soil nitrous oxide (ISNO) - product of both volatilized nitrogen and leached nitrogen (N2O expressed in CO2e)

    * Volatilized N: Indirect Soil Nitrous Oxide - `<volpac>`

    * Leached N: Indirect Soil Nitrous Oxide - `<strmac_2>`

    * units are g N m2/yr

    * For example, consider the following output strings for a Current Management model period (identified as “Current”, or 2000-2017) on a 1 hectare parcel:

    * The equation to calculate the soil indirect N2O emissions from volatilization is as follows for the period 2008 to 2017:

        `( average DayCent volpac emissions over the model run ) * ( 0.0075 EFvol ) * ( 44/28 N2O-N to N2O conversion ) * ( 298 N2O to CO2e conversion) * ( size of parcel in ha ) * ( 10,000 m2/hectare ) * ( 1 Mg / 1,000,000 grams)`

    * The equation to calculate the soil indirect N2O emissions from leaching is as follows for the period of 2008 to 2017:

        `( average DayCent strmac_2 emissions over the model run ) * ( 0.01 EFleach ) * ( 44/28 N2O-N to N2O conversion ) * ( 298 N2O to CO2e conversion) * ( size of parcel in ha ) * ( 10,000 m2/hectare ) * ( 1 Mg / 1,000,000 grams) = Mg/ha CO2e`

    * The yearly indirect soil N2O emissions predicted by DayCent from leaching would be as follows:

        `( 0.313 + 0.318 + 0.045872 + 0.216 + 0.335 + 0.335 + 0.357 + 0.320 + 0.335 + .046745 ) * ( 1 / 10 years ) * ( 0.01 ) * ( 44/28 ) * ( 298 ) * ( 1 ha ) * ( 10000 / 1000000 ) =  Mg N2O / yr ( in CO2e ) = 0.0092 Mg/ha CO2e`

Steps:
    1. Open results file
    2. Loop through model runs
    3. Create a CSV file with a row for each map unit and columns for:
        * mapunitID
        * Baseline
        * Baseline +14 days
        * Baseline -14 days  


### Caveats

Gotcas and some other things to be aware of:  

  * COMET-Farm parameter values in output XML have a trailing comma
    (*e.g.,* `<agcprd>2000,765.234,2001,86.234,...,2028,76.212,</agcprd>`)
  * COMET-Farm output XML returns the current year twice in each parameter value
    (*e.g.,* `<agcprd>2000,765.234,2001,86.234,...,2019,55.328,2019,55.328,2020,450,230,...</agcprd`)
    * sometimes on of the parameter values for the current year is 0
      (*e.g.,* `<agcprd>2000,765.234,2001,86.234,...,2019,0,2019,55.328,2020,450,230,...</agcprd`)

### Additional Documenation  

  * https://github.com/Ecotrust/COMET-Farm/issues/1
  * https://github.com/Ecotrust/COMET-Farm/issues/14
    
    

