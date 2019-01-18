# Import system modules
from datetime import datetime
import os, sys, time, MySQLdb, string, re, math
import xml.etree.ElementTree as ET
#import mysql.connector as mariadb
from os import listdir
from os.path import isfile, join
import zipfile
from subprocess import call
import shutil
import warnings
warnings.filterwarnings( "ignore", "Unknown table.*" )

'''

Mark Easter, 18 January 2017

This script opens a COMET-Farm API results file and writes the data to a database.  Steps:
    1) Open a results file
    2) Loop through the Model Runs
    3) Extract the following from the scenario name:
        - Model run name
        - Model Run Id number
        - conservation practice name
        - rotation name
        - MLRA
        - scenario
        - irrigated (Y/N)
    4) Extract the model run results
    5) Build an SQL String
    6) Delete any existing records for the same model run
    5) Insert the data into the table api_results_cropland, or api_results_forestry, or api_results_agroforestry, or api_results_livestock

Script processing syntax:

        print "\n"
        print "python script ReadResults.py <zipOrxml> <fileOrDirectory> <FileOrDirectoryName> <croplandOrGrassland> <database name>"
        print "\n"
        print "Command-line arguments are as follows:"
        print "   <zipOrxml> use word 'zip' to indicate data are in zip file format, or 'xml' to indicate xml file format"
        print "   <fileOrDirectory> use the word 'file' to indicate the input files are in file format, 'directory' indicates intent to import a set of files in a directory "
        print "   <fileOrDirectoryName> fully-qualified path to the input file name or the directory containing the input files"
        print "   <croplandOrGrassland> use the word 'cropland' to indicate data are from a cropland system, or 'grassland' to indicate data are from a grassland system"
        print "   <database name> name of the tusker database to which these data are to be saved"
        print ""

Table comet.api_results_cropland:

+----------------------------------------+--------------+------+-----+---------+-------+
| Field                                  | Type         | Null | Key | Default | Extra |
+----------------------------------------+--------------+------+-----+---------+-------+
| name                                   | varchar(250) | YES  |     | NULL    |       |
| id_mlra_crops_from_cdl_2009_2015       | int(11)      | YES  | MUL | NULL    |       |
| id_mlra_grass_from_cdl_2009_2015       | int(11)      | YES  | MUL | NULL    |       |
| mlra                                   | varchar(5)   | YES  |     | NULL    |       |
| practice                               | varchar(125) | YES  |     | NULL    |       |
| scenario                               | varchar(125) | YES  |     | NULL    |       |
| irrigated                              | char(1)      | NO   |     | NULL    |       |
| soil_carbon_co2                        | float        | YES  |     | NULL    |       |
| soil_carbon_co2_uncertainty             | float        | YES  |     | NULL    |       |
# 3/29/2017 MJE, Added the following float null fields
    - SoilCarbonStock2000
    - SoilCarbonStock2000Uncertainty
    - SoilCarbonStockBegin
    - SoilCarbonStockBeginUncertainty
    - SoilCarbonStockEnd
    - SoilCarbonStockEndUncertainty
| soil_n2o                               | float        | YES  |     | NULL    |       |
| soil_n2o_uncertainty                    | float        | YES  |     | NULL    |       |
| biomass_burning_co2                    | float        | YES  |     | NULL    |       |
| biomass_burning_co2_uncertainty         | float        | YES  |     | NULL    |       |
| liming_co2                             | float        | YES  |     | NULL    |       |
| liming_co2_uncertainty                  | float        | YES  |     | NULL    |       |
| ureafertilization_co2                  | float        | YES  |     | NULL    |       |
| ureafertilization_co2_uncertainty       | float        | YES  |     | NULL    |       |
| drainedorganicsoils_co2                | float        | YES  |     | NULL    |       |
| drainedorganicsoils_co2_uncertainty     | float        | YES  |     | NULL    |       |
| biomassburning_co                      | float        | YES  |     | NULL    |       |
| biomassburning_co_uncertainty           | float        | YES  |     | NULL    |       |
| wetlandricecultivation_n2o             | float        | YES  |     | NULL    |       |
| wetlandricecultivation_n2o_uncertainty  | float        | YES  |     | NULL    |       |
| biomassburning_n2o                     | float        | YES  |     | NULL    |       |
| biomassburning_n2o_uncertainty          | float        | YES  |     | NULL    |       |
| drainedorganicsoils_n2o                | float        | YES  |     | NULL    |       |
| drainedorganicsoils_n2o_uncertainty     | float        | YES  |     | NULL    |       |
| soil_ch4                               | float        | YES  |     | NULL    |       |
| soil_ch4_uncertainty                    | float        | YES  |     | NULL    |       |
| wetlandricecultivation_ch4             | float        | YES  |     | NULL    |       |
| wetlandricecultivation_ch4_uncertainty  | float        | YES  |     | NULL    |       |
| biomassburning_ch4                     | float        | YES  |     | NULL    |       |
| biomassburning_ch4_uncertainty          | float        | YES  |     | NULL    |       |
+----------------------------------------+--------------+------+-----+---------+-------+

Table comet.api_results_agroforestry:

+-----------------------------------+--------------+------+-----+---------+-------+
| Field                             | Type         | Null | Key | Default | Extra |
+-----------------------------------+--------------+------+-----+---------+-------+
| name                              | varchar(250) | YES  |     | NULL    |       |
| fips                              | mediumint(9) | YES  | MUL | NULL    |       |
| mlra                              | varchar(5)   | YES  | MUL | NULL    |       |
| practice                          | varchar(125) | YES  |     | NULL    |       |
| scenario                          | varchar(125) | YES  |     | NULL    |       |
| livetrees_co2                     | float        | YES  |     | NULL    |       |
| livetrees_co2Uncertainty         | float        | YES  |     | NULL    |       |
| downeddeadwood_co2                | float        | YES  |     | NULL    |       |
| downeddeadwood_co2Uncertainty    | float        | YES  |     | NULL    |       |
| forestfloor_co2                   | float        | YES  |     | NULL    |       |
| forestfloor_co2Uncertainty       | float        | YES  |     | NULL    |       |
| standingdeadtrees_co2             | float        | YES  |     | NULL    |       |
| standingdeadtrees_co2Uncertainty | float        | YES  |     | NULL    |       |
| understory_co2                    | float        | YES  |     | NULL    |       |
| understory_co2Uncertainty        | float        | YES  |     | NULL    |       |
+-----------------------------------+--------------+------+-----+---------+-------+

Table comet.api_results_livestock:

+----------------------------------------------+--------------+------+-----+---------+-------+
| Field                                        | Type         | Null | Key | Default | Extra |
+----------------------------------------------+--------------+------+-----+---------+-------+
| name                                         | varchar(250) | YES  |     | NULL    |       |
| fips                                         | mediumint(9) | YES  | MUL | NULL    |       |
| mlra                                         | varchar(5)   | YES  | MUL | NULL    |       |
| practice                                     | varchar(125) | YES  |     | NULL    |       |
| scenario                                     | varchar(125) | YES  |     | NULL    |       |
| enteric_ch4                                  | float        | YES  |     | NULL    |       |
| enteric_ch4_uncertainty                      | float        | YES  |     | NULL    |       |
| housing_ch4                                  | float        | YES  |     | NULL    |       |
| housing_ch4_uncertainty                      | float        | YES  |     | NULL    |       |
| barnhousing_ch4                              | float        | YES  |     | NULL    |       |
| barnhousing_ch4_uncertainty                  | float        | YES  |     | NULL    |       |
| termporaryandlongtermstorage_ch4             | float        | YES  |     | NULL    |       |
| termporaryandlongtermstorage_ch4_uncertainty | float        | YES  |     | NULL    |       |
| composting_ch4                               | float        | YES  |     | NULL    |       |
| composting_ch4_uncertainty                   | float        | YES  |     | NULL    |       |
| thermochemicalconversion_ch4                 | float        | YES  |     | NULL    |       |
| thermochemicalconversion_ch4_uncertainty     | float        | YES  |     | NULL    |       |
| aerobiclagoon_ch4                            | float        | YES  |     | NULL    |       |
| aerobiclagoon_ch4_uncertainty                | float        | YES  |     | NULL    |       |
| anaerobiclagoon_ch4                          | float        | YES  |     | NULL    |       |
| anaerobiclagoon_ch4_uncertainty              | float        | YES  |     | NULL    |       |
| combinedaerobictreatment_ch4                 | float        | YES  |     | NULL    |       |
| combinedaerobictreatment_ch4_uncertainty     | float        | YES  |     | NULL    |       |
| anaerobicdigester_ch4                        | float        | YES  |     | NULL    |       |
| anaerobicdigester_ch4_uncertainty            | float        | YES  |     | NULL    |       |
| housing_n2o                                  | float        | YES  |     | NULL    |       |
| housing_n2o_uncertainty                      | float        | YES  |     | NULL    |       |
| barnhousing_n2o                              | float        | YES  |     | NULL    |       |
| barnhousing_n2o_uncertainty                  | float        | YES  |     | NULL    |       |
| termporaryandlongtermstorage_n2o             | float        | YES  |     | NULL    |       |
| termporaryandlongtermstorage_n2o_uncertainty | float        | YES  |     | NULL    |       |
| composting_n2o                               | float        | YES  |     | NULL    |       |
| composting_n2o_uncertainty                   | float        | YES  |     | NULL    |       |
| thermochemicalconversion_n2o                 | float        | YES  |     | NULL    |       |
| thermochemicalconversion_n2o_uncertainty     | float        | YES  |     | NULL    |       |
| aerobiclagoon_n2o                            | float        | YES  |     | NULL    |       |
| aerobiclagoon_n2o_uncertainty                | float        | YES  |     | NULL    |       |
| anaerobiclagoon_n2o                          | float        | YES  |     | NULL    |       |
| anaerobiclagoon_n2o_uncertainty              | float        | YES  |     | NULL    |       |
| combinedaerobictreatment_n2o                 | float        | YES  |     | NULL    |       |
| combinedaerobictreatment_n2o_uncertainty     | float        | YES  |     | NULL    |       |
| anaerobicdigester_n2o                        | float        | YES  |     | NULL    |       |
| anaerobicdigester_n2o_uncertainty            | float        | YES  |     | NULL    |       |
+----------------------------------------------+--------------+------+-----+---------+-------+

Table comet.api_results_forestry:

+-----------------------------------+--------------+------+-----+---------+-------+
| Field                             | Type         | Null | Key | Default | Extra |
+-----------------------------------+--------------+------+-----+---------+-------+
| name                              | varchar(250) | YES  |     | NULL    |       |
| fips                              | mediumint(9) | YES  | MUL | NULL    |       |
| mlra                              | varchar(5)   | YES  | MUL | NULL    |       |
| practice                          | varchar(125) | YES  |     | NULL    |       |
| scenario                          | varchar(125) | YES  |     | NULL    |       |
| livetrees_co2                     | float        | YES  |     | NULL    |       |
| certainty                         | float        | YES  |     | NULL    |       |
| standingdeadtrees_co2             | float        | YES  |     | NULL    |       |
| standingdeadtrees_co2Uncertainty | float        | YES  |     | NULL    |       |
| forestfloor_co2                   | float        | YES  |     | NULL    |       |
| forestfloor_co2Uncertainty       | float        | YES  |     | NULL    |       |
| understory_co2                    | float        | YES  |     | NULL    |       |
| understory_co2Uncertainty        | float        | YES  |     | NULL    |       |
| downeddeadwood_co2                | float        | YES  |     | NULL    |       |
| downeddeadwood_co2Uncertainty    | float        | YES  |     | NULL    |       |
| soilorganiccarbon_co2             | float        | YES  |     | NULL    |       |
| soilorganiccarbon_co2Uncertainty | float        | YES  |     | NULL    |       |
| productsinuse_co2                 | float        | YES  |     | NULL    |       |
| productsinuse_co2Uncertainty     | float        | YES  |     | NULL    |       |
| inlandfills_co2                   | float        | YES  |     | NULL    |       |
| inlandfills_co2Uncertainty       | float        | YES  |     | NULL    |       |
+-----------------------------------+--------------+------+-----+---------+-------+

# Modifications 21 November 2017
- added capacity to pull in daycent output generated at the soil mapunit level.
- applicable tables are as follows:

desc api_results_cropland_daycent_master
+----------------------------------+--------------+------+-----+---------+----------------+
| Field                            | Type         | Null | Key | Default | Extra          |
+----------------------------------+--------------+------+-----+---------+----------------+
| id                               | int(11)      | NO   | PRI | NULL    | auto_increment |
| name                             | varchar(250) | YES  |     | NULL    |                |
| id_mlra_crops_from_cdl_2009_2015 | int(11)      | YES  |     | NULL    |                |
| mlra                             | varchar(5)   | YES  |     | NULL    |                |
| practice                         | varchar(200) | YES  |     | NULL    |                |
| scenario                         | varchar(200) | YES  |     | NULL    |                |
| irrigated                        | char(1)      | YES  |     | NULL    |                |
| mapunit                          | int(11)      | YES  |     | NULL    |                |
| area                             | float        | YES  |     | NULL    |                |
+----------------------------------+--------------+------+-----+---------+----------------+

MariaDB [comet]> desc api_results_cropland_daycent_values;
+----------------------------------------+-------------+------+-----+---------+----------------+
| Field                                  | Type        | Null | Key | Default | Extra          |
+----------------------------------------+-------------+------+-----+---------+----------------+
| id                                     | int(11)     | NO   | PRI | NULL    | auto_increment |
| id_api_results_cropland_daycent_master | int(11)     | YES  | MUL | NULL    |                |
| daycent_variable                       | varchar(12) | YES  |     | NULL    |                |
| date_value                             | varchar(8)  | YES  |     | NULL    |                |
| output_value                           | varchar(20) | YES  |     | NULL    |                |
+----------------------------------------+-------------+------+-----+---------+----------------+

# Modifications 8 February 2018
# restricted it so we aren't loading the reduced to no till converstion scenario
# this has a different baseline scenario compared with the conventional tillage baseline scenario

'''

# Extract monthly output data from the DayCent variable and insert only the end-of-year value into the database
# The date value is adjusted to represent the actual year. For example, records with the date value of "2003" refer to December 31, 2002.
# Those whole number date values are reduced by 1 and inserted so they correspond to the value for 2002.
def writeMonthlyDayCentOutput( daycent_variable, arrayText, cursor_daycent, mariadb_daycent, id_api_results_cropland_daycent_master, databaseName, baselineOrScenario ):
    array1 = arrayText.split(',')
    array1Length = len( array1 )

    # The output data for 2018 in the API begin with two copies of the 2018 data. 
    # This logic prevents the first from being written to the data tables.
    loopStartValue = 1
    if str( array1[0] ) == '2018':
        loopStartValue = 1
        
    for y in range( loopStartValue, ( array1Length / 2 ) ):
        if str( array1[ y * 2 ][4:5] ) != '.':
            year_value = str( int( array1[ y * 2 ] ) )
            output_value = str( array1[ ( y * 2 ) + 1 ] )
            sql = "INSERT INTO " + str( databaseName ) + ".api_results_cropland_daycent_" + str( baselineOrScenario ) + "_" + daycent_variable + " ( id_api_results_cropland_daycent_master, date_value, output_value ) VALUE ( '" + str( id_api_results_cropland_daycent_master ) + "', '" + str( year_value ) + "', '" + str( output_value ) + "' );"
            try:
                cursor_daycent.execute( sql )
            except mariadb_daycent.Error as error:
                print( "Error: {}".format( error ) )

# Extract yearly output data from the DayCent variable and insert the end-of-year value into the database
# This function is used for API data with whole numbers representing the yearly output data
# For example, the records with the date value of "2003" refer to "2003".
def writeYearlyDayCentOutput( daycent_variable, arrayText, cursor_daycent, mariadb_daycent, id_api_results_cropland_daycent_master, databaseName, baselineOrScenario ):
    arrayText = arrayText.replace( ':', ',' )
    array1 = arrayText.split(',')
    array1Length = len( array1 )

    for y in range( 0, ( array1Length / 2 ) ):
        year_value = str( int( array1[ y * 2 ] ) )
        output_value = str( array1[ ( y * 2 ) + 1 ] )
        sql = "INSERT INTO " + str( databaseName ) + ".api_results_cropland_daycent_" + str( baselineOrScenario ) + "_" + daycent_variable + " ( id_api_results_cropland_daycent_master, date_value, output_value ) VALUE ( '" + str( id_api_results_cropland_daycent_master ) + "', '" + str( year_value ) + "', '" + str( output_value ) + "' );"
        try:
            cursor_daycent.execute( sql )
        except mariadb_daycent.Error as error:
            print( "Error: {}".format( error ) )

# Extract only the end-of-year data from the DayCent variable and insert into the database
# These are pulled from the year_summary.out and similar files.
# For example, the records with the date value of "2003" refer to "2003".
def writeEndOfYearDayCentOutput( daycent_variable, arrayText, cursor_daycent, mariadb_daycent, id_api_results_cropland_daycent_master, databaseName, baselineOrScenario ):
    arrayText = arrayText.replace( ':', ',' )
    array1 = arrayText.split(',')
    array1Length = len( array1 )

    for y in range( 2, ( array1Length / 2 ) ):
        if '.' not in array1[ y * 2 ]:
            year_value = str( int( array1[ y * 2 ] ) - 1 )
            output_value = str( array1[ ( y * 2 ) + 1 ] )
            sql = "INSERT INTO " + str( databaseName ) + ".api_results_cropland_daycent_" + str( baselineOrScenario ) + "_" + daycent_variable + " ( id_api_results_cropland_daycent_master, date_value, output_value ) VALUE ( '" + str( id_api_results_cropland_daycent_master ) + "', '" + str( year_value ) + "', '" + str( output_value ) + "' );"
            try:
                cursor_daycent.execute( sql )
            except mariadb_daycent.Error as error:
                print( "Error: {}".format( error ) )

# Extract yearly output data from the DayCent variable and insert the end-of-year value into the database
# These are pulled from the year_summary.out and similar files.
# For example, the records with the date value of "2003.92" are truncated to "2003"
def writeYearlyDayCentOutput92( daycent_variable, arrayText, cursor_daycent, mariadb_daycent, id_api_results_cropland_daycent_master, databaseName, baselineOrScenario ):
    array1 = arrayText.split(',')
    array1Length = len( array1 )

    for y in range( 0, ( array1Length / 2 ) ):
        if '.92' in array1[ y * 2 ]:
            year_value = str( array1[ y * 2 ][:4] )
            output_value = str( array1[ ( y * 2 ) + 1 ] )
            sql = "INSERT INTO " + str( databaseName ) + ".api_results_cropland_daycent_" + str( baselineOrScenario ) + "_" + daycent_variable + " ( id_api_results_cropland_daycent_master, date_value, output_value ) VALUE ( '" + str( id_api_results_cropland_daycent_master ) + "', '" + str( year_value ) + "', '" + str( output_value ) + "' );"
            try:
                cursor_daycent.execute( sql )
            except mariadb_daycent.Error as error:
                print( "Error: {}".format( error ) )

# Update the api_records_cropland table with the summary data produced by COMET-Farm
def updateGUIdata( variableToUpdate2, updatedValue2, mariadb_connection, cursor, modelRunName, modelRunId, mlra, practice, scenario, irrigated, databaseName, id_api_results_cropland_GUIdata_master ):
        
        sql = "UPDATE " + str( databaseName ) + ".api_results_cropland SET " + str( variableToUpdate2 ) + " = '" + str( updatedValue2 ) + "' WHERE id = '" + str( id_api_results_cropland_GUIdata_master ) + "';"
        runSQL( sql, mariadb_connection, cursor )

# Run an SQL statement using the cursor and connection passed to it
def runSQL( sql, mariadb_connection2, cursor2 ):
        try:
            #print "\n   ...runSQL function SQL = [" + str( sql ) + "]\n"
            cursor2.execute( sql )
        except mariadb_connection2.Error as error:
            print( "   ...E: {}".format( error ) )
            print "      ...SQL WITH ERROR= [" + str( sql ) + "]"

# Main function
def main():

    # show the following if the command-line arguments are incomplete
    if len( sys.argv ) < 5 :
        print "\n"
        print "python script ReadResults.py <zipOrxml> <fileOrDirectory> <FileOrDirectoryName> <croplandOrGrassland> <database name>"
        print "\n"
        print "Command-line arguments are as follows:"
        print "   <zipOrxml> use word 'zip' to indicate data are in zip file format, or 'xml' to indicate xml file format"
        print "   <fileOrDirectory> use the word 'file' to indicate the input files are in file format, 'directory' indicates intent to import a set of files in a directory "
        print "   <fileOrDirectoryName> fully-qualified path to the input file name or the directory containing the input files"
        print "   <croplandOrGrassland> use the word 'cropland' to indicate data are from a cropland system, or 'grassland' to indicate data are from a grassland system"
        print "   <database name> name of the tusker database to which these data are to be saved"
        print ""
    
    else:
        
        #take in the command-line arguments
        zipOrXML = sys.argv[1] #'zip', 'xml'
        fileOrDirectory = sys.argv[2] #'file', 'directory'
        fileOrDirectoryName = sys.argv[3]
        croplandOrGrassland = sys.argv[4]
        databaseName = sys.argv[5]

        start = datetime.now( )
        mariadb_connection = MySQLdb.connect( host='', user='', passwd='', db=databaseName )
        cursor = mariadb_connection.cursor()

        print ""
        print "Starting script at " + str( time.ctime( int( time.time( ) ) ) )
        print ""

        print "----------------------------------------------------------------------"
        #print "     1) Open an output file"

        #print "zipOrXML = " + zipOrXML
        #print "fileOrDirectory = " + fileOrDirectory
        #print "fileOrDirectoryName = " + fileOrDirectoryName
        #print "croplandOrGrassland = " + croplandOrGrassland

        #read in the XML input file
        #print "...reading the input file"

        inDirectory = ''

        #load the file(s) into an array for reading
        if fileOrDirectory == 'directory':
            inDirectory = fileOrDirectoryName
            if inDirectory[-1:] != "/":
                inDirectory = inDirectory + "/"
            fileList = [ f for f in listdir( inDirectory) if isfile( join( inDirectory, f ) ) ]
        elif fileOrDirectory == 'file':
            fileList = [ fileOrDirectoryName ]
        else:
            print "     ...argument 2 must be the word 'file' or 'directory'\n"
            sys.exit(0)

        ModelRunNameArray = ''
        module = ''
        modelRunId = ''
        irrigated = ''
        mlra = ''
        practice = ''
        scenario = ''

        id_api_results_cropland_daycent_master = ''
        id_api_results_cropland_GUIdata_master = ''

        for inputFile in fileList[:]:
            fileName = ""
            print "name of inputFile = " + inputFile
            if inputFile.find( 'DaycentReport' ) > -1:

                if zipOrXML == 'xml':
                    fileName = inputFile
                elif zipOrXML == 'zip':
                    #make a copy of the zip file, and unzip the copy with the double .zip suffix
                    os.chdir( os.path.dirname( inputFile ) )
                    #call([ "cp", inputFile, inputFile + ".zip" ])
                    #call([ "ls", "-lah", inputFile + ".zip" ])
                    #print "unzip string: " + "unzip" + " " + inputFile + ".zip"
                    #call( [ "unzip", inputFile + ".zip", "-d", "-o", os.path.dirname( inputFile ) + "/" ] )
                    call( [ "unzip", inputFile ] )
                    call([ "ls", "-lah", inputFile[:-4] ])
                    sys.exit(0)
                    if os.path.exists( inputFile[:-4] ):
                        fileName = inputFile[:-4]
                    else:
                        print "     ...unzipped file doesn't exist, skipping file " + inputFile
                else:
                    print "     ...argument 1 must be the word 'zip' or 'xml'"
                    sys.exit(0)
            else:
                print "     ...skipping file " + inputFile
                break

            source = open( inputFile )
            tree = ET.parse( source )
            root = tree.getroot()

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
            #put these values in as a placeholder while Kevin fixes things
            BiomassBurningCO = '0'
            BiomassBurningCOUncertainty = '0'

            #count the number of scenarios
            #print "...counting the number of scenarios in the xml file"
            scenarioCount = 0
            for elem in tree.iter():
                if( str( elem.tag ) == 'Scenario' ):
                    scenarioCount = scenarioCount + 1

            #print "...there are " + str( scenarioCount ) + " scenarios to process"

            #process the scenarios
            #print "...processing the scenarios"
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
                    #get the module, id, irrigated, mlra, and practice
                    ModelRunNameArray = xmlAttribName.split( '|' )
                    module = str( ModelRunNameArray[0][7:] )
                    modelRunId = str( ModelRunNameArray[1][3:] )

                    #print "name = " + str( xmlAttribName )
                    print "array element = " + str( ModelRunNameArray[1] ) + ", modelRunId = " + str( modelRunId )
                    #exit()
                    
                    irrigated = str( ModelRunNameArray[2][10:] )
                    
                    if ModelRunNameArray[3][:7] == 'mlra42:':
                        mlra = str( ModelRunNameArray[3][7:12] )
                    else:
                        mlra = str( ModelRunNameArray[3][5:10] )
                    
                    print "array element = " + str( ModelRunNameArray[3] ) + ", mlra = " + str( mlra )
                    
                    practice = str( ModelRunNameArray[4][9:] )
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
                    
                        # create a master record for the GUI-generated results 
                        #print "\n   ...creating master record for ModelRunID = [" + str( modelRunId ) + "] and name = '" + str( modelRunName ) + "' AND id_mlra_crops_from_cdl_2009_2015 = '" + str( modelRunId ) + "' AND mlra = '" + str( mlra ) + "' AND practice =  '" + str( practice ) + "' AND scenario = '" + str( scenario ) + "' AND irrigated = '" + str( irrigated ) + "'"

                        # delete any existing record in the database
                        sql = "DELETE FROM " + str( databaseName ) + ".api_results_cropland WHERE name = '" + str( modelRunName ) + "' AND id_mlra_crops_from_cdl_2009_2015 = '" + str( modelRunId ) + "' AND mlra = '" + str( mlra ) + "' AND practice =  '" + str( practice ) + "' AND scenario = '" + str( scenario ) + "' AND irrigated = '" + str( irrigated ) + "';"
                        #print "      ...sql = " + sql
                        runSQL( sql, mariadb_connection, cursor )

                        #insert the new record
                        sql = "INSERT INTO " + str( databaseName ) + ".api_results_cropland (name, id_mlra_crops_from_cdl_2009_2015, mlra, practice, scenario, irrigated ) VALUES ('" + str( modelRunName ) + "', '" + str( modelRunId ) + "', '" + str( mlra ) + "', '" + str( practice ) + "', '" + str( scenario ) + "', '" + str( irrigated ) + "' );"
                        #print "      ...sql = " + sql
                        runSQL( sql, mariadb_connection, cursor )

                        #get the new master record id
                        sql = "SELECT id as masterId FROM " + str( databaseName ) + ".api_results_cropland WHERE name = '" + str( modelRunName ) + "' and id_mlra_crops_from_cdl_2009_2015 = '" + str( modelRunId ) + "' and mlra = '" + str( mlra ) + "' and practice = '" + str( practice ) + "' and scenario = '" + str( scenario ) + "' and irrigated = '" + str( irrigated ) + "' ;"
                        #print "      ...sql = " + sql
                        cursor_master = mariadb_connection.cursor()
                        cursor_master.execute( sql )
                        for ( masterId ) in cursor_master:
                            id_api_results_cropland_GUIdata_master = str( masterId[0] )
                            id_api_results_cropland_GUIdata_master
                            print "      ...Scenario tag id_api_results_cropland_GUIdata_master = " + str( id_api_results_cropland_GUIdata_master )
                        if ( cursor_master ):
                            cursor_master.close()

                elif( "current" in scenario.lower() ):
                    continue

                elif( xmlTag == "MapUnit" ):

                    mapunit = xmlAttribId
                    area = xmlAttribArea
                    cursor_master = mariadb_connection.cursor()

                    if scenario == 'Baseline':
                        # create the master records
                        print "      ...creating DayCent + mapunit master records for scenario = [" + str( scenario ) + "] and mapunit = [" + str( mapunit ) + "]"

                        # find any existing masterId record and delete the records from the daycent value tables that correspond
                        sql = "SELECT id as masterId FROM " + str( databaseName ) + ".api_results_cropland_daycent_baseline_master WHERE id_mlra_crops_from_cdl_2009_2015 = '" + str( modelRunId ) + "' and mlra = '" + str( mlra ) + "' and irrigated = '" + str( irrigated ) + "' and mapunit = '" + str( mapunit ) + "';"
                        #print "      ...sql = " + sql
                        cursor_master.execute( sql )
                        for ( masterId ) in cursor_master:
                            id_api_results_cropland_daycent_master = masterId[0]
                            id_api_results_cropland_daycent_master
                            #print "\n   ...id from " + str( databaseName ) + ".api_results_cropland_daycent_baseline_master = " + str( id_api_results_cropland_daycent_master ) + "\n"

                            # create a master record in the DayCent master file and then get the id number back
                            sql = "DELETE FROM " + str( databaseName ) + ".api_results_cropland_daycent_baseline_master WHERE id_mlra_crops_from_cdl_2009_2015 = '" + str( modelRunId ) + "' AND mlra = '" + str( mlra ) + "' AND irrigated = '" + str( irrigated ) + "' and mapunit = '" + str( mapunit ) + "';"
                            #print "      ...sql = " + sql
                            runSQL( sql, mariadb_connection, cursor )

                            # delete the records in the daycent data child tables for this master record
                            for ( daycent2 ) in ( 'InputCrop', 'Irrigated', 'Year', 'aagdefac', 'abgdefac', 'accrst', 'accrste_1_', 'agcprd', 'aglivc', 'annppt', 'bgdefac', 'bglivcm', 'cgrain', 'cinput', 'crmvst', 'crootc', 'crpval', 'egracc_1_', 'eupacc_1_', 'fbrchc', 'fertac_1_', 'fertot_1_1_', 'frootcm', 'gromin_1_', 'irrtot', 'metabc_1_', 'metabc_2_', 'metabe_1_1_', 'metabe_2_1_', 'n2oflux', 'nfixac', 'noflux', 'omadac', 'omadae_1_', 'petann', 'rlwodc', 'somsc', 'somse_1_', 'stdedc', 'stdede_1_', 'strmac_1_', 'strmac_2_', 'strmac_6_', 'strucc_1_', 'struce_1_1_', 'struce_2_1_', 'tminrl_1_', 'tnetmn_1_', 'volpac' ):
                                sql = "DELETE FROM " + str( databaseName ) + ".api_results_cropland_daycent_baseline_" + daycent2.lower() + " WHERE id_api_results_cropland_daycent_master = " + str( id_api_results_cropland_daycent_master ) + ";"
                                #print "      ...sql = " + sql
                                runSQL( sql, mariadb_connection, cursor )

                        #insert the new record
                        sql = "INSERT INTO " + str( databaseName ) + ".api_results_cropland_daycent_baseline_master ( id_mlra_crops_from_cdl_2009_2015, mlra, irrigated, mapunit, area ) VALUES ('" + str( modelRunId ) + "', '" + str( mlra ) + "', '" + str( irrigated ) + "', '" + str( mapunit ) + "', '" + str( area ) + "' );"
                        #print "      ...sql = " + sql
                        runSQL( sql, mariadb_connection, cursor )

                        #get the new master record id
                        sql = "SELECT id as masterId FROM " + str( databaseName ) + ".api_results_cropland_daycent_baseline_master WHERE id_mlra_crops_from_cdl_2009_2015 = '" + str( modelRunId ) + "' and mlra = '" + str( mlra ) + "' and irrigated = '" + str( irrigated ) + "' and mapunit = '" + str( mapunit ) + "';"
                        #print "      ...sql = " + sql
                        cursor_master = mariadb_connection.cursor()
                        cursor_master.execute( sql )
                        for ( masterId ) in cursor_master:
                            id_api_results_cropland_daycent_master = masterId[0]
                            id_api_results_cropland_daycent_master
                            #print "\n   ...id from " + str( databaseName ) + ".api_results_cropland_daycent_baseline_master = " + str( id_api_results_cropland_daycent_master ) + "\n"

                    else:
                    
                        # find any existing masterId record and delete the records from the daycent value tables that correspond
                        sql = "SELECT id as masterId FROM " + str( databaseName ) + ".api_results_cropland_daycent_scenario_master WHERE name = '" + modelRunName + "' and id_mlra_crops_from_cdl_2009_2015 = '" + str( modelRunId ) + "' and mlra = '" + str( mlra ) + "' and practice = '" + str( practice ) + "' and scenario = '" + str( scenario ) + "' and irrigated = '" + str( irrigated ) + "' and mapunit = '" + str( mapunit ) + "';"
                        #print "      ...sql = " + sql
                        cursor_master = mariadb_connection.cursor()
                        cursor_master.execute( sql )
                        for ( masterId ) in cursor_master:
                            id_api_results_cropland_daycent_master = masterId[0]
                            id_api_results_cropland_daycent_master
                            #print "\n   ...id from " + str( databaseName ) + ".api_results_cropland_daycent_master = " + str( id_api_results_cropland_daycent_master ) + "\n"

                            # create a master record in the DayCent master file and then get the id number back
                            sql = "DELETE FROM " + str( databaseName ) + ".api_results_cropland_daycent_scenario_master WHERE name = '" + str( modelRunName ) + "' AND id_mlra_crops_from_cdl_2009_2015 = '" + str( modelRunId ) + "' AND mlra = '" + str( mlra ) + "' AND practice =  '" + str( practice ) + "' AND scenario = '" + str( scenario ) + "' AND irrigated = '" + str( irrigated ) + "' and mapunit = '" + str( mapunit ) + "';"
                            #print "      ...sql = " + sql
                            runSQL( sql, mariadb_connection, cursor )

                            # delete the records in the daycent data child tables for this master record
                            for ( daycent2 ) in ( 'InputCrop', 'Irrigated', 'Year', 'aagdefac', 'abgdefac', 'accrst', 'accrste_1_', 'agcprd', 'aglivc', 'annppt', 'bgdefac', 'bglivcm', 'cgrain', 'cinput', 'crmvst', 'crootc', 'crpval', 'egracc_1_', 'eupacc_1_', 'fbrchc', 'fertac_1_', 'fertot_1_1_', 'frootcm', 'gromin_1_', 'irrtot', 'metabc_1_', 'metabc_2_', 'metabe_1_1_', 'metabe_2_1_', 'n2oflux', 'nfixac', 'noflux', 'omadac', 'omadae_1_', 'petann', 'rlwodc', 'somsc', 'somse_1_', 'stdedc', 'stdede_1_', 'strmac_1_', 'strmac_2_', 'strmac_6_', 'strucc_1_', 'struce_1_1_', 'struce_2_1_', 'tminrl_1_', 'tnetmn_1_', 'volpac' ):
                                sql = "DELETE FROM " + str( databaseName ) + ".api_results_cropland_daycent_scenario_" + daycent2.lower() + " WHERE id_api_results_cropland_daycent_master = " + str( id_api_results_cropland_daycent_master ) + ";"
                                #print "      ...sql = " + sql
                                runSQL( sql, mariadb_connection, cursor )

                        #insert the new record
                        sql = "INSERT INTO " + str( databaseName ) + ".api_results_cropland_daycent_scenario_master ( name, id_mlra_crops_from_cdl_2009_2015, mlra, practice, scenario, irrigated, mapunit, area ) VALUES ('" + str( modelRunName ) + "', '" + str( modelRunId ) + "', '" + str( mlra ) + "', '" + str( practice ) + "', '" + str( scenario ) + "', '" + str( irrigated ) + "', '" + str( mapunit ) + "', '" + str( area ) + "' );"
                        #print "      ...sql = " + sql
                        runSQL( sql, mariadb_connection, cursor )

                        #get the new master record id
                        sql = "SELECT id as masterId FROM " + str( databaseName ) + ".api_results_cropland_daycent_scenario_master WHERE name = '" + modelRunName + "' and id_mlra_crops_from_cdl_2009_2015 = '" + str( modelRunId ) + "' and mlra = '" + str( mlra ) + "' and practice = '" + str( practice ) + "' and scenario = '" + str( scenario ) + "' and irrigated = '" + str( irrigated ) + "' and mapunit = '" + str( mapunit ) + "';"
                        #print "      ...sql = " + sql
                        cursor_master = mariadb_connection.cursor()
                        cursor_master.execute( sql )
                        for ( masterId ) in cursor_master:
                            id_api_results_cropland_daycent_master = masterId[0]
                            id_api_results_cropland_daycent_master
                            #print "\n   ...id from " + str( databaseName ) + ".api_results_cropland_daycent_scenario_master = " + str( id_api_results_cropland_daycent_master ) + "\n"

                        if ( cursor_master ):
                            cursor_master.close()

                # process the DayCent output data
                elif( xmlTag.lower() in ( 'aagdefac', 'abgdefac', 'accrst', 'accrste_1_', 'agcprd', 'aglivc', 'bgdefac', 'bglivcm', 'cgrain', 'cinput', 'crmvst', 'crootc', 'crpval', 'egracc_1_', 'eupacc_1_', 'fbrchc', 'fertac_1_', 'fertot_1_1_', 'frootcm', 'gromin_1_', 'irrtot', 'metabc_1_', 'metabc_2_', 'metabe_1_1_', 'metabe_2_1_', 'nfixac', 'omadac', 'omadae_1_', 'petann', 'rlwodc', 'somsc', 'somse_1_', 'stdedc', 'stdede_1_', 'strmac_1_', 'strmac_2_', 'strmac_6_', 'strucc_1_', 'struce_1_1_', 'struce_2_1_', 'tminrl_1_', 'tnetmn_1_', 'volpac' ) ):

                    if scenario == 'Baseline':
                        writeEndOfYearDayCentOutput( xmlTag.lower(), str( xmlText ), cursor, mariadb_connection, id_api_results_cropland_daycent_master, databaseName, 'baseline' )
                    else:
                        writeEndOfYearDayCentOutput( xmlTag.lower(), str( xmlText ), cursor, mariadb_connection, id_api_results_cropland_daycent_master, databaseName, 'scenario' )
                    
                elif( xmlTag.lower() in ( 'year', 'irrigated', 'inputcrop' ) ):

                    if scenario == 'Baseline':
                        writeYearlyDayCentOutput( xmlTag.lower(), str( xmlText ), cursor, mariadb_connection, id_api_results_cropland_daycent_master, databaseName, 'baseline' )
                    else:
                        writeYearlyDayCentOutput( xmlTag.lower(), str( xmlText ), cursor, mariadb_connection, id_api_results_cropland_daycent_master, databaseName, 'scenario' )

                elif( xmlTag.lower() in ( 'noflux', 'n2oflux', 'annppt' ) ):

                    if scenario == 'Baseline':
                        writeYearlyDayCentOutput92( xmlTag.lower(), str( xmlText ), cursor, mariadb_connection, id_api_results_cropland_daycent_master, databaseName, 'baseline' )
                    else:
                        writeYearlyDayCentOutput92( xmlTag.lower(), str( xmlText ), cursor, mariadb_connection, id_api_results_cropland_daycent_master, databaseName, 'scenario' )

                # process the GUI output data
                elif( xmlTag == 'SoilCarbon' ):                 updateGUIdata( "soil_carbon_co2", str( xmlText ), mariadb_connection, cursor, modelRunName, modelRunId, mlra, practice, scenario, irrigated, databaseName, id_api_results_cropland_GUIdata_master )
                elif( xmlTag == 'SoilCarbonStock2000' ):        updateGUIdata( "soil_carbon_stock_2000", str( xmlText ), mariadb_connection, cursor, modelRunName, modelRunId, mlra, practice, scenario, irrigated, databaseName, id_api_results_cropland_GUIdata_master )
                elif( xmlTag == 'SoilCarbonStockBegin' ):       updateGUIdata( "soil_carbon_stock_begin", str( xmlText ), mariadb_connection, cursor, modelRunName, modelRunId, mlra, practice, scenario, irrigated, databaseName, id_api_results_cropland_GUIdata_master )
                elif( xmlTag == 'SoilCarbonStockEnd' ):         updateGUIdata( "soil_carbon_stock_end", str( xmlText ), mariadb_connection, cursor, modelRunName, modelRunId, mlra, practice, scenario, irrigated, databaseName, id_api_results_cropland_GUIdata_master )
                elif( xmlTag == 'BiomassBurningCarbon' ):       updateGUIdata( "biomass_burning_co2", str( xmlText ), mariadb_connection, cursor, modelRunName, modelRunId, mlra, practice, scenario, irrigated, databaseName, id_api_results_cropland_GUIdata_master )
                elif( xmlTag == 'LimingCO2' ):                  updateGUIdata( "liming_co2", str( xmlText ), mariadb_connection, cursor, modelRunName, modelRunId, mlra, practice, scenario, irrigated, databaseName, id_api_results_cropland_GUIdata_master )
                elif( xmlTag == 'UreaFertilizationCO2' ):       updateGUIdata( "ureafertilization_co2", str( xmlText ), mariadb_connection, cursor, modelRunName, modelRunId, mlra, practice, scenario, irrigated, databaseName, id_api_results_cropland_GUIdata_master )
                elif( xmlTag == 'DrainedOrganicSoilsCO2' ):     updateGUIdata( "drainedorganicsoils_co2", str( xmlText ), mariadb_connection, cursor, modelRunName, modelRunId, mlra, practice, scenario, irrigated, databaseName, id_api_results_cropland_GUIdata_master )
                elif( xmlTag == 'SoilN2O' ):                    updateGUIdata( "soil_n2o", str( xmlText ), mariadb_connection, cursor, modelRunName, modelRunId, mlra, practice, scenario, irrigated, databaseName, id_api_results_cropland_GUIdata_master )
                elif( xmlTag == 'WetlandRiceCultivationN2O' ):  updateGUIdata( "wetlandricecultivation_n2o", str( xmlText ), mariadb_connection, cursor, modelRunName, modelRunId, mlra, practice, scenario, irrigated, databaseName, id_api_results_cropland_GUIdata_master )
                elif( xmlTag == 'BiomassBurningN2O' ):          updateGUIdata( "biomassburning_n2o", str( xmlText ), mariadb_connection, cursor, modelRunName, modelRunId, mlra, practice, scenario, irrigated, databaseName, id_api_results_cropland_GUIdata_master )
                elif( xmlTag == 'DrainedOrganicSoilsN2O' ):     updateGUIdata( "drainedorganicsoils_n2o", str( xmlText ), mariadb_connection, cursor, modelRunName, modelRunId, mlra, practice, scenario, irrigated, databaseName, id_api_results_cropland_GUIdata_master )
                elif( xmlTag == 'SoilCH4' ):                    updateGUIdata( "soil_ch4", str( xmlText ), mariadb_connection, cursor, modelRunName, modelRunId, mlra, practice, scenario, irrigated, databaseName, id_api_results_cropland_GUIdata_master )
                elif( xmlTag == 'WetlandRiceCultivationCH4' ):  updateGUIdata( "wetlandricecultivation_ch4", str( xmlText ), mariadb_connection, cursor, modelRunName, modelRunId, mlra, practice, scenario, irrigated, databaseName, id_api_results_cropland_GUIdata_master )
                elif( xmlTag == 'BiomassBurningCH4' ):          updateGUIdata( "biomassburning_ch4", str( xmlText ), mariadb_connection, cursor, modelRunName, modelRunId, mlra, practice, scenario, irrigated, databaseName, id_api_results_cropland_GUIdata_master )
                else:
                    continue
            #close the XML input file
            source.close()

        cursor.close()
        mariadb_connection.close()

        print "----------------------------------------------------------------------"
        print ""
        End = datetime.now( )
        print "Ending script at " + str( time.ctime( int( time.time( ) ) ) )
        elapsed = End-start
        print "elapsed time = " + str( elapsed )
        print ""

main()
