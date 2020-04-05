# Project Information  

Information gathered during meeting on 4.9.19  

<details>
<summary>Problem to be solved and reason for project</summary>

## Problems to Solve  

1. Understand potential for different landscapes to sequester carbon as part of ongoing efforts to mitigate and build resilance against effects of climate change  

2. Simplify use of Comet-Farm by utilizing Comet-Farm API  

## Why these are problems  

1. Running meta analysis of landscape carbon sequestration is difficult due to its complexity and limited number of studies  

2. Current work flow demands too much time  

</details>  

____  


<details>
<summary>Goals & success</summary>

## Goals

1. Inform Food & Farms program strategy by understanding agriculture (not grazing) field management practices on climate outputs

2. Inform broader conversation
  - inform and improve political policy
    - rule making process parameters
    - which practices should be incentivized
  - drive Ecotrust research questions

3. Ability to do analysis of climate outputs (*i.e.*, sensitivity analysis) 


## How we will be successful  

Automate Daycent model runs through Comet-Farm API

</details>  

____  


<details>
<summary>Project Summary</summary>
  
## Data

**Fields** (geospatial)
  - data set of millions of fields
  - each field has its own land management practices
  - running a model of 1000s of fields multiple times is not practical
  - fields will be classified and sample fields created

**Field types** (sample classification)
  - classification of fields using field data
    - inputs that affect soil carbon
  - samples created with unsuppervised classifcation alogorithm
  - discrete categores
  - will be between 80 and 90 samples of field
  - same params as comet farm
  
**Comet-Farm** (tool)  
  - runs a series of models for each potential source of green house gas emissions
    - uses DayCent model for field data
  - gives you spatially-explicit information on climate and soil conditions from USDA databases

## Comet-Farm  

Steps to use Comet-Farm (tool):  
  - add shapes to a map
  - define a set of land mgmt practices
  - comet-farm then gives you information on ghg emissions
  - export to a csv
  
## Current Process
  1. A dataset of fields exists in ESRI
    - includes geospatial, crop, and land mgmt data
  2. fields are classified into sample field types
  3. fields are drawn in comet-farm
  4. land mgmt data is entered into comet-farm
  5. comet-farm runs models
  6. comet-farm provides output
  7. output is exported to csv from comet-farm
  8. output under goes sensitivity analysis

Sensitivity analysis requires changes to output and reruning the model. These changes must be done through comet-farm website, repeating steps 4 - 8. Therefore sensitivity analysis is difficult and time consuming.
   
## New Process
  1. a set of 70 - 80 field types samples is created from millions of actual fields. Each sample includes:
    - geospatial data
    - crop data
    - management practice data (mean)
  2. A table is built for each sample. Table matches comet-farm output table. Includes cells for:
    - geospatial data
    - crop data
    - mgmt practices data 
    - **Note:** based on geospatial data comet-farm gathers climate data
    - **Note:** additional inputs and variables TBD
  3. Run Comet-Farm on table using Comet-Farm API 
  4. comet-farm provides output
  5. output under goes sensitivity analysis
  
Sensitiviy analysis will be run through command line and excel. This eliminates use of comet-farm website. Sensitivity analysis will be simplier and take less time. Reasoning:  

  - Simplier by reducing number of steps and modifying parameters using: 
    single software (excel) **VS** multiple tools (excel, comet-farm website)
  - Save time by using: 
    command line and API **VS** comet-farm website
  
</details>  


<details>
  <summary>Challenges</summary>

  - not many oregon crops on comet farm
  - only top crop in oregon is winter wheat
    - barley
    - corn
    - potatoes

  - Corn will be possible through mike's data as veg and silage.
  - Approximate grass seed would help a lot for Dwayne
  - Approximate for hay
  - Solution will not be a fully automated process
</details>

