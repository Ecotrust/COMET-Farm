# import system modules
from datetime import datetime
import os, sys, csv, time, string, re, math
import xml.etree.ElementTree as ET
import pandas as pd
import ipdb
from os import listdir
from os.path import isfile, join

'''
    Overview of script
    ==================

    This script inputs XML from a COMET-Farm results email,
    then outputs a CSV file for each Map Unit.
    Steps:
        1. Open results file
        2. Loop through model runs
        3. Count the number of MapUnits for each Scenario
        4. Extract the following for each MapUnit:
            - Model run name
            - Model Run Id number
            - scenario
        5. Extract the model run results for each MapUnit
        6. Create CSV file for each MapUnit


'''

def writeToCSVFile(elem, mapunit_id, area ,scenario):

    model_run_data = {
        # "year": [],
        # "data": [],
        # "id": mapunit_id,
        # "area": area,
        # "scenario": scenario,
    }

    # for child in elem.iter() :
    #     xmlTag = str( child.tag )
    #     xmlAttrib = str( child.attrib )
    #     xmlAttribName = str( child.attrib.get( 'name' ) )
    #     xmlAttribId = str( child.attrib.get( 'id' ) )
    #     xmlAttribArea = str( child.attrib.get( 'area' ) )
    #     xml_text = str( child.text )

        # if (xmlTag == 'Year'):
            # years = xml_text.split(',')
            # for i in range(len(years)) :
                # year = years[i]
                # model_run_data["year"].append(str(year))
        # model_run_data["data"].append([xmlTag, xmlText])
        # print(xmlTag)
        # ipdb.set_trace()

        # print(model_run_data)

    # for child in elem.iter():
    #     xml_tag = str(child.tag)
    #     xml_text = str(child.text)

        # if (xml_tag.lower() not in ( 'Day', 'Cropland', 'Carbon', 'CO2', 'N2O', 'CH4', 'BiomassBurningCarbonUncertainty', 'BiomassBurningCH4Uncertainty', 'BiomassBurningN2OUncertainty', 'C02', 'DrainedOrganicSoilsCO2Uncertainty', 'DrainedOrganicSoilsN2OUncertainty', 'LimingCO2Uncertainty', 'SoilCarbonUncertainty', 'SoilCH4Uncertainty', 'SoilN2OUncertainty', 'UreaFertilizationCO2Uncertainty', 'WetlandRiceCultivationCH4Uncertainty', 'WetlandRiceCultivationN2OUncertainty', 'AFDownedDeadWood', 'AFDownedDeadWoodUncertainty', 'AFForestFloor', 'AFForestFloorUncertainty', 'AFLiveTrees', 'AFLiveTreesUncertainty', 'AFStandingDeadTrees', 'AFStandingDeadTreesUncertainty', 'AFUnderstory', 'AFUnderstoryUncertainty', 'Agroforestry', 'Animal', 'FORDownedDeadWood', 'FORDownedDeadWoodUncertainty', 'Forestry', 'FORForestFloorUncertainty', 'FORInLandfills', 'FORInLandfillsUncertainty', 'FORLiveTrees', 'FORLiveTreesUncertainty', 'FORProductsInUse', 'FORProductsInUseUncertainty', 'FORSoilOrganicCarbon', 'FORSoilOrganicCarbonUncertainty', 'FORStandingDeadTreesUncertainty', 'FORUnderstory', 'FORUnderstoryUncertainty' ) ):
            # if xml_tag not in model_run_data:
                # model_run_data[xml_tag] = []

    for child in elem.iter():
        xml_tag = str(child.tag)
        xml_tag = xml_tag.lower()
        xml_text = str(child.text)

        if (xml_tag in ( 'aagdefac', 'abgdefac', 'accrst', 'accrste_1_', 'agcprd', 'aglivc', 'bgdefac', 'bglivcm', 'cgrain', 'cinput', 'crmvst', 'crootc', 'crpval', 'egracc_1_', 'eupacc_1_', 'fbrchc', 'fertac_1_', 'fertot_1_1_', 'frootcm', 'gromin_1_', 'irrtot', 'metabc_1_', 'metabc_2_', 'metabe_1_1_', 'metabe_2_1_', 'nfixac', 'omadac', 'omadae_1_', 'petann', 'rlwodc', 'somsc', 'somse_1_', 'stdedc', 'stdede_1_', 'strmac_1_', 'strmac_2_', 'strmac_6_', 'strucc_1_', 'struce_1_1_', 'struce_2_1_', 'tminrl_1_', 'tnetmn_1_', 'volpac' ) ):
            if scenario == 'Baseline':
                values = writeEndOfYearDayCentOutput( xml_tag, str( xml_text ), 'baseline', mapunit_id, area )
                for i in range(len(values)) :
                    value = values[i]
                    model_run_data[xml_tag] = value
            else:
                # model_run.append([mapunit, scenario, xmlTag.lower(), xmlText])
                values = writeEndOfYearDayCentOutput( xml_tag.lower(), str( xml_text ), 'scenario', mapunit_id, area )
                for value in values:
                    # value = values[i]
                    model_run_data[xml_tag] = value
                # model_run_data[xml_tag] = values

            # transposed = []
            # for i in range(len(model_run_data)):
                # transposed.append([row[i] for row in model_run_data[xml_tag]])

    # print(model_run_data)

    #  header fields
    values_array = ['year', 'id', 'area',]
    count = 0
    for values in model_run_data:
        values_array.append(values)

    # write parsed out to csv
    csv_file_name = mapunit_id + scenario
    os.mkdir(mapunit_id)
    with open('./' + mapunit_id + '/' + csv_file_name + '.csv', 'wt') as csvFile:
        writer = csv.DictWriter(csvFile, fieldnames=values_array)
        writer.writeheader()

        if model_run_data:
            # writer.writerow(model_run_data)
            for row in model_run_data:
                print(model_run_data[row])
                writer.writerow(model_run_data[row])
            # for value in values:
                    # print(value)
                    # values_array.append(values[i])

                # writer.writerow(values_array)

    csvFile.close()


# Extract yearly output data from the DayCent variable and insert the end-of-year value into the database
# This function is used for API data with whole numbers representing the yearly output data
# For example, the records with the date value of "2003" refer to "2003".
def writeYearlyDayCentOutput( daycent_variable, arrayText, baselineOrScenario, mapunit, area ):
    arrayText = arrayText.replace( ':', ',' )
    array1 = arrayText.split(',')
    array1Length = len( array1 )
    daycent_variable = str(daycent_variable).lower()

    values = []

    for y in range( 2, ( array1Length // 2 ) ):
        if '.' not in array1[ y * 2 ]:
            # print(array1[y * 2])
            year_value = str( int( array1[ y * 2 ] ) - 1 )
            output_value = str( array1[ ( y * 2 ) + 1 ] )
            yearly_output = {
                "year": year_value,
                # "value": output_value,
                daycent_variable: output_value,
                "id": mapunit,
                "area": area,
            }
            values.append(yearly_output)

    return values

    # print(daycent_variable)
    # print(arrayText)
    # year_value = [str(array1[x]) for x in range(array1Length) if x % 2 == 0]
    # output_value = [str(array1[x]) for x in range(array1Length) if x % 2 == 1]
    # ipdb.set_trace()
    # for y in range( 0, ( array1Length ) ):
        # print('y = ' + str(y))
        # if y > (array1Length // 2):
            # year_value = str( int( array1[ y * 2 ] ) )
            # output_value = str( array1[ ( y * 2 ) + 1 ] )

            # print(year_value)
        # sql = "INSERT INTO " + str( databaseName ) + ".api_results_cropland_daycent_" + str( baselineOrScenario ) + "_" + daycent_variable + " ( id_api_results_cropland_daycent_master, date_value, output_value ) VALUE ( '" + str( id_api_results_cropland_daycent_master ) + "', '" + str( year_value ) + "', '" + str( output_value ) + "' );"
        # try:
            # cursor_daycent.execute( sql )
        # except mariadb_daycent.Error as error:
            # print( "Error: {}".format( error ) )
#  TODO: Output CSV
            # print(output_value)

# Extract only the end-of-year data from the DayCent variable
# These are pulled from the year_summary.out and similar files.
# For example, the records with the date value of "2003" refer to "2003".
def writeEndOfYearDayCentOutput( daycent_variable, arrayText, baselineOrScenario, mapunit, area ):
    arrayText = arrayText.replace( ':', ',' )
    array1 = arrayText.split(',')
    array1Length = len( array1 )
    daycent_variable = str(daycent_variable).lower()

    values = []
    print(array1)

    for y in range( 2, ( array1Length // 2 ) ):
        # if '.' not in array1[ y * 2 ]:
            # print(array1[y * 2])
        year_value = str( int( array1[ y * 2 ] ) - 1 )
        output_value = str( array1[ ( y * 2 ) + 1 ] )
        yearly_output = {
            "year": year_value,
            # "value": output_value,
            daycent_variable: output_value,
            "id": mapunit,
            "area": area,
        }
        values.append(yearly_output)

            # writeToCSVFile([{daycent_variable, }])
            # sql = "INSERT INTO " + str( databaseName ) + ".api_results_cropland_daycent_" + str( baselineOrScenario ) + "_" + daycent_variable + " ( id_api_results_cropland_daycent_master, date_value, output_value ) VALUE ( '" + str( id_api_results_cropland_daycent_master ) + "', '" + str( year_value ) + "', '" + str( output_value ) + "' );"
            # try:
                # cursor_daycent.execute( sql )
            #  TODO: Output CSV
            # print(output_value)
            # except mariadb_daycent.Error as error:
                # print( "Error: {}".format( error ) )
    return values

# Extract yearly output data from the DayCent variable and insert the end-of-year value into the database
# These are pulled from the year_summary.out and similar files.
# For example, the records with the date value of "2003.92" are truncated to "2003"
def writeYearlyDayCentOutput92( daycent_variable, arrayText, baselineOrScenario, mapunit, area ):
    array1 = arrayText.split(',')
    array1Length = len( array1 )

    if array1Length == 1:
        return
    else:
        for y in range( 0, ( array1Length // 2 ) ):
            if '.92' in array1[ y * 2 ]:
                year_value = str( array1[ y * 2 ][:4] )
                output_value = str( array1[ ( y * 2 ) + 1 ] )
                # print(year_value)
                # sql = "INSERT INTO " + str( databaseName ) + ".api_results_cropland_daycent_" + str( baselineOrScenario ) + "_" + daycent_variable + " ( id_api_results_cropland_daycent_master, date_value, output_value ) VALUE ( '" + str( id_api_results_cropland_daycent_master ) + "', '" + str( year_value ) + "', '" + str( output_value ) + "' );"
                # try:
                    # cursor_daycent.execute( sql )
                #  TODO: Output CSV
                # print(year_value)
                # except mariadb_daycent.Error as error:
                    # print( "Error: {}".format( error ) )


# Update the api_records_cropland table with the summary data produced by COMET-Farm
def updateGUIdata( variableToUpdate2, updatedValue2, modelRunName, scenario):

    sql = [str( variableToUpdate2 ), str( updatedValue2 ), str( modelRunName), str(scenario)]
    # runSQL( sql )
    #  TODO: Output CSV
    # print(sql)

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

    print("")
    print("Starting script at " + str( time.ctime( int( time.time( ) ) ) ))
    print("")

    print("----------------------------------------------------------------------")

    xml_file = open(xml_name, 'r+')

    # XML Parse
    tree = ET.parse(xml_name)
    root = tree.getroot()

    ModelRunNameArray = ''
    module = ''
    modelRunId = ''
    irrigated = ''
    mlra = ''
    practice = ''
    scenario = ''

    model_run = []
    mapunit_ids = []
    mapunits_data = {}

    run_name = ''

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

    #count the number of scenarios
    scenarioCount = 0

    for elem in tree.iter():
        if ( str( elem.tag ) == 'Scenario' ):
            scenarioCount = scenarioCount + 1

    # get title row values
    mapunit_count = 0
    header_row = []
    for elem in tree.iter():
        # use the elem tags in the first mapunit
        # prevents multiple writes to list
        # all mapunits should have matching elem.tags'
        if ( str( elem.tag ) == 'MapUnit' ):
            mapunit_count = mapunit_count + 1
        if mapunit_count < 2:
            if ( elem.tag not in ( 'Day', 'Cropland', 'Carbon', 'CO2', 'N2O', 'CH4', 'BiomassBurningCarbonUncertainty', 'BiomassBurningCH4Uncertainty', 'BiomassBurningN2OUncertainty', 'C02', 'DrainedOrganicSoilsCO2Uncertainty', 'DrainedOrganicSoilsN2OUncertainty', 'LimingCO2Uncertainty', 'SoilCarbonUncertainty', 'SoilCH4Uncertainty', 'SoilN2OUncertainty', 'UreaFertilizationCO2Uncertainty', 'WetlandRiceCultivationCH4Uncertainty', 'WetlandRiceCultivationN2OUncertainty', 'AFDownedDeadWood', 'AFDownedDeadWoodUncertainty', 'AFForestFloor', 'AFForestFloorUncertainty', 'AFLiveTrees', 'AFLiveTreesUncertainty', 'AFStandingDeadTrees', 'AFStandingDeadTreesUncertainty', 'AFUnderstory', 'AFUnderstoryUncertainty', 'Agroforestry', 'Animal', 'FORDownedDeadWood', 'FORDownedDeadWoodUncertainty', 'Forestry', 'FORForestFloorUncertainty', 'FORInLandfills', 'FORInLandfillsUncertainty', 'FORLiveTrees', 'FORLiveTreesUncertainty', 'FORProductsInUse', 'FORProductsInUseUncertainty', 'FORSoilOrganicCarbon', 'FORSoilOrganicCarbonUncertainty', 'FORStandingDeadTreesUncertainty', 'FORUnderstory', 'FORUnderstoryUncertainty' ) ):
                header_row.append(str(elem.tag))

    model_run.append(header_row)

    # print(model_run)

    #process the scenarios
    recordCount = 1

    for elem in tree.iter():
        xmlTag = str( elem.tag )
        xmlAttrib = str( elem.attrib )
        xmlAttribName = str( elem.attrib.get( 'name' ) )
        xmlAttribId = str( elem.attrib.get( 'id' ) )
        xmlAttribArea = str( elem.attrib.get( 'area' ) )
        xmlText = str( elem.text )

        #Steps to process:
        # - Model Run Name
        if ( xmlTag in ( 'Day', 'Cropland', 'Carbon', 'CO2', 'N2O', 'CH4', 'BiomassBurningCarbonUncertainty', 'BiomassBurningCH4Uncertainty', 'BiomassBurningN2OUncertainty', 'C02', 'DrainedOrganicSoilsCO2Uncertainty', 'DrainedOrganicSoilsN2OUncertainty', 'LimingCO2Uncertainty', 'SoilCarbonUncertainty', 'SoilCH4Uncertainty', 'SoilN2OUncertainty', 'UreaFertilizationCO2Uncertainty', 'WetlandRiceCultivationCH4Uncertainty', 'WetlandRiceCultivationN2OUncertainty', 'AFDownedDeadWood', 'AFDownedDeadWoodUncertainty', 'AFForestFloor', 'AFForestFloorUncertainty', 'AFLiveTrees', 'AFLiveTreesUncertainty', 'AFStandingDeadTrees', 'AFStandingDeadTreesUncertainty', 'AFUnderstory', 'AFUnderstoryUncertainty', 'Agroforestry', 'Animal', 'FORDownedDeadWood', 'FORDownedDeadWoodUncertainty', 'Forestry', 'FORForestFloorUncertainty', 'FORInLandfills', 'FORInLandfillsUncertainty', 'FORLiveTrees', 'FORLiveTreesUncertainty', 'FORProductsInUse', 'FORProductsInUseUncertainty', 'FORSoilOrganicCarbon', 'FORSoilOrganicCarbonUncertainty', 'FORStandingDeadTreesUncertainty', 'FORUnderstory', 'FORUnderstoryUncertainty' ) ):
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

        # - Scenario
        elif( xmlTag == 'Scenario' ):

            scenarioFullName = xmlAttribName
            scenario = xmlAttribName

            if scenarioFullName.find( ' : FILE RESULTS' ) > -1:
                # generate the scenario name to use further down in the script for the DayCent data when the mapunit tag is reached
                scenario = xmlAttribName[:-15]

            if ( "from reduced" not in scenario.lower() and "current" not in scenario.lower() ):
                # run_name = '"' + str( modelRunName ) + "', '" + str( ) + "', '" + str( mlra ) + "', '" + str( practice ) + "', '" + str( scenario ) + "', '" + str( irrigated ) + '"'
                print("creating records for scenario = [" + str( scenario ) + "] and mapunit = [" + str( scenarioFullName ) + "]")

        elif( "current" in scenario.lower() ):
            continue

        elif( "current" in scenario.lower() ):
            continue

        elif( xmlTag == "MapUnit" ):

            mapunit = xmlAttribId
            area = xmlAttribArea

            writeToCSVFile(elem, mapunit, area, scenario)

            mapunit_ids.append(mapunit)

            model_run.append([mapunit, scenario, xmlTag.lower(), xmlText])

            if scenario == 'Baseline':
                # create the master records
                print("creating records for scenario = [" + str( scenario ) + "] and mapunit = [" + str( mapunit ) + "]")
            else:

                print("creating records for scenario = [" + str( scenario ) + "] and mapunit = [" + str( mapunit ) + "]")

                # find any existing masterId record and delete the records from the daycent value tables that correspond
                # sql = "SELECT id as masterId FROM " + str( databaseName ) + ".api_results_cropland_daycent_scenario_master WHERE name = '" + modelRunName + "' and id_mlra_crops_from_cdl_2009_2015 = '" + str( modelRunId ) + "' and mlra = '" + str( mlra ) + "' and practice = '" + str( practice ) + "' and scenario = '" + str( scenario ) + "' and irrigated = '" + str( irrigated ) + "' and mapunit = '" + str( mapunit ) + "';"
                #print "      ...sql = " + sql


                # for ( masterId ) in cursor_master:
                    # id_api_results_cropland_daycent_master = masterId[0]
                    # id_api_results_cropland_daycent_master

                    # create a master record in the DayCent master file and then get the id number back
                    # sql = "DELETE FROM " + str( databaseName ) + ".api_results_cropland_daycent_scenario_master WHERE name = '" + str( modelRunName ) + "' AND id_mlra_crops_from_cdl_2009_2015 = '" + str( modelRunId ) + "' AND mlra = '" + str( mlra ) + "' AND practice =  '" + str( practice ) + "' AND scenario = '" + str( scenario ) + "' AND irrigated = '" + str( irrigated ) + "' and mapunit = '" + str( mapunit ) + "';"
                    #print "      ...sql = " + sql
                    # runSQL( sql, mariadb_connection, cursor )

                    # delete the records in the daycent data child tables for this master record
                    # for ( daycent2 ) in ( 'InputCrop', 'Irrigated', 'Year', 'aagdefac', 'abgdefac', 'accrst', 'accrste_1_', 'agcprd', 'aglivc', 'annppt', 'bgdefac', 'bglivcm', 'cgrain', 'cinput', 'crmvst', 'crootc', 'crpval', 'egracc_1_', 'eupacc_1_', 'fbrchc', 'fertac_1_', 'fertot_1_1_', 'frootcm', 'gromin_1_', 'irrtot', 'metabc_1_', 'metabc_2_', 'metabe_1_1_', 'metabe_2_1_', 'n2oflux', 'nfixac', 'noflux', 'omadac', 'omadae_1_', 'petann', 'rlwodc', 'somsc', 'somse_1_', 'stdedc', 'stdede_1_', 'strmac_1_', 'strmac_2_', 'strmac_6_', 'strucc_1_', 'struce_1_1_', 'struce_2_1_', 'tminrl_1_', 'tnetmn_1_', 'volpac' ):
                        # sql = "DELETE FROM " + str( databaseName ) + ".api_results_cropland_daycent_scenario_" + daycent2.lower() + " WHERE id_api_results_cropland_daycent_master = " + str( id_api_results_cropland_daycent_master ) + ";"

                        # runSQL( sql, mariadb_connection, cursor )

                #insert the new record
                # sql = "INSERT INTO " + str( databaseName ) + ".api_results_cropland_daycent_scenario_master ( name, id_mlra_crops_from_cdl_2009_2015, mlra, practice, scenario, irrigated, mapunit, area ) VALUES ('" + str( modelRunName ) + "', '" + str( modelRunId ) + "', '" + str( mlra ) + "', '" + str( practice ) + "', '" + str( scenario ) + "', '" + str( irrigated ) + "', '" + str( mapunit ) + "', '" + str( area ) + "' );"

                # runSQL( sql, mariadb_connection, cursor )

                #get the new master record id
                # sql = "SELECT id as masterId FROM " + str( databaseName ) + ".api_results_cropland_daycent_scenario_master WHERE name = '" + modelRunName + "' and id_mlra_crops_from_cdl_2009_2015 = '" + str( modelRunId ) + "' and mlra = '" + str( mlra ) + "' and practice = '" + str( practice ) + "' and scenario = '" + str( scenario ) + "' and irrigated = '" + str( irrigated ) + "' and mapunit = '" + str( mapunit ) + "';"

        # process the DayCent output data
        # elif( xmlTag.lower() in ( 'aagdefac', 'abgdefac', 'accrst', 'accrste_1_', 'agcprd', 'aglivc', 'bgdefac', 'bglivcm', 'cgrain', 'cinput', 'crmvst', 'crootc', 'crpval', 'egracc_1_', 'eupacc_1_', 'fbrchc', 'fertac_1_', 'fertot_1_1_', 'frootcm', 'gromin_1_', 'irrtot', 'metabc_1_', 'metabc_2_', 'metabe_1_1_', 'metabe_2_1_', 'nfixac', 'omadac', 'omadae_1_', 'petann', 'rlwodc', 'somsc', 'somse_1_', 'stdedc', 'stdede_1_', 'strmac_1_', 'strmac_2_', 'strmac_6_', 'strucc_1_', 'struce_1_1_', 'struce_2_1_', 'tminrl_1_', 'tnetmn_1_', 'volpac' ) ):

            # print(xmlTag)
            # if scenario == 'Baseline':
                # get_data_array = writeEndOfYearDayCentOutput( xmlTag.lower(), str( xmlText ), 'baseline', mapunit )
                # get_data_array = [mapunit, scenario] + get_data_array
                # model_run.append(get_data_array)
            # else:
                # model_run.append([mapunit, scenario, xmlTag.lower(), xmlText])
                # writeEndOfYearDayCentOutput( xmlTag.lower(), str( xmlText ), 'scenario', mapunit )

            # print(model_run)
        # elif( xmlTag.lower() in ( 'year', 'irrigated', 'inputcrop' ) ):

            # if scenario == 'Baseline':
                # writeYearlyDayCentOutput( xmlTag.lower(), str( xmlText ), 'baseline', mapunit )
            # else:
                # writeYearlyDayCentOutput( xmlTag.lower(), str( xmlText ), 'scenario', mapunit )

        # elif( xmlTag.lower() in ( 'noflux', 'n2oflux', 'annppt' ) ):

            # if scenario == 'Baseline':
                # writeYearlyDayCentOutput92( xmlTag.lower(), str( xmlText ), 'baseline', mapunit )
            # else:
                # writeYearlyDayCentOutput92( xmlTag.lower(), str( xmlText ), 'scenario', mapunit )

        # process the GUI output data
        # elif( xmlTag == 'SoilCarbon' ):                 updateGUIdata( "soil_carbon_co2", str( xmlText ), modelRunName, scenario)
        # elif( xmlTag == 'SoilCarbonStock2000' ):        updateGUIdata( "soil_carbon_stock_2000", str( xmlText ), modelRunName, scenario)
        # elif( xmlTag == 'SoilCarbonStockBegin' ):       updateGUIdata( "soil_carbon_stock_begin", str( xmlText ), modelRunName, scenario)
        # elif( xmlTag == 'SoilCarbonStockEnd' ):         updateGUIdata( "soil_carbon_stock_end", str( xmlText ), modelRunName, scenario)
        # elif( xmlTag == 'BiomassBurningCarbon' ):       updateGUIdata( "biomass_burning_co2", str( xmlText ), modelRunName, scenario)
        # elif( xmlTag == 'LimingCO2' ):                  updateGUIdata( "liming_co2", str( xmlText ), modelRunName, scenario)
        # elif( xmlTag == 'UreaFertilizationCO2' ):       updateGUIdata( "ureafertilization_co2", str( xmlText ), modelRunName, scenario)
        # elif( xmlTag == 'DrainedOrganicSoilsCO2' ):     updateGUIdata( "drainedorganicsoils_co2", str( xmlText ), modelRunName, scenario)
        # elif( xmlTag == 'SoilN2O' ):                    updateGUIdata( "soil_n2o", str( xmlText ), modelRunName, scenario)
        # elif( xmlTag == 'WetlandRiceCultivationN2O' ):  updateGUIdata( "wetlandricecultivation_n2o", str( xmlText ), modelRunName, scenario)
        # elif( xmlTag == 'BiomassBurningN2O' ):          updateGUIdata( "biomassburning_n2o", str( xmlText ), modelRunName, scenario)
        # elif( xmlTag == 'DrainedOrganicSoilsN2O' ):     updateGUIdata( "drainedorganicsoils_n2o", str( xmlText ), modelRunName, scenario)
        # elif( xmlTag == 'SoilCH4' ):                    updateGUIdata( "soil_ch4", str( xmlText ), modelRunName, scenario)
        # elif( xmlTag == 'WetlandRiceCultivationCH4' ):  updateGUIdata( "wetlandricecultivation_ch4", str( xmlText ), modelRunName, scenario)
        # elif( xmlTag == 'BiomassBurningCH4' ):          updateGUIdata( "biomassburning_ch4", str( xmlText ), modelRunName, scenario)
        else:
            continue

    # for i in range(mapunit_count):
        # mapunits_data.append(mapunits_data)

    mapunit_ids = set(mapunit_ids)

    #close the XML input file
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
