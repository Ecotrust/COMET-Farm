# import system modules
from datetime import datetime
import os, sys, csv, time, string
import xml.etree.ElementTree as ET
# import ipdb

'''
    Overview of script
    ==================

    This script takes as arguments XML files from a COMET-Farm results email,
    then outputs a CSV file containing a table with rows for mapunits and columns for CO2e
    formulas for CO2e:
        * area-weighted greenhouse gas balance (soil C stock change + N2O emissions + CH4 emissions)

    Next steps:
      * Do calculations for greenhouse gas balance in each mapunit
        `(soil C stock change + N2O emissions + CH4 emissions)`

        * Soil Carbon Stock Change (SCSC) - equation to evaluate changes in soil carbon (C change expressed in CO2e)

            * use `<somsc>` tag

            * units are grams of soil carbon per meter squared

            * `( ( somsc at beginning of model run – somsc at end of model run ) / time period in years of model run ) * ( size of parcel in ha ) * ( 10,000 m2/hectare ) * ( 1 Mg / 1,000,000 grams) * (44/12 C to CO2e conversion factor) = change in soil C (Mg CO2e/yr)`

            * a negative value indicates net soil carbon sequestration for this parcel

        * Direct Soil Nitrous Oxide (DSNO) - (N2O expressed in CO2e)

            * use `<n2oflux>` tag

            * units are grams of N2O-N per meter squared per year

            * `( average DayCent yearly N2O emissions over the model run ) * ( 44 / 28 N2O-N to N2O conversion ) * ( 298 N2O to CO2e conversion) * ( size of parcel in ha ) * ( 10,000 m2/hectare ) * ( 1 Mg / 1,000,000 grams)`

        * Indirect soil nitrous oxide (ISNO) - product of both volatilized nitrogen and leached nitrogen (N2O expressed in CO2e)

            * use `<volpac>` tag for volatilized N

            * use `<strmac_2>` tag for leached N

            * units are g N m2/yr

            * For example, consider the following output strings for a Current Management model period (identified as “Current”, or 2000-2017) on a 1 hectare parcel:

                <strmac_2_>2009,0.0,2009.08,0.245,2009.17,0.265,2009.25,0.266,2009.33,0.269,2009.42,0.271,2009.5,0.272,2009.58,0.272,2009.67,0.272,2009.75,0.272,2009.83,0.272,2009.92,0.272,2010,0.272,2010.08,0.0,2010.17,0.0,2010.25,0.0,2010.33,0.0,2010.42,0.0,2010.5,0.0,2010.58,0.0,2010.67,0.0,2010.75,0.0,2010.83,0.0,2010.92,0.0,2011,0.0,2011.08,0.0,2011.17,0.0,2011.25,0.0,2011.33,0.0,2011.42,0.0,2011.5,0.0,2011.58,0.0,2011.67,0.0,2011.75,0.0,2011.83,0.0,2011.92,0.0,2012,0.0,2012.08,0.0,2012.17,0.0,2012.25,0.284,2012.33,0.346,2012.42,0.351,2012.5,0.356,2012.58,0.359,2012.67,0.359,2012.75,0.359,2012.83,0.359,2012.92,0.359,2013,0.359,2013.08,0.0,2013.17,1.785,2013.25,2.878,2013.33,2.881,2013.42,2.881,2013.5,2.886,2013.58,2.887,2013.67,2.887,2013.75,2.887,2013.83,2.887,2013.92,2.887,2014,2.887,2014.08,3.031,2014.17,4.010,2014.25,4.083,2014.33,4.093,2014.42,4.094,2014.5,4.094,2014.58,4.094,2014.67,4.094,2014.75,4.094,2014.83,4.094,2014.92,4.094,2015,4.094,2015.08,0.0,2015.17,0.0,2015.25,0.0,2015.33,0.0,2015.42,0.0,2015.5,0.0,2015.58,0.0,2015.67,0.0,2015.75,0.0,2015.83,0.0,2015.92,0.0,2016,0.0,2016.08,3.230,2016.17,3.466,2016.25,4.978,2016.33,4.993,2016.42,4.993,2016.5,4.995,2016.58,4.995,2016.67,4.995,2016.75,4.995,2016.83,4.995,2016.92,4.995,2017,4.995,2017.08,0.184,2017.17,2.175,2017.25,2.880,2017.33,2.882,2017.42,2.884,2017.5,2.884,2017.58,2.884,2017.67,2.884,2017.75,2.884,2017.83,2.889,2017.92,2.891,2018,3.122,2018,0.0,</strmac_2_>

                <volpac>2009,0.313,2009.08,0.0,2009.17,0.0,2009.25,0.0,2009.33,0.0,2009.42,0.0,2009.5,0.0,2009.58,0.0,2009.67,0.0,2009.75,0.0,2009.83,0.318,2009.92,0.318,2010,0.318,2010.08,-8.506E-09,2010.17,6.5631E-06,2010.25,1.4848E-05,2010.33,5.6368E-03,2010.42,1.7234E-02,2010.5,2.6689E-02,2010.58,3.3214E-02,2010.67,3.9155E-02,2010.75,4.2075E-02,2010.83,4.4129E-02,2010.92,4.5445E-02,2011,4.5872E-02,2011.08,7.5126E-05,2011.17,-1.394E-05,2011.25,1.9422E-04,2011.33,5.0168E-04,2011.42,5.0168E-04,2011.5,5.0168E-04,2011.58,0.216,2011.67,0.216,2011.75,0.216,2011.83,0.216,2011.92,0.216,2012,0.216,2012.08,0.0,2012.17,0.0,2012.25,0.0,2012.33,0.0,2012.42,0.0,2012.5,0.0,2012.58,0.0,2012.67,0.0,2012.75,0.0,2012.83,0.335,2012.92,0.335,2013,0.335,2013.08,0.0,2013.17,0.0,2013.25,0.0,2013.33,0.0,2013.42,0.0,2013.5,0.0,2013.58,0.0,2013.67,0.0,2013.75,0.0,2013.83,0.335,2013.92,0.335,2014,0.335,2014.08,0.0,2014.17,0.0,2014.25,0.0,2014.33,0.0,2014.42,0.0,2014.5,0.0,2014.58,0.0,2014.67,0.0,2014.75,0.0,2014.83,0.357,2014.92,0.357,2015,0.357,2015.08,0.0,2015.17,0.0,2015.25,0.0,2015.33,0.0,2015.42,0.0,2015.5,0.0,2015.58,0.0,2015.67,0.0,2015.75,0.0,2015.83,0.320,2015.92,0.320,2016,0.320,2016.08,0.0,2016.17,0.0,2016.25,0.0,2016.33,0.0,2016.42,0.0,2016.5,0.0,2016.58,0.0,2016.67,0.0,2016.75,0.0,2016.83,0.335,2016.92,0.335,2017,0.335,2017.08,-2.711E-08,2017.17,8.9977E-06,2017.25,6.2888E-04,2017.33,3.3137E-03,2017.42,1.0772E-02,2017.5,2.3423E-02,2017.58,3.1529E-02,2017.67,3.8201E-02,2017.75,4.3781E-02,2017.83,4.6393E-02,2017.92,4.6729E-02,2018,4.6745E-02,2018,0.0,</volpac>


            * The equation to calculate the soil indirect N2O emissions from volatilization is as follows for the period 2008 to 2017:

                `( 0.0 + 0.272 + 0.0 + 0.0 + 0.359 + 2.887 + 4.094 + 0.0 + 4.995 + 3.122 ) ( 1/10 yrs) * ( 0.01 EFleach) * ( 44/28 N2O-N to N2O conversion ) * ( 298 N2O to CO2e conversion) * ( size of parcel in ha ) * ( 10,000 m2/hectare ) * ( 1 Mg / 1,000,000 grams) = 0.074 Mg/ha CO2e`

            * The equation to calculate the soil indirect N2O emissions from leaching is as follows for the period of 2008 to 2017:

                `( average DayCent volpac emissions over the model run ) * ( 0.0075 EFvol) * ( 44/28 N2O-N to N2O conversion ) * ( 298 N2O to CO2e conversion) * ( size of parcel in ha ) * ( 10,000 m2/hectare ) * ( 1 Mg / 1,000,000 grams)`

            * The yearly indirect soil N2O emissions predicted by DayCent from leaching would be as follows:

                `( 0.313 + 0.318 + 0.045872 + 0.216 + 0.335 + 0.335 + 0.357 + 0.320 + 0.335 + .046745 ) * ( 1 / 10 years ) * ( 0.01 ) * ( 44/28 ) * ( 298 ) * ( 1 ha ) * ( 10000 / 1000000 ) =  Mg N2O / yr ( in CO2e ) = 0.0092 Mg/ha CO2e`




    Steps:
        1. Open results file
        2. Loop through model runs
        3. Create a CSV file with a row for each map unit and columns for:
            * Baseline
            * Baseline +14 days
            * Baseline -14 days

'''

# Most results contain duplicate for first year
def remove_duplicate_years(arr=[]):
    years = [dic["year"] for dic in arr]
    dup_year = ''
    for year in years:
        if years.count(year) > 1:
            dup_year = year
    if len(dup_year) > 0:
        for i in arr:
            if dup_year == i.get('year'):
                el = arr.pop(arr.index(i))
    return arr

def calc_co2_exchange(arr=[{"output": 0, "year": ""}]):
    arr = remove_duplicate_years(arr)
    arr_len = len(arr) - 1
    print(arr[arr_len]["output"])
    if arr_len > 0:
        area = map_unit_area(arr)
        calc = ((float(arr[0]["output"]) - float(arr[arr_len]["output"])) / arr_len) * (float(area)) * (1/100) * (44/12)
    return

def map_unit_area(arr=[]):
    # area should be same for each dict in list
    # so we only need the first
    return arr[0]['area']


def organize_by_year(data):
    main_dic = {}
    for key, value in data.items():
        variable = ''
        if value:
            for y in value:
                # y should contain the following keys:
                    # year, var, output, {var}, id, area, scenario
                year = str(y["year"])
                id = str(y["id"])
                area = str(y["area"])
                scenario = str(y["scenario"])
                if year not in main_dic.keys():
                    main_dic[year] = {
                        "year": year,
                        "id": id,
                        "area": area,
                        "scenario": scenario,
                    }
            for v in value:
                year = str(v["year"])
                variable = str(v["var"])
                output = str(v["output"])
                main_dic[year][variable] = output
    return main_dic

def parse_aggregate(elem, scenario):

    aggregate_data = {}
    scenario_name = scenario.lower()

    for child in elem.iter():
        xml_tag = str(child.tag)
        xml_tag = xml_tag.lower()
        xml_text = str(child.text)

        if (xml_tag == 'scenario'):
            aggregate_data['scenario'] = scenario_name
        else:
            aggregate_data[xml_tag] = xml_text

    return aggregate_data

def write_aggregate_csv(all_agg, xml_name):
    # write parsed aggregate to csv
    csv_file_name = xml_name + '.aggregate'
    dir_name = './results/'

    if not os.path.isdir(dir_name):
        os.mkdir(dir_name)

    aggregate_data_fieldnames = []

    for r in all_agg:

        for k,v in r.items():

            if k not in aggregate_data_fieldnames:
                aggregate_data_fieldnames.append(k)

        print(r)
    with open(dir_name + csv_file_name + '.csv', 'wt') as csvFile:
        writer = csv.DictWriter(csvFile, fieldnames=aggregate_data_fieldnames)
        writer.writeheader()
        for r in all_agg:
            writer.writerow(r)

    csvFile.close()

def parse_mapunit(elem, mapunit_id, area ,scenario):

    model_run_data = {}

    for child in elem.iter():
        xml_tag = str(child.tag)
        xml_tag = xml_tag.lower()
        xml_text = str(child.text)

        if (xml_tag in ( 'aagdefac', 'abgdefac', 'accrst', 'accrste_1_', 'agcprd', 'aglivc', 'bgdefac', 'bglivcm', 'rain', 'cgrain', 'cinput', 'crmvst', 'crootc', 'crpval', 'egracc_1_', 'eupacc_1_', 'fbrchc', 'fertac_1_', 'fertot_1_1_', 'frootcm', 'gromin_1_', 'irrtot', 'metabc_1_', 'metabc_2_', 'metabe_1_1_', 'metabe_2_1_', 'nfixac', 'omadac', 'omadae_1_', 'petann', 'rlwodc', 'somsc', 'somse_1_', 'stdedc', 'stdede_1_', 'strmac_1_', 'strmac_2_', 'strmac_6_', 'strucc_1_', 'struce_1_1_', 'struce_2_1_', 'tminrl_1_', 'tnetmn_1_', 'volpac' ) ):

            values = write_end_of_year_daycent_output( xml_tag, xml_text, scenario, mapunit_id, area )
            for value in values:
                if xml_tag not in model_run_data.keys():
                    model_run_data[xml_tag] = []
                model_run_data[xml_tag].append(value)

            if (xml_tag == 'somsc') :
                somsc = model_run_data[xml_tag]
                co2exchange = calc_co2_exchange(somsc)
                model_run_data['soil_carbon_exchange'] = co2exchange

        elif( xml_tag in ('irrigated', 'inputcrop' ) ):

            values = write_yearly_daycent_output( xml_tag, xml_text, scenario, mapunit_id, area )
            for value in values:
                if xml_tag not in model_run_data.keys():
                    model_run_data[xml_tag] = []
                model_run_data[xml_tag].append(value)

        elif( xml_tag in ('noflux', 'n2oflux', 'annppt') ):

            values = write_yearly_daycent_output92( xml_tag, xml_text, scenario, mapunit_id, area )
            for value in values:
                if xml_tag not in model_run_data.keys():
                    model_run_data[xml_tag] = []
                model_run_data[xml_tag].append(value)

        else:
            continue

    #  header fields
    values_array = ['year', 'scenario', 'id', 'area']

    for values in model_run_data:
        values_array.append(values)

    # write parsed out to csv
    csv_file_name = scenario
    dir_name = './results/' + mapunit_id + '/'

    if not os.path.isdir(dir_name):
        os.mkdir(dir_name)

    with open(dir_name + csv_file_name + '.csv', 'wt') as csvFile:
        writer = csv.DictWriter(csvFile, fieldnames=values_array)
        writer.writeheader()

        if model_run_data:
            org_by_year = organize_by_year(model_run_data)
            for k,v in org_by_year.items():
                writer.writerow(v)
    csvFile.close()


# Extract yearly output data from the DayCent variable for end-of-year value
# This function is used for API data with whole numbers representing the yearly output data
def write_yearly_daycent_output( daycent_variable, arrayText, scenario, mapunit, area ):

    if arrayText.endswith(','):
        arrayText = arrayText[:-1]

    arrayText = arrayText.replace( ':', ',' )
    array1 = arrayText.split(',')
    array1Length = len( array1 )
    daycent_variable = str(daycent_variable).lower()
    values = []

    for y in range( 0, (array1Length // 2) ):
        year_value = str( array1[ y * 2 ] )
        output_value = str( array1[ int(( y * 2 ) + 1) ] )
        yearly_output = {
            "year": year_value,
            "var": daycent_variable,
            "output": output_value,
            daycent_variable: output_value,
            "id": mapunit,
            "area": area,
            "scenario": scenario,
        }
        values.append(yearly_output)

    return values

# Extract only the end-of-year data from the DayCent variable
# These are pulled from the year_summary.out and similar files.
def write_end_of_year_daycent_output( daycent_variable, arrayText, scenario, mapunit, area ):

    if arrayText.endswith(','):
        arrayText = arrayText[:-1]

    arrayText = arrayText.replace( ':', ',' )
    array1 = arrayText.split(',')
    array1Length = len(array1)
    daycent_variable = str(daycent_variable).lower()
    values = []

    for y in range( 0, ( array1Length // 2) ):
        if '.' not in array1[ y * 2 ]:
            # print(array1[y * 2])
            year_value = str(int(array1[ y * 2 ]))
            output_value = str( array1[ int(( y * 2 ) + 1) ] )
            yearly_output = {
                "year": year_value,
                "var": daycent_variable,
                "output": output_value,
                daycent_variable: output_value,
                "id": mapunit,
                "area": area,
                "scenario": scenario,
            }
            values.append(yearly_output)

    return values

# Extract yearly output data from the DayCent variable for end-of-year value
# These are pulled from the year_summary.out and similar files.
def write_yearly_daycent_output92( daycent_variable, arrayText, scenario, mapunit, area ):

    if arrayText.endswith(','):
        arrayText = arrayText[:-1]

    array1 = arrayText.split(',')
    array1Length = len( array1 )
    daycent_variable = str(daycent_variable).lower()
    values = []

    for y in range( 0, ( array1Length // 2 ) ):
        if '.92' in array1[ y * 2 ]:
            year_value = str( array1[ y * 2 ][:4] )
            output_value = str( array1[ ( y * 2 ) + 1 ] )
            yearly_output = {
                "year": year_value,
                "var": daycent_variable,
                "output": output_value,
                daycent_variable: output_value,
                "id": mapunit,
                "area": area,
                "scenario": scenario,
            }
            values.append(yearly_output)

    return values


# Update the api_records_cropland table with the summary data produced by COMET-Farm
def update_gui_data(name, array_text, model_run_name, scenario):

    sql = [str(name), str(array_text), str(model_run_name), str(scenario)]
    print(sql)


def main():
    # check if argument has been given for xml
    if len(sys.argv) < 1:
        print("\nMissing argument.")
        pring("\npython3 script xml2csv.py <XML COMET-Farm Output>\n")
        print("<XML COMET-Farm Output> system location of XML output file from COMET-Farm\n")
        print("  eg /usr/local/name/comet/output.xml\n")
        exit()

    xml_name = sys.argv[1]

    start = datetime.now()
    print("\nStarting script at " + str( time.ctime( int( time.time( ) ) ) ) + "\n")
    print("----------------------------------------------------------------------")

    parsed_agg = []
    xml_file = open(xml_name, 'r+')

    # XML Parse
    tree = ET.parse(xml_name)
    root = tree.getroot()

    # old var from example script
    ModelRunNameArray = ''
    module = ''
    modelRunId = ''
    irrigated = ''
    mlra = ''
    practice = ''
    scenario = ''
    run_name = ''

    # variables thjat will be useful for future reference
    SoilCarbon = '0'
    SoilCarbonUncertainty = '0'
    SoilCarbonStock2000 = '0'
    SoilCarbonStockBegin = '0'
    SoilCarbonStockEnd = '0'
    SoilCarbonStock2000Uncertainty = '0'
    SoilCarbonStockBeginUncertainty = '0'
    SoilCarbonStockEndUncertainty = '0'
    BiomassBurningCarbon = '0'
    BiomassBurningCarbonUncertainty = '0'
    LimingCO2 = '0'
    LimingCO2Uncertainty = '0'
    UreaFertilizationCO2 = '0'
    UreaFertilizationCO2Uncertainty = '0'
    DrainedOrganicSoilsCO2 = '0'
    DrainedOrganicSoilsCO2Uncertainty = '0'
    SoilN2O = '0'
    SoilN2OUncertainty = '0'
    WetlandRiceCultivationN2O = '0'
    WetlandRiceCultivationN2OUncertainty = '0'
    BiomassBurningN2O = '0'
    BiomassBurningN2OUncertainty = '0'
    DrainedOrganicSoilsN2O = '0'
    DrainedOrganicSoilsN2OUncertainty = '0'
    SoilCH4 = '0'
    SoilCH4Uncertainty = '0'
    WetlandRiceCultivationCH4 = '0'
    WetlandRiceCultivationCH4Uncertainty = '0'
    BiomassBurningCH4 = '0'
    BiomassBurningCH4Uncertainty = '0'
    mapunit = '0'
    area = '0'

    #the output file is missing the carbon monoxide emissions from biomass burning
    BiomassBurningCO = '0'
    BiomassBurningCOUncertainty = '0'

    for elem in tree.iter():
        xmlTag = str( elem.tag )
        xmlAttrib = str( elem.attrib )
        xmlAttribName = str( elem.attrib.get( 'name' ) )
        xmlAttribId = str( elem.attrib.get( 'id' ) )
        xmlAttribArea = str( elem.attrib.get( 'area' ) )
        xmlText = str( elem.text )

        # Model run parameters that we do not want/need to process
        if ( xmlTag in ( 'Day', 'Cropland', 'CO2', 'N2O', 'CH4', 'BiomassBurningCarbonUncertainty', 'BiomassBurningCH4Uncertainty', 'BiomassBurningN2OUncertainty', 'C02', 'DrainedOrganicSoilsCO2Uncertainty', 'DrainedOrganicSoilsN2OUncertainty', 'LimingCO2Uncertainty', 'SoilCarbonUncertainty', 'SoilCH4Uncertainty', 'SoilN2OUncertainty', 'UreaFertilizationCO2Uncertainty', 'WetlandRiceCultivationCH4Uncertainty', 'WetlandRiceCultivationN2OUncertainty', 'AFDownedDeadWood', 'AFDownedDeadWoodUncertainty', 'AFForestFloor', 'AFForestFloorUncertainty', 'AFLiveTrees', 'AFLiveTreesUncertainty', 'AFStandingDeadTrees', 'AFStandingDeadTreesUncertainty', 'AFUnderstory', 'AFUnderstoryUncertainty', 'Agroforestry', 'Animal', 'FORDownedDeadWood', 'FORDownedDeadWoodUncertainty', 'Forestry', 'FORForestFloorUncertainty', 'FORInLandfills', 'FORInLandfillsUncertainty', 'FORLiveTrees', 'FORLiveTreesUncertainty', 'FORProductsInUse', 'FORProductsInUseUncertainty', 'FORSoilOrganicCarbon', 'FORSoilOrganicCarbonUncertainty', 'FORStandingDeadTreesUncertainty', 'FORUnderstory', 'FORUnderstoryUncertainty' ) ):
            continue

        if ( xmlTag == 'ModelRun' ):
            # get the module, id, irrigated, mlra, and practice
            ModelRunNameArray = xmlAttribName.split( '|' )
            module = str( ModelRunNameArray )
            irrigated = str( ModelRunNameArray )
            mlra = str( '?' )
            practice = str( ModelRunNameArray )
            modelRunName = xmlAttribName

        elif( "from reduced" in modelRunName ):
            # continue the loop but don't model this practice with the different baseline scenario
            continue

        # ====== Scenario
        elif( xmlTag == 'Scenario' ):

            scenarioFullName = xmlAttribName
            scenario = xmlAttribName

            if scenarioFullName.find( ' : FILE RESULTS' ) > -1:
                # generate the scenario name
                # used later for DayCent data within mapunit
                scenario = xmlAttribName[:-15]
            else:
                # aggregate results
                scenario_parsed = parse_aggregate(elem, scenario)
                parsed_agg.append(scenario_parsed)

        elif( "current" in scenario.lower() ):
            continue

        elif( "current" in scenario.lower() ):
            continue

        elif( xmlTag == "MapUnit" ):

            mapunit = xmlAttribId
            area = xmlAttribArea
            carbon = root.find('.//Carbon')

            # write csv file for scenario per map unit
            parse_mapunit(elem, mapunit, area, scenario)

            # give a status update for scipt user
            print("creating records for scenario = [" + str( scenario ) + "] and mapunit = [" + str( mapunit ) + "]")


        # process the GUI output data
        # elif( xmlTag == 'SoilCarbon' ):                 update_gui_data( "soil_carbon_co2", str( xmlText ), modelRunName, scenario)
        # elif( xmlTag == 'SoilCarbonStock2000' ):        update_gui_data( "soil_carbon_stock_2000", str( xmlText ), modelRunName, scenario)
        # elif( xmlTag == 'SoilCarbonStockBegin' ):       update_gui_data( "soil_carbon_stock_begin", str( xmlText ), modelRunName, scenario)
        # elif( xmlTag == 'SoilCarbonStockEnd' ):         update_gui_data( "soil_carbon_stock_end", str( xmlText ), modelRunName, scenario)
        # elif( xmlTag == 'BiomassBurningCarbon' ):       update_gui_data( "biomass_burning_co2", str( xmlText ), modelRunName, scenario)
        # elif( xmlTag == 'LimingCO2' ):                  update_gui_data( "liming_co2", str( xmlText ), modelRunName, scenario)
        # elif( xmlTag == 'UreaFertilizationCO2' ):       update_gui_data( "ureafertilization_co2", str( xmlText ), modelRunName, scenario)
        # elif( xmlTag == 'DrainedOrganicSoilsCO2' ):     update_gui_data( "drainedorganicsoils_co2", str( xmlText ), modelRunName, scenario)
        # elif( xmlTag == 'SoilN2O' ):                    update_gui_data( "soil_n2o", str( xmlText ), modelRunName, scenario)
        # elif( xmlTag == 'WetlandRiceCultivationN2O' ):  update_gui_data( "wetlandricecultivation_n2o", str( xmlText ), modelRunName, scenario)
        # elif( xmlTag == 'BiomassBurningN2O' ):          update_gui_data( "biomassburning_n2o", str( xmlText ), modelRunName, scenario)
        # elif( xmlTag == 'DrainedOrganicSoilsN2O' ):     update_gui_data( "drainedorganicsoils_n2o", str( xmlText ), modelRunName, scenario)
        # elif( xmlTag == 'SoilCH4' ):                    update_gui_data( "soil_ch4", str( xmlText ), modelRunName, scenario)
        # elif( xmlTag == 'WetlandRiceCultivationCH4' ):  update_gui_data( "wetlandricecultivation_ch4", str( xmlText ), modelRunName, scenario)
        # elif( xmlTag == 'BiomassBurningCH4' ):          update_gui_data( "biomassburning_ch4", str( xmlText ), modelRunName, scenario)

        else:
            continue

    write_aggregate_csv(parsed_agg, xml_name)

    # close the XML input file
    xml_file.close()

    print("----------------------------------------------------------------------")
    End = datetime.now( )
    print("Ending script at " + str( time.ctime( int( time.time( ) ) ) ))
    elapsed = End-start
    print("elapsed time = " + str( elapsed ))

main()









# all_rows = []
# header_row = []

# iter through the <Scenario> element's children to get key values
# for scenario_element in root.iter('Scenario'):
    # create list to store list of current iteration's value
    # tmp_list = []
    # iter through each elements children
    # for mapunit_run in scenario_element.iter():
        # some values we need are tags, some are attrbutes
        # first check for tags
        # if mapunit_run.tag != None:
            # add the tag
            # tmp_list.append(mapunit_run.tag)
        # next check for attributes
        # if mapunit_run.attrib != {}:
            # attributes are returned as a dict {'key, 'value'}
            # loop through the dict
            # for attribute in mapunit_run.attrib:
                # add only the key to our current list
                # tmp_list.append(attribute)
    # add the current iter values to the master list
    # header_row.append(tmp_list)

#  add header row to csv data
# all_rows.append(header_row)

# iter through the <Scenario> element's chlidren to get text value
# data_row = []
# for scenario_element in root.iter('Scenario'):
    # create list to store list of current iteration's value
    # tmp_list = []
    # iter through each elements children
    # for mapunit_run in scenario_element.iter():
        # some values we need are tags, some are attrbutes
        # first check for tags
        # if mapunit_run.tag != None:
            # add the tag
            # tmp_list.append(mapunit_run.text)
        # next check for attributes
        # if mapunit_run.attrib != {}:
            # loop through the dict
            # for attribute in mapunit_run.attrib:
                # tmp_list.append(mapunit_run.get(attribute))

    # data_row.append(tmp_list)
    # print(tmp_list)
# all_rows.append(data_row)

    #----- for mapunit in root.findall('MapUnit'):
        # mapunit_id = mapunit.get('id')
        # template_file = '../output/' + mapunit_id + '/' + scenario_name + '.csv'
        # open a file for writing
        # mapunit_data = open(template_file, 'w')

        # create the csv writer object
        # csvwriter = csv.writer(template_file)
        # mapunit_data = []
        # years = mapunit_data.find('Year')
        # mapunit_data.append(years)
        # csvwrite.writerow(mapunit_data)
        # print(mapunit_data)


# create csv file for aggregate results
# get aggregate from xml
# aggregate parameters:
#   carbon
# 	co2
# 	n2o
# 	ch4
# ----
