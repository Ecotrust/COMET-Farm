'''

Mark Easter, 20 December 2017

This script builds a list of cropland API input files for the CAR N2O study.  Steps are as follows:
    1) Open an output file
    2) Write mariadb table id field and username to file
    3) Write GEOM, State and County
    4) Write systems
    5) Close file

'''
# Import system modules
from datetime import datetime, timedelta
import os, sys, time, MySQLdb, string, re, math, zipfile, zlib
#import mysql.connector as mariadb

import warnings
warnings.filterwarnings( "ignore", "Unknown table.*" )

start = datetime.now( )

# show the following if the command-line arguments are incomplete
if len( sys.argv ) < 1:
    print "\n"
    print "python script planner_cropland_input_files24.py <number of mlra42>"
    print "\n"
    print "Command-line arguments are as follows:"
    print "   <number of mlra42> enter the mlra42 number"
    print ""
    exit()


mariadb_connection = MySQLdb.connect( host='', user='', passwd='', db='' )

tab1 = "\t"
tab2 = "\t\t"
tab3 = "\t\t\t"
tab4 = "\t\t\t\t"
tab5 = "\t\t\t\t\t"
tab6 = "\t\t\t\t\t\t"
tab7 = "\t\t\t\t\t\t\t"

print ""
print "Starting script at " + str( time.ctime( int( time.time( ) ) ) )
print ""

print "     ----------------------------------------------------------------------"
#print "     1) Open an output file"

mlra42_name = sys.argv[1]
print "mlra42_name = " + mlra42_name

'''
run script syntax follows:

#Note: the MLRAs not shown in this list don't have cropland points
python /data/paustian/CAR/N2O2017/InputData/cropland_input_files17.py 17

+--------+
| mlra42 |
+--------+
|        |
| 14     |
| 15     |
| 16     |
| 17     |
| 18     |
| 19     |
| 20     |
| 21     |
| 23     |
| 30     |
| 31     |
| 5      |
+--------+
'''

#cursor_mlras = mariadb_connection.cursor()
total_points_per_file = 10

homeDirectory = "/data/paustian/COMET-Planner/CFARM_alignment/cropland/model_run_input_files/runfolder20180211/"
os.chdir( homeDirectory )

#Write the SQL query:  Build input datasets by CPS practice
sql = "SELECT DISTINCT pccl.id as 'cps_id', pccl.irrigated, pccl.practice, pchmm.historic_management_name, pchmm.modern_management_name FROM comet.planner_cropland_cps_list pccl JOIN comet.planner_cropland_historic_and_modern_management pchmm ON pccl.id = pchmm.cps_id WHERE pchmm.mlra = '" + str( mlra42_name ) + "' ORDER BY practice"
print "sql = " + sql

cursor_practices = mariadb_connection.cursor()
cursor_practices.execute( sql )

#see how many points there are to run:
total_number_model_points = 120
sql = "SELECT DISTINCT mcfc.id AS 'id_mcfc', point_x, point_y, lrr, state as 'statecode', county, fips, crop_2009, crop_2010, crop_2011, crop_2012, crop_2013, crop_2014, crop_2015 FROM comet.mlra_crops_from_cdl_2009_2015 mcfc WHERE mcfc.mlra42 = '" + str( mlra42_name ) + "' AND crop_2009 <> 'NoData' AND crop_2010 <> 'NoData' AND crop_2011 <> 'NoData' AND crop_2012 <> 'NoData' AND crop_2013 <> 'NoData' AND crop_2014 <> 'NoData' AND crop_2015 <> 'NoData' AND selected = 'Y' ORDER BY random_order LIMIT " + str( total_number_model_points ) + ";"
print "sql = " + sql
cursor_points_count = mariadb_connection.cursor()
cursor_points_count.execute( sql )
number_of_points = cursor_points_count.rowcount
cursor_points_count.close()

number_of_files = int( number_of_points / total_points_per_file ) + 1
#print "number_of_files = " + str( number_of_files )
point_count = 0;

for file_counter in range( 0, number_of_files - 1 ):

    if( file_counter <= number_of_files ):

        sql = "SELECT DISTINCT mcfc.id AS 'id_mcfc', point_x, point_y, lrr, state as 'statecode', county, fips, crop_2009, crop_2010, crop_2011, crop_2012, crop_2013, crop_2014, crop_2015, winter_crop_2008_2009, summer_crop_2009, winter_crop_2009_2010, summer_crop_2010, winter_crop_2010_2011, summer_crop_2011, winter_crop_2011_2012, summer_crop_2012, winter_crop_2012_2013, summer_crop_2013, winter_crop_2013_2014, summer_crop_2014, winter_crop_2014_2015, summer_crop_2015 FROM comet.mlra_crops_from_cdl_2009_2015 mcfc WHERE mlra42 = '" + str( mlra42_name ) + "' AND crop_2009 <> 'NoData' AND crop_2010 <> 'NoData' AND crop_2011 <> 'NoData' AND crop_2012 <> 'NoData' AND crop_2013 <> 'NoData' AND crop_2014 <> 'NoData' AND crop_2015 <> 'NoData' AND selected = 'Y' ORDER BY random_order LIMIT " + str( ( file_counter * total_points_per_file ) ) + ", " + str( total_points_per_file )
        print "sql = " + sql

        cursor_points = mariadb_connection.cursor()
        cursor_points.execute( sql )

        input_xml_file_name = "cropland_mlra42-" + mlra42_name + "-file" + str( file_counter ) + ".xml"
        input_xml_file = homeDirectory + input_xml_file_name
        zipfile_name = input_xml_file_name + ".zip"
        
        #delete the zipfile if it already exists
        if( os.path.isfile( zipfile_name ) ): os.remove( zipfile_name )

        #initialize the file content string that will contain the text to be written to the file
        with open( input_xml_file, 'w' ) as f:
            
            print "\n********************************************************"
            print "Writing to file " + str( input_xml_file )
            print "********************************************************"

            f.write( "<Day cometEmailId=\"mark.easter@colostate.edu\">\n" )

            practice_count = 0
            for ( cps_id, irrigated, practice, historic_management_name, modern_management_name  ) in cursor_practices:

                practice_count = practice_count + 1;
                print "   ... File# " + str( file_counter ) + " of " + str( number_of_files - 1 ) + ", practice = [" + practice + "], irrig = [" + irrigated + "], mlra42 = " + str( mlra42_name )

                id_mcfc_string = ''
                
                for ( id_mcfc, point_x, point_y, lrr, statecode, county, fips, crop_2009, crop_2010, crop_2011, crop_2012, crop_2013, crop_2014, crop_2015, winter_crop_2008_2009, summer_crop_2009, winter_crop_2009_2010, summer_crop_2010, winter_crop_2010_2011, summer_crop_2011, winter_crop_2011_2012, summer_crop_2012, winter_crop_2012_2013, summer_crop_2013, winter_crop_2013_2014, summer_crop_2014, winter_crop_2014_2015, summer_crop_2015 ) in cursor_points:
                
                    fileWriteString = ""
                    
                    id_mcfc_string = str( id_mcfc_string ) + str( id_mcfc ) + ', '

                    if( practice_count == 1 ): point_count = point_count + 1

                    #print "     ----------------------------------------------------------------------"

                    #print "      ...mlra42 = " + str( mlra42_name ) + ", id_mcfc = [" + str( id_mcfc ) + "], " + str( point_count ) + " of " + str( number_of_points ) + " total points, " + str( practice_count ) + " of " + str( cursor_practices.rowcount ) + " total conservation practices"

                    #print "     2) Write mariadb table id field and username to file for id = " + str( id )

                    fileWriteString = fileWriteString +  tab1 + "<Cropland name=\"module:cropland|id:" + str( id_mcfc ) + "|irrigated:" + irrigated + "|mlra42:" + str( mlra42_name ) + "|practice:" + practice + "|crop2009:" + crop_2009 + "|crop2010:" + crop_2010 + "|crop2011:" + crop_2011 + "|crop2012:" + crop_2012 + "|crop2013:" + crop_2013 + "|crop2014:" + crop_2014 + "|crop2015:" + crop_2015 + "\">\n"

                    #print "     4) Write GEOM, State and County"
                    fileWriteString = fileWriteString + tab2 + "<GEOM SRID=\"4326\" AREA=\"10\">POINT(" + str( point_x ) + " " + str( point_y ) + ")</GEOM>\n" 


                    fileWriteString = fileWriteString + tab2 + "<Pre-1980>" + historic_management_name + "</Pre-1980>\n" 
                    fileWriteString = fileWriteString + tab2 + "<CRP>None</CRP>\n" 
                    fileWriteString = fileWriteString + tab2 + "<CRPStartYear></CRPStartYear>\n" 
                    fileWriteString = fileWriteString + tab2 + "<CRPEndYear></CRPEndYear>\n" 
                    fileWriteString = fileWriteString + tab2 + "<CRPType>None</CRPType>\n" 

                    if( irrigated in ( 'Y', 'I' ) ):
                        if( mlra42_name == '14'):
                            modern_management_name = 'Irrigated: 2 Yrs Cotton-Vegetables-3 Yrs Legume Hay'
                        elif( mlra42_name == '15'):
                            modern_management_name = 'Irrigated: Continuous Vegetables'
                        elif( mlra42_name == '16'):
                            modern_management_name = 'Irrigated: Continuous Vegetables'
                        elif( mlra42_name == '17'):
                            modern_management_name = 'Irrigated: Continuous Vegetables'
                        elif( mlra42_name == '18'):
                            modern_management_name = 'Irrigated: Continuous Vegetables'
                        elif( mlra42_name == '19'):
                            modern_management_name = 'Irrigated: Continuous Vegetables'
                        elif( mlra42_name == '20'):
                            modern_management_name = 'Irrigated: Continuous Vegetables'
                        elif( mlra42_name == '21'):
                            modern_management_name = 'Irrigated: Spring Grain-Sugar Beet'
                        elif( mlra42_name == '23'):
                            modern_management_name = 'Irrigated: Spring Grain-Potato'
                        elif( mlra42_name == '30'):
                            modern_management_name = 'Irrigated: Continuous Vegetables'
                        elif( mlra42_name == '31'):
                            modern_management_name = 'Irrigated: Continuous Vegetables'
                        elif( mlra42_name == '5'):
                            modern_management_name = 'Irrigated: Winter Wheat-Corn Silage-Dry Bean'
                    else:
                        if( mlra42_name == '14'):
                            modern_management_name = 'Non-Irrigated: Spring Wheat-Mechanical Fallow'
                        elif( mlra42_name == '15'):
                            modern_management_name = 'Non-Irrigated: Spring Wheat-Mechanical Fallow'
                        elif( mlra42_name == '16'):
                            modern_management_name = 'Non-Irrigated: Spring Wheat-Mechanical Fallow'
                        elif( mlra42_name == '17'):
                            modern_management_name = 'Non-Irrigated: Spring Wheat-Mechanical Fallow'
                        elif( mlra42_name == '18'):
                            modern_management_name = 'Non-Irrigated: Spring Wheat-Mechanical Fallow'
                        elif( mlra42_name == '19'):
                            modern_management_name = 'Non-Irrigated: Spring Wheat-Mechanical Fallow'
                        elif( mlra42_name == '20'):
                            modern_management_name = 'Non-Irrigated: Spring Wheat-Mechanical Fallow'
                        elif( mlra42_name == '21'):
                            modern_management_name = 'Non-Irrigated: Spring Wheat-Mechanical Fallow'
                        elif( mlra42_name == '23'):
                            modern_management_name = 'Non-Irrigated: Spring Wheat-Mechanical Fallow'
                        elif( mlra42_name == '30'):
                            modern_management_name = 'Non-Irrigated: Spring Wheat-Mechanical Fallow'
                        elif( mlra42_name == '31'):
                            modern_management_name = 'Non-Irrigated: Spring Wheat-Mechanical Fallow'
                        elif( mlra42_name == '5'):
                            modern_management_name = 'Non-Irrigated: Spring Wheat-Mechanical Fallow'

                        #modern_management_name = 'Heavy Utilization, Year-Round, Fertilized (Grazing)'

                    fileWriteString = fileWriteString + tab2 + "<Year1980-2000>" + modern_management_name + "</Year1980-2000>\n" 
                    fileWriteString = fileWriteString + tab2 + "<Year1980-2000_Tillage>Intensive Tillage</Year1980-2000_Tillage>\n" 

                    #print "     5) Write system = " + practice

                    for current_or_future_management in ( 'current', 'future' ):

                        crop_2000 = crop_2014
                        crop_2001 = crop_2015
                        crop_2002 = crop_2009
                        crop_2003 = crop_2010
                        crop_2004 = crop_2011
                        crop_2005 = crop_2012
                        crop_2006 = crop_2013
                        crop_2007 = crop_2014
                        crop_2008 = crop_2015
                        crop_2009 = crop_2009
                        crop_2010 = crop_2010
                        crop_2011 = crop_2011
                        crop_2012 = crop_2012
                        crop_2013 = crop_2013
                        crop_2014 = crop_2014
                        crop_2015 = crop_2015
                        crop_2016 = crop_2009
                        crop_2017 = crop_2010
                        
                        crop_2018 = crop_2014
                        crop_2019 = crop_2015
                        crop_2020 = crop_2009
                        crop_2021 = crop_2010
                        crop_2022 = crop_2011
                        crop_2023 = crop_2012
                        crop_2024 = crop_2013
                        crop_2025 = crop_2014
                        crop_2026 = crop_2015
                        crop_2027 = crop_2009

                        summer_crop_2000 = summer_crop_2014
                        summer_crop_2001 = summer_crop_2015
                        summer_crop_2002 = summer_crop_2009
                        summer_crop_2003 = summer_crop_2010
                        summer_crop_2004 = summer_crop_2011
                        summer_crop_2005 = summer_crop_2012
                        summer_crop_2006 = summer_crop_2013
                        summer_crop_2007 = summer_crop_2014
                        summer_crop_2008 = summer_crop_2015
                        summer_crop_2009 = summer_crop_2009
                        summer_crop_2010 = summer_crop_2010
                        summer_crop_2011 = summer_crop_2011
                        summer_crop_2012 = summer_crop_2012
                        summer_crop_2013 = summer_crop_2013
                        summer_crop_2014 = summer_crop_2014
                        summer_crop_2015 = summer_crop_2015
                        summer_crop_2016 = summer_crop_2009
                        summer_crop_2017 = summer_crop_2010

                        summer_crop_2018 = summer_crop_2014
                        summer_crop_2019 = summer_crop_2015
                        summer_crop_2020 = summer_crop_2009
                        summer_crop_2021 = summer_crop_2010
                        summer_crop_2022 = summer_crop_2011
                        summer_crop_2023 = summer_crop_2012
                        summer_crop_2024 = summer_crop_2013
                        summer_crop_2025 = summer_crop_2014
                        summer_crop_2026 = summer_crop_2015
                        summer_crop_2027 = summer_crop_2009

                        winter_crop_1999_2000 = winter_crop_2013_2014
                        winter_crop_2000_2001 = winter_crop_2014_2015
                        winter_crop_2001_2002 = winter_crop_2008_2009
                        winter_crop_2002_2003 = winter_crop_2009_2010
                        winter_crop_2003_2004 = winter_crop_2010_2011
                        winter_crop_2004_2005 = winter_crop_2011_2012
                        winter_crop_2005_2006 = winter_crop_2012_2013
                        winter_crop_2006_2007 = winter_crop_2013_2014
                        winter_crop_2007_2008 = winter_crop_2014_2015
                        winter_crop_2008_2009 = winter_crop_2008_2009
                        winter_crop_2009_2010 = winter_crop_2009_2010
                        winter_crop_2010_2011 = winter_crop_2010_2011
                        winter_crop_2011_2012 = winter_crop_2011_2012
                        winter_crop_2012_2013 = winter_crop_2012_2013
                        winter_crop_2013_2014 = winter_crop_2013_2014
                        winter_crop_2014_2015 = winter_crop_2014_2015
                        winter_crop_2015_2016 = winter_crop_2008_2009
                        winter_crop_2016_2017 = winter_crop_2009_2010

                        winter_crop_2017_2018 = winter_crop_2013_2014
                        winter_crop_2018_2019 = winter_crop_2014_2015
                        winter_crop_2019_2020 = winter_crop_2008_2009
                        winter_crop_2020_2021 = winter_crop_2009_2010
                        winter_crop_2021_2022 = winter_crop_2010_2011
                        winter_crop_2022_2023 = winter_crop_2011_2012
                        winter_crop_2023_2024 = winter_crop_2012_2013
                        winter_crop_2024_2025 = winter_crop_2013_2014
                        winter_crop_2025_2026 = winter_crop_2014_2015
                        winter_crop_2026_2027 = winter_crop_2008_2009

                        summer_cropList = [ summer_crop_2000, summer_crop_2001, summer_crop_2002, summer_crop_2003, summer_crop_2004, summer_crop_2005, summer_crop_2006, summer_crop_2007, summer_crop_2008, summer_crop_2009, summer_crop_2010, summer_crop_2011, summer_crop_2012, summer_crop_2013, summer_crop_2014, summer_crop_2015, summer_crop_2016, summer_crop_2017 ]
                        #print "\n\n     ...summer_cropList = " + str( summer_cropList ) + "\n"
                        winter_cropList = [ winter_crop_1999_2000, winter_crop_2000_2001, winter_crop_2001_2002, winter_crop_2002_2003, winter_crop_2003_2004, winter_crop_2004_2005, winter_crop_2005_2006, winter_crop_2006_2007, winter_crop_2007_2008, winter_crop_2008_2009, winter_crop_2009_2010, winter_crop_2010_2011, winter_crop_2011_2012, winter_crop_2012_2013, winter_crop_2013_2014, winter_crop_2014_2015, winter_crop_2015_2016, winter_crop_2016_2017 ]
                        #print "\n\n     ...winter_cropList = " + str( winter_cropList ) + "\n"

                        year = 1999

                        crop1_harvest_date_str = ""

                        if( current_or_future_management == 'current' ):
                            #initialize the harvest date string with a rational value for a date
                            # that won't likely conflict with the plant date for a winter crop or cover crop
                            crop1_harvest_date_str = "09/15/2000"
                            fileWriteString = fileWriteString + tab2 + "<CropScenario Name=\"Current\">\n" 
                            #tab1 = "\t"
                            #tab2 = "\t\t"
                            #tab3 = "\t\t\t"
                            #tab4 = "\t\t\t\t"
                            #tab5 = "\t\t\t\t\t"
                            #tab6 = "\t\t\t\t\t\t"
                            #tab7 = "\t\t\t\t\t\t\t"

                        if( current_or_future_management == 'future' ):
                            #initialize the harvest date string with a rational value for a date
                            # that won't likely conflict with the plant date for a winter crop or cover crop
                            crop1_harvest_date_str = "09/15/2018"
                            year = 2017
                            fileWriteString = fileWriteString + tab2 + "<CropScenario Name=\"" + practice + "\">\n" 
                            #tab1 = "\t"
                            #tab2 = "\t\t\t"
                            #tab3 = "\t\t\t\t"
                            #tab4 = "\t\t\t\t\t"
                            #tab5 = "\t\t\t\t\t\t"
                            #tab6 = "\t\t\t\t\t\t\t"
                            #tab7 = "\t\t\t\t\t\t\t\t"
                            summer_cropList = [ summer_crop_2018, summer_crop_2019, summer_crop_2020, summer_crop_2021, summer_crop_2022, summer_crop_2023, summer_crop_2024, summer_crop_2025, summer_crop_2026 , summer_crop_2027 ]
                            #print "\n\n     ...summer_cropList = " + str( summer_cropList ) + "\n"
                            winter_cropList = [ winter_crop_2017_2018, winter_crop_2018_2019, winter_crop_2019_2020, winter_crop_2020_2021, winter_crop_2021_2022, winter_crop_2022_2023, winter_crop_2023_2024, winter_crop_2024_2025 , winter_crop_2025_2026, winter_crop_2026_2027 ]
                            #print "\n\n     ...winter_cropList = " + str( winter_cropList ) + "\n"
                            
                        previous_crop = ""
                        
                        # crop sequences:
                        #summer_crop1        plant   harv    |   winter grain    plant   harv    |   summer_crop2         plant   harv    NOTES
                        #-----------------------------------|-----------------------------------|------------------------------------|------------------------------------------------------------------------------------------------------
                        #grass/hay          JAN     DEC     |   NULL                            |   grass/hay           JAN     DEC     no change
                        #grass/hay          JAN     DEC     |   NULL                            |   summer_crop/fallow   APRIL   OCT     no change
                        #grass/hay          JAN     DEC     |   NULL                            |   winter grain        NOV     JUN     end grass/hay before winter grain starts 
                        #grass/hay          JAN     DEC     |   winter grain    NOV     JUN     |   summer_crop/fallow   APRIL   OCT     end grass/hay before winter grain starts, end winter grain before summer crop 2 starts
                        #summer_crop/fallow  APRIL   OCT     |   NULL                            |   grass/hay           JAN     DEC     no change
                        #summer_crop/fallow  APRIL   OCT     |   NULL                            |   summer_crop/fallow   APRIL   OCT     no change
                        #summer_crop/fallow  APRIL   OCT     |   NULL                            |   winter grain        NOV     JUN     no change
                        #summer_crop/fallow  APRIL   OCT     |   winter grain    NOV     JUN     |   summer_crop/fallow   APRIL   OCT     harvest summer crop 1 before winter grain starts, harvest winter grain before summer crop 2 starts
                        #winter grain       NOV     JUN     |   NULL                            |   grass/hay           JAN     DEC     start grass/hay 2 after winter grain ends
                        #winter grain       NOV     JUN     |   NULL                            |   summer_crop/fallow   APRIL   OCT     harvest winter grain before summer crop 2 starts
                        #winter grain       NOV     JUN     |   NULL                            |   winter grain        NOV     JUN     no change
                        #winter grain       NOV     JUN     |   winter grain    NOV     JUN     |   summer_crop/fallow   APRIL   OCT     harvest winter grain before summer crop 2 starts
                        
                        for x in range( 0, len( summer_cropList ) ): 
                            
                            summer_crop = ""
                            winter_crop = ""
                            next_summer_crop = ""
                            
                            summer_crop_class = ""
                            winter_crop_class = ""
                            next_summer_crop_class = ""
                            previous_summer_crop_class = ""
                            
                            previous_summer_crop = ""
                            previous_winter_crop = ""
                            previous_winter_crop_class = ""
                            
                            #***Year
                            year = year + 1
                            year_str = str( year )
                            fileWriteString = fileWriteString + tab3 + "<CropYear Year=\"" + year_str + "\">\n" 

                            #***********************************************************************************************************
                            #******** Summer Crop ***********
                            #***********************************************************************************************************
                            
                            tillage_type = ""

                            #***********************************************************************************************************
                            # get the plant date for the next summer crop 
                            #***********************************************************************************************************
                            next_summer_crop = ""
                            next_cfarm_cropname = ""
                            next_summer_crop_plant_month = 0
                            next_summer_crop_plant_dayofmonth = 0
                            next_summer_crop_plant_dayofyear = 0
                            next_summer_crop_plant_date_str = '04/01/2000'
                            next_summer_crop_plant_date_d = datetime.strptime( next_summer_crop_plant_date_str, '%m/%d/%Y' )

                            if( year_str == "2017" or year_str == "2027" ): 
                                # set the next crop details to fix the plant month and date at the end of the current year
                                next_summer_crop = "" 
                                next_summer_crop_plant_month = 12
                                next_summer_crop_plant_dayofmonth = 31
                                next_summer_crop_plant_dayofyear = 365
                                next_summer_crop_plant_year = int( year_str )
                                next_summer_crop_plant_date_str = "12/31/" + year_str
                            
                            else:
                                # get the next crop details
                                next_summer_crop = summer_cropList[ x + 1 ]
                                if( next_summer_crop is None ): next_summer_crop = ""

                                if( practice == "Conversion to non-legume grassland reserve" and current_or_future_management == 'future' ):
                                    next_summer_crop = "grass_hay"
                                elif( practice == "Conversion to grass-legume grassland reserve" and current_or_future_management == 'future' ):
                                    next_summer_crop = "grass_hay"
                                elif( practice == "Conversion to grass-legume forage production" and current_or_future_management == 'future' ):
                                    next_summer_crop = "grass_hay"
                                
                                
                                #Get the next crop plant date
                                #print "id_mcfc = " + str( id_mcfc ) + ", year = " + str( year )
                                sql = "SELECT DISTINCT pc.cfarm_cropname1, pc.plant_month1, pc.plant_dayofmonth1, pc.plant_dayofyear1 FROM comet.planner_cropland_crops pc JOIN comet.planner_cropland_cps_list pcl ON pc.id_planner_cropland_cps_list = pcl.id WHERE pcl.irrigated = '" + irrigated + "' AND pcl.practice = '" + practice + "' AND pc.current_or_future = '" + current_or_future_management + "' AND pc.statecode = '" + statecode + "' AND pc.cdl_name = '" + next_summer_crop + "' AND sequence = 'summercrop';"
                                #print "\n      ...year = " + str( year )
                                #print "\n      ...sql = " + sql + "\n" 

                                cursor_next_summer_crop = mariadb_connection.cursor()
                                cursor_next_summer_crop.execute( sql )
                                data_next_summer_crop = cursor_next_summer_crop.fetchone()
                                cursor_next_summer_crop.close()

                                #get the plant date for the next crop
                                #check to see if the array is empty
                                if not data_next_summer_crop: 
                                    next_cfarm_cropname = ''
                                    next_summer_crop_plant_month = 12
                                    next_summer_crop_plant_dayofmonth = 31
                                    next_summer_crop_plant_dayofyear = 365
                                    next_summer_crop_plant_date_str = "12/31/" + year_str
                                else:                                
                                    next_cfarm_cropname = data_next_summer_crop[0]
                                    next_summer_crop_plant_month = data_next_summer_crop[1]
                                    next_summer_crop_plant_dayofmonth = data_next_summer_crop[2]
                                    next_summer_crop_plant_dayofyear = data_next_summer_crop[3]
                                    next_summer_crop_plant_year = year + 1


                                    next_summer_crop_plant_month_str = str( next_summer_crop_plant_month )
                                    if( next_summer_crop_plant_month < 10 ): next_summer_crop_plant_month_str = "0" + str( next_summer_crop_plant_month ) 

                                    next_summer_crop_plant_dayofmonth_str = str( next_summer_crop_plant_dayofmonth )
                                    if( next_summer_crop_plant_dayofmonth < 10 ): next_summer_crop_plant_dayofmonth_str = "0" + str( next_summer_crop_plant_dayofmonth )

                                    next_summer_crop_plant_year_str = str( next_summer_crop_plant_year )

                                    next_summer_crop_plant_date_str = next_summer_crop_plant_month_str + "/" + next_summer_crop_plant_dayofmonth_str + "/" + next_summer_crop_plant_year_str
                            
                                next_summer_crop_plant_date_d = datetime.strptime( next_summer_crop_plant_date_str, '%m/%d/%Y' )

                            #***********************************************************************************************************
                            # get the this year's winter crop details
                            #***********************************************************************************************************
                            
                            winter_crop_cfarm_cropname = ""
                            winter_crop_plant_date_str = ""
                            tillage2_date_str = ""
                            nfert2_date_str = ""
                            omad2_date_str = ""
                            winter_crop_continue_from_previous_year2 = ""
                            winter_crop_cfarm_cropname = ""
                            winter_crop_irrigated = ""
                            id_planner_cropland_crops2 = 0
                            winter_crop_plant_date_str = '12/01/2000'
                            winter_crop_plant_date_d = datetime.strptime( winter_crop_plant_date_str, '%m/%d/%Y' )
                            
                            if( current_or_future_management == 'future' and ( practice.lower().find( 'grassland reserve' ) != -1 or practice.lower().find( 'forage production' ) != -1 ) ):
                                winter_plant_date_str = ""
                                winter_crop = ""
                            else:
                                winter_plant_date_str = ""
                                winter_crop = winter_cropList[x]
                            
                            if( winter_crop is not None and winter_crop != '' ): 
                                #print "\n      ...winter_crop = " + str( winter_crop ) + "\n"

                                #Get the crop plant date, harvest date, irrigation amount from the database
                                sql = "SELECT DISTINCT pc.id as 'id_planner_cropland_crops', pc.statecode, pc.sequence, pc.cdl_name, pc.cropname1, pc.cfarm_cropname1, pc.irrigated1, pc.plant_month1, pc.plant_dayofmonth1, pc.plant_dayofyear1, pc.pltm_or_frst1 FROM comet.planner_cropland_crops pc JOIN comet.planner_cropland_cps_list pcl ON pc.id_planner_cropland_cps_list = pcl.id WHERE pcl.irrigated = '" + irrigated + "' AND pcl.practice = '" + practice + "' AND pc.current_or_future = '" + current_or_future_management + "' AND pc.statecode = '" + statecode + "' AND pc.cdl_name = '" + winter_crop + "' AND sequence = 'wintercrop';"
                                #print "\n      ...sql = " + sql + "\n"

                                cursor_winter_crop = mariadb_connection.cursor()
                                cursor_winter_crop.execute( sql )

                                data_crop = cursor_winter_crop.fetchone()

                                cursor_winter_crop.close()

                                id_planner_cropland_crops2 = data_crop[0]
                                statecode2 = data_crop[1]
                                sequence2 = data_crop[2]
                                cdl_name = data_crop[3]
                                cropname2 = data_crop[4]
                                cfarm_cropname2 = data_crop[5]
                                irrigated2 = data_crop[6]
                                plant_month2 = data_crop[7]
                                plant_dayofmonth2 = data_crop[8]
                                plant_dayofyear2 = data_crop[9]
                                pltm_or_frst2 = data_crop[10]

                                plant_month2_str = str( plant_month2 )
                                plant_dayofmonth2_str = str( plant_dayofmonth2 )
                                if len( str( plant_month2 ) ) == 1: plant_month2_str = "0" + plant_month2_str
                                if len( str( plant_dayofmonth2 ) ) == 1: plant_dayofmonth2_str = "0" + plant_dayofmonth2_str
                                winter_crop_plant_date_str = plant_month2_str + "/" + plant_dayofmonth2_str + "/" + year_str
                                winter_crop_plant_date_d = datetime.strptime( winter_crop_plant_date_str, '%m/%d/%Y' )

                                d = datetime.strptime( winter_crop_plant_date_str, '%m/%d/%Y' )
                                d = d - timedelta( days = 1 )
                                tillage2_date_str = d.strftime( '%m/%d/%Y' )
                                nfert2_date_str = winter_crop_plant_date_str
                                omad2_date_str = d.strftime( '%m/%d/%Y' )

                                winter_crop_continue_from_previous_year2 = "N"
                                winter_crop_cfarm_cropname = cfarm_cropname2
                                winter_crop_irrigated = irrigated2

                            #**********************************************************************************************************

                            if( summer_cropList[x] is not None and summer_cropList[x] != ''):
                                #Get the crop plant date, harvest date, irrigation amount from the database
                                
                                summer_crop = ""
                                if( practice == "Conversion to non-legume grassland reserve" and current_or_future_management == 'future' ):
                                    summer_crop = "grass_hay"
                                elif( practice == "Conversion to grass-legume grassland reserve" and current_or_future_management == 'future' ):
                                    summer_crop = "grass_hay"
                                elif( practice == "Conversion to grass-legume forage production" and current_or_future_management == 'future' ):
                                    summer_crop = "grass_hay"
                                else:
                                    summer_crop = str( summer_cropList[x] )

                                if( summer_crop is None ):
                                    summer_crop = ""

                                sql = "SELECT DISTINCT pc.id as 'id_planner_cropland_crops', pc.statecode, pc.sequence, pc.cdl_name, pc.cropname1, pc.cfarm_cropname1, pc.irrigated1, pc.plant_month1, pc.plant_dayofmonth1, pc.plant_dayofyear1, pc.harv_month1, pc.harv_dayofmonth1, pc.harv_dayofyear1, pc.pltm_or_frst1 FROM comet.planner_cropland_crops pc JOIN comet.planner_cropland_cps_list pcl ON pc.id_planner_cropland_cps_list = pcl.id WHERE pcl.irrigated = '" + irrigated + "' AND pcl.practice = '" + practice + "' AND pc.current_or_future = '" + current_or_future_management + "' AND pc.statecode = '" + statecode + "' AND pc.cdl_name = '" + str( summer_crop ) + "' and sequence = 'summercrop';" 
                                #print "\n      ...sql = " + sql + "\n"

                                cursor_summer_crop = mariadb_connection.cursor()
                                cursor_summer_crop.execute( sql )

                                data_crop = cursor_summer_crop.fetchone()

                                cursor_summer_crop.close()

                                #process the summer crop
                                id_planner_cropland_crops1 = data_crop[0]
                                statecode1 = data_crop[1]
                                sequence1 = data_crop[2]
                                cdl_name1 = data_crop[3]
                                cropname1 = data_crop[4]
                                cfarm_cropname1 = data_crop[5]
                                irrigated1 = data_crop[6]
                                plant_month1 = data_crop[7]
                                plant_dayofmonth1 = data_crop[8]
                                plant_dayofyear1 = data_crop[9]
                                harv_month1 = data_crop[10]
                                harv_dayofmonth1 = data_crop[11]
                                harv_dayofyear1 = data_crop[12]
                                pltm_or_frst1 = data_crop[13]

                                if cdl_name1 == 'fallow':
                                    plant_month1 = 5
                                    plant_dayofmonth1 = 1
                                    plant_dayofyear1 = 150
                                    harv_month1 = 9
                                    harv_dayofmonth1 = 30
                                    harv_dayofyear1 = 270
                                    pltm_or_frts1 = 'pltm'
                                    
                                #build plant/harvest month and day of month strings
                                plant_month1_str = str( plant_month1 )
                                plant_dayofmonth1_str = str( plant_dayofmonth1 )
                                harv_month1_str = str( harv_month1 )
                                harv_dayofmonth1_str = str( harv_dayofmonth1 )

                                if len( str( plant_month1 ) ) == 1: plant_month1_str = "0" + plant_month1_str
                                if len( str( plant_dayofmonth1 ) ) == 1: plant_dayofmonth1_str = "0" + plant_dayofmonth1_str
                                if len( str( harv_month1 ) ) == 1: harv_month1_str = "0" + harv_month1_str
                                if len( str( harv_dayofmonth1 ) ) == 1: harv_dayofmonth1_str = "0" + harv_dayofmonth1_str

                                plant1_str = plant_month1_str + "/" + plant_dayofmonth1_str + "/" + year_str
                                continue_from_previous_year1 = "N"

                                # set the crop classes for use later in this script
                                summer_crop_class = ""
                                winter_crop_class = ""
                                next_summer_crop_class = ""

                                if( summer_crop is None ):
                                    summer_crop_class = ""
                                elif( summer_crop == "" ):
                                    summer_crop_class = ""
                                elif( summer_crop.lower() in [ 'grass', 'grass-legume mix', 'grass_legume mix', 'grass_clover mix', 'grass_hay', 'alfalfa', 'grass_pasture' ] ):
                                    summer_crop_class = "perennial"
                                elif( summer_crop.lower() in [ 'winter wheat', 'winter barley', 'winter oats' ] ):
                                    summer_crop_class = "winter"
                                else:
                                    summer_crop_class = "summer"

                                if( winter_crop is None ):
                                    winter_crop_class = ""
                                elif( winter_crop == "" ):
                                    winter_crop_class = ""
                                elif( winter_crop.lower() in [ 'grass', 'grass-legume mix', 'grass_legume mix', 'grass_clover mix', 'grass_hay', 'alfalfa', 'grass_pasture' ] ):
                                    winter_crop_class = "perennial"
                                elif( winter_crop.lower() in [ 'winter wheat', 'winter barley', 'winter oats' ] ):
                                    winter_crop_class = "winter"
                                else:
                                    winter_crop_class = "summer"

                                if( next_summer_crop is None ):
                                    next_summer_crop_class = ""
                                elif( next_summer_crop == "" ):
                                    next_summer_crop_class = ""
                                elif( next_summer_crop.lower() in [ 'grass', 'grass-legume mix', 'grass_legume mix', 'grass_clover mix', 'grass_hay', 'alfalfa', 'grass_pasture' ] ):
                                    next_summer_crop_class = "perennial"
                                elif( next_summer_crop.lower() in [ 'winter wheat', 'winter barley', 'winter oats' ] ):
                                    next_summer_crop_class = "winter"
                                else:
                                    next_summer_crop_class = "summer"
                                    
                                #If the crop is a perennial, set the start date to 01/03/<year> and the start type to frst
                                if( summer_crop_class == "perennial" or pltm_or_frst1 == 'frst' ):
                                    continue_from_previous_year1 = "Y"
                                    pltm_or_frst1 = "frst"
                                    plant1_str = "01/03/" + year_str
                                    plant_month1 = 1
                                    plant_dayofmonth1 = 3
                                    plant_month1_str = "01"
                                    plant_dayofmonth1_str = "03"

                                #trap errors with dates of 07/33/yyyy
                                if( plant_month1_str == "07" and plant_dayofmonth1_str == "33" ): 
                                    plant_month1_str = "08"
                                    plant_dayofmonth1_str = "02"

                                plant1_str = plant_month1_str + "/" + plant_dayofmonth1_str + "/" + year_str

                                # if the summer crop is a winter grain, and the previous summer crop class and winter crop classes are not a winter crop, 
                                # then plant the winter wheat in January
                                if( summer_crop_class == "winter" and previous_summer_crop_class != "winter" and previous_winter_crop_class != "winter" ):
                                    plant1_str = "01/05/" + year_str
                                
                                plant1_d = datetime.strptime( plant1_str, '%m/%d/%Y' )

                                # set the tillage, nfert and omad application dates
                                d = datetime.strptime( plant1_str, '%m/%d/%Y' )
                                d = d - timedelta( days = 1 )
                                tillage1_date_str = d.strftime( '%m/%d/%Y' )
                                nfert1_date_str = plant1_str
                                omad1_date_str = d.strftime( '%m/%d/%Y' )
                                
                                if( practice.lower().find( 'reserve' ) > -1 and current_or_future_management == 'future' ):
                                    continue_from_previous_year1 = 'Y'

                                if( cfarm_cropname1 is not None ):
                                    #print "\n     ...cfarm_cropname1 = " + str( cfarm_cropname1 ) + "\n"
                                    fileWriteString = fileWriteString + tab4 + "<Crop CropNumber=\"1\">\n" 
                                    fileWriteString = fileWriteString + tab5 + "<CropName>" + cfarm_cropname1 + "</CropName>\n" 

                                    fileWriteString = fileWriteString + tab5 + "<PlantingDate>" + plant1_str + "</PlantingDate>\n" 
                                    fileWriteString = fileWriteString + tab5 + "<ContinueFromPreviousYear>" + continue_from_previous_year1 + "</ContinueFromPreviousYear>\n" 

                                    #***Harvests

                                    fileWriteString = fileWriteString + tab5 + "<HarvestList>\n" 
                                    # loop through harvest events
                                    sql = "SELECT DISTINCT pch.month, pch.day_of_month, pch.day_of_year as 'harv_day_of_year', pch.number_of_harvests, pch.grain, pch.yield as 'yield1', pch.strawstoverhayremoval FROM comet.planner_cropland_harvests pch JOIN comet.planner_cropland_crops pc ON pch.id_planner_cropland_crops = pc.id WHERE pch.id_planner_cropland_crops = " + str( id_planner_cropland_crops1 ) + " AND pc.sequence = 'summercrop' ORDER BY day_of_year;"
                                    #print "\n      ...sql = " + sql + "\n"
                                    cursor_harvests = mariadb_connection.cursor()
                                    cursor_harvests.execute( sql )
                                    
                                    crop1_harvest_date_str = ""
                                    for( month, day_of_month, harv_day_of_year, number_of_harvests, grain, yield1, strawstoverhayremoval ) in cursor_harvests:

                                        if( yield1 == "None" or yield1 is None ):
                                            yield1 = "0"
                                            
                                        if( cfarm_cropname1 == 'fallow' ):
                                            grain = "No"

                                        if( int( month ) == 2 and int( day_of_month ) == 29 ):
                                            day_of_month = 28

                                        month_str = str( month )
                                        day_of_month_str = str( day_of_month )

                                        if len( str( month ) ) == 1 : month_str = "0" + str( month ) 
                                        if len( str( day_of_month ) ) == 1: day_of_month_str = "0" + str( day_of_month ) 
                                        if( day_of_month_str == "00" ): day_of_month_str = "01"

                                        #if( summer_crop_class == "winter" and winter_crop_class == "" ):
                                        #    crop1_harvest_date_str = month_str + "/" + day_of_month_str + "/" + str( year + 1 )
                                        #else:
                                        #    crop1_harvest_date_str = month_str + "/" + day_of_month_str + "/" + year_str
                                        
                                        crop1_harvest_date_str = month_str + "/" + day_of_month_str + "/" + year_str
                                        crop1_harvest_date_d = d = datetime.strptime( crop1_harvest_date_str, '%m/%d/%Y' )
                                        
                                        harvest_date_str = crop1_harvest_date_str
                                        harvest_date_d = crop1_harvest_date_d
                                        print_harvest_event = "yes"
                                        summer_crop_harvest_date_str = harvest_date_str
                                        
                                        # crop sequences where date changes might be needed
                                        #summer_crop1        plant   harv    |   winter grain    plant   harv    |   summer_crop2         plant   harv    NOTES
                                        #-----------------------------------|-----------------------------------|------------------------------------|------------------------------------------------------------------------------------------------------
                                        #grass/hay          JAN     DEC     |   NULL                            |   winter grain        NOV     JUN     end grass/hay before winter grain starts 
                                        # check if the harvest date of the current perennial crop is later than the plant date of the next winter grain crop.
                                        # if so, don't print this harvest event
                                        if( summer_crop_class == "perennial" and winter_crop_class == "" and next_summer_crop_class == "winter"):
                                            if( harvest_date_d > next_summer_crop_plant_date_d ):
                                                #There are likely harvest dates preceding this one, so don't harvest
                                                print_harvest_event = "no"
                                        
                                        #grass/hay          JAN     DEC     |   winter grain    NOV     JUN     |   summer_crop/fallow   APRIL   OCT     end grass/hay before winter grain starts, end winter grain before summer crop 2 starts
                                        if( summer_crop_class == "perennial" and winter_crop_class == "winter" ):
                                            if( harvest_date_d > winter_crop_plant_date_d ):
                                                #There are likely harvest dates preceding this one, so don't harvest
                                                print_harvest_event = "no"
                                        
                                        #summer_crop/fallow  APRIL   OCT     |   winter grain    NOV     JUN     |   summer_crop/fallow   APRIL   OCT     harvest summer crop 1 before winter grain starts, harvest winter grain before summer crop 2 starts
                                        if( summer_crop_class == "summer" and winter_crop_class == "winter" ):
                                            if( harvest_date_d > winter_crop_plant_date_d ):
                                                harvest_date_d = winter_crop_plant_date_d - timedelta( days = 3 )
                                                harvest_date_str = harvest_date_d.strftime( '%m/%d/%Y' )
                                            print_harvest_event = "yes"
                                        
                                        #winter grain       NOV     JUN     |   NULL                            |   grass/hay           JAN     DEC     start grass/hay 2 after winter grain ends
                                        if( summer_crop_class == "winter" and winter_crop_class == "" and next_summer_crop_class == "perennial"):
                                            harvest_date_str = "12/28/" + year_str
                                            print_harvest_event = "yes"

                                        #winter grain       NOV     JUN     |   NULL                            |   summer_crop/fallow   APRIL   OCT     harvest winter grain before summer crop 2 starts
                                        if( summer_crop_class == "winter" and winter_crop_class == "" and next_summer_crop_class == "summer"):
                                            if( harvest_date_d > next_summer_crop_plant_date_d ):
                                                harvest_date_d = next_summer_crop_plant_date_d - timedelta( days = 3 )
                                                harvest_date_str = harvest_date_d.strftime( '%m/%d/%Y' )
                                            print_harvest_event = "yes"

                                        #winter grain       NOV     JUN     |   winter grain    NOV     JUN     |   summer_crop/fallow   APRIL   OCT     harvest winter grain before summer crop 2 starts
                                        if( summer_crop_class == "winter" and winter_crop_class == "winter" ):
                                            if( harvest_date_d > winter_crop_plant_date_d ):
                                                harvest_date_d = winter_crop_plant_date_d - timedelta( days = 3 )
                                                harvest_date_str = harvest_date_d.strftime( '%m/%d/%Y' )
                                            print_harvest_event = "yes"
                                            
                                        summer_crop_harvest_date_d = harvest_date_d

                                        if( print_harvest_event == "yes" ):
                                            fileWriteString = fileWriteString + tab6 + "<HarvestEvent>\n" 
                                            fileWriteString = fileWriteString + tab7 + "<HarvestDate>" + harvest_date_str + "</HarvestDate>\n" 
                                            fileWriteString = fileWriteString + tab7 + "<Grain>" + grain + "</Grain>\n" 
                                            fileWriteString = fileWriteString + tab7 + "<yield>" + str( yield1 ) + "</yield>\n" 
                                            fileWriteString = fileWriteString + tab7 + "<StrawStoverHayRemoval>" + str( strawstoverhayremoval ) + "</StrawStoverHayRemoval>\n" 
                                            fileWriteString = fileWriteString + tab6 + "</HarvestEvent>\n" 

                                    fileWriteString = fileWriteString + tab5 + "</HarvestList>\n" 
                                    cursor_harvests.close()

                                    #***Grazing
                                    # I am simulating this like we do harvests

                                    fileWriteString = fileWriteString + tab5 + "<GrazingList>\n" 

                                    if( cropname1 == 'grass_pasture' ):
                                        # loop through harvest events
                                        sql = "SELECT DISTINCT pch.start_month as start_grazing_month, pch.start_day_of_month as start_grazing_day_of_month, pch.start_day_of_year as start_grazing_day_of_year, pch.end_month as end_grazing_month, pch.end_day_of_month as end_grazing_day_of_month, pch.end_day_of_year as end_grazing_day_of_year, pch.rest_period, pch.utilization_pct FROM comet.planner_cropland_grazing pch JOIN comet.planner_cropland_crops pc ON pch.id_planner_cropland_crops = pc.id WHERE pch.id_planner_cropland_crops = " + str( id_planner_cropland_crops1 ) + " AND pc.sequence = 'summercrop' ORDER BY start_day_of_year;"
                                        #print "\n      ...sql = " + sql + "\n"
                                        cursor_grazing = mariadb_connection.cursor()
                                        cursor_grazing.execute( sql )

                                        print_grazing_event = ""
                                        
                                        for( start_grazing_month, start_grazing_day_of_month, start_grazing_day_of_year, end_grazing_month, end_grazing_day_of_month, end_grazing_day_of_year, rest_period, utilization_pct ) in cursor_grazing:

                                            if( int( start_grazing_month ) == 2 and int( start_grazing_day_of_month ) == 29 ):
                                                start_grazing_day_of_month = 28

                                            start_grazing_month_str = str( int( start_grazing_month ) )
                                            start_grazing_day_of_month_str = str( int( start_grazing_day_of_month ) )

                                            if len( str( start_grazing_month ) ) == 1 : start_grazing_month_str = "0" + str( start_grazing_month ) 
                                            if len( str( int( start_grazing_day_of_month ) ) ) == 1: start_grazing_day_of_month_str = "0" + str( int( start_grazing_day_of_month ) ) 

                                            start_grazing_date_str = start_grazing_month_str + "/" + start_grazing_day_of_month_str + "/" + year_str
                                            start_grazing_date_d = datetime.strptime( start_grazing_date_str, '%m/%d/%Y' )

                                            if( int( end_grazing_month ) == 2 and int( end_grazing_day_of_month ) == 29 ):
                                                end_grazing_day_of_month = 28

                                            end_grazing_month_str = str( int( end_grazing_month ) )
                                            end_grazing_day_of_month_str = str( int( end_grazing_day_of_month ) )

                                            if len( str( end_grazing_month ) ) == 1 : end_grazing_month_str = "0" + str( end_grazing_month ) 
                                            if len( str( int( end_grazing_day_of_month ) ) ) == 1: end_grazing_day_of_month_str = "0" + str( int( end_grazing_day_of_month ) ) 

                                            end_grazing_date_str = end_grazing_month_str + "/" + end_grazing_day_of_month_str + "/" + year_str
                                            end_grazing_date_d = datetime.strptime( end_grazing_date_str, '%m/%d/%Y' )

                                            if( summer_crop_class == "perennial" and winter_crop_class == "winter" ):
                                                if( start_grazing_date_d > winter_crop_plant_date_d ):
                                                    #don't graze
                                                    print_grazing_event = "no"
                                                if( start_grazing_date_d < winter_crop_plant_date_d and end_grazing_date_d > winter_crop_plant_date_d ):
                                                    # adjust the end grazing date to be 3 days before planting the winter crop
                                                    end_grazing_date_d = winter_crop_plant_date_d - timedelta( days = 3 )
                                                    end_grazing_date_str = end_grazing_date_d.strftime( '%m/%d/%Y' )
                                                    print_grazing_event = "yes"

                                            if( summer_crop_class == "perennial" and next_summer_crop_class == "winter" ):
                                                if( start_grazing_date_d > next_summer_crop_plant_date_d ):
                                                    #don't graze
                                                    print_grazing_event = "no"
                                                if( start_grazing_date_d < next_summer_crop_plant_date_d and end_grazing_date_d > winter_crop_plant_date_d ):
                                                    # adjust the end grazing date to be 3 days before planting the winter crop
                                                    end_grazing_date_d = winter_crop_plant_date_d - timedelta( days = 3 )
                                                    end_grazing_date_str = end_grazing_date_d.strftime( '%m/%d/%Y' )
                                                    print_grazing_event = "yes"

                                            if( print_grazing_event == "yes" ):
                                                fileWriteString = fileWriteString + tab6 + "<GrazingEvent>\n" 
                                                fileWriteString = fileWriteString + tab7 + "<GrazingStartDate>" + start_grazing_date_str + "</GrazingStartDate>\n" 
                                                fileWriteString = fileWriteString + tab7 + "<GrazingEndDate>" + end_grazing_date_str + "</GrazingEndDate>\n" 
                                                fileWriteString = fileWriteString + tab7 + "<RestPeriod>" + str( int( rest_period ) ) + "</RestPeriod>\n" 
                                                fileWriteString = fileWriteString + tab7 + "<UtilizationPct>" + str( int( utilization_pct ) ) + "</UtilizationPct>\n" 
                                                fileWriteString = fileWriteString + tab6 + "</GrazingEvent>\n" 

                                        cursor_grazing.close()

                                    fileWriteString = fileWriteString + tab5 + "</GrazingList>\n" 

                                    #*** Tillage
                                    fileWriteString = fileWriteString + tab5 + "<TillageList>\n" 
                                    # loop through Tillage events
                                    sql = "SELECT DISTINCT pch.month, pch.day_of_month, pch.day_of_year, pch.tillage_type FROM comet.planner_cropland_tillage pch JOIN comet.planner_cropland_crops pc ON pch.id_planner_cropland_crops = pc.id WHERE pch.id_planner_cropland_crops = " + str( id_planner_cropland_crops1 ) + " AND pc.sequence = 'summercrop' ORDER BY day_of_year;"
                                    #print "\n      ...sql = " + sql + "\n"
                                    cursor_tillages = mariadb_connection.cursor()
                                    cursor_tillages.execute( sql )

                                    for( month, day_of_month, day_of_year, tillage_type ) in cursor_tillages:

                                        #reset the tillage type to no tillage if this is a perennial crop following another perennial crop
                                        if( cropname1 in [ 'grass', 'grass-legume mix', 'grass_legume mix', 'grass_clover mix', 'grass_hay', 'alfalfa', 'grass_pasture' ] and previous_crop in [ 'grass', 'grass-legume mix', 'grass_legume mix', 'grass_clover mix', 'grass_hay', 'alfalfa', 'grass_pasture' ] ):
                                            #don't print a tillage event
                                            tillage_type = "No Tillage"
                                        else:
                                            #print a tillage event
                                            fileWriteString = fileWriteString + tab6 + "<TillageEvent>\n" 
                                            fileWriteString = fileWriteString + tab7 + "<TillageDate>" + tillage1_date_str + "</TillageDate>\n" 
                                            fileWriteString = fileWriteString + tab7 + "<TillageType>" + tillage_type + "</TillageType>\n" 
                                            fileWriteString = fileWriteString + tab6 + "</TillageEvent>\n" 

                                    cursor_tillages.close()
                                    fileWriteString = fileWriteString + tab5 + "</TillageList>\n" 

                                    #*** N Fertilization
                                    fileWriteString = fileWriteString + tab5 + "<NApplicationList>\n" 
                                    # loop through NFert events


                                    sql = "SELECT DISTINCT pch.month, pch.day_of_month, pch.day_of_year, pch.nfert_type, pch.nfert_amount, pch.nfert_application_method, pch.nfert_eep FROM comet.planner_cropland_nfert pch JOIN comet.planner_cropland_crops pc ON pch.id_planner_cropland_crops = pc.id WHERE pch.id_planner_cropland_crops = " + str( id_planner_cropland_crops1 ) + " AND pc.sequence = 'summercrop' ORDER BY day_of_year;"
                                    #print "\n      ...sql = " + sql + "\n"
                                    cursor_nfert = mariadb_connection.cursor()
                                    cursor_nfert.execute( sql )

                                    for( month, day_of_month, day_of_year, nfert_type, nfert_amount, nfert_application_method, nfert_eep ) in cursor_nfert:

                                        nfert_amount_temp = nfert_amount
                                        #lower the N rate according to plot defined 
                                        if( practice.lower().find( 'compost' ) > -1 or practice.lower().find( 'manure' ) > -1 ):
                                            if( year == 2018 ): nfert_amount_temp = nfert_amount * ( 1 - 0.10 )
                                            if( year == 2019 ): nfert_amount_temp = nfert_amount * ( 1 - 0.15 )
                                            if( year == 2020 ): nfert_amount_temp = nfert_amount * ( 1 - 0.175 )
                                            if( year == 2021 ): nfert_amount_temp = nfert_amount * ( 1 - 0.1875 )
                                            if( year == 2022 ): nfert_amount_temp = nfert_amount * ( 1 - 0.19375 )
                                            if( year == 2023 ): nfert_amount_temp = nfert_amount * 0.8
                                            if( year == 2024 ): nfert_amount_temp = nfert_amount * 0.8
                                            if( year == 2025 ): nfert_amount_temp = nfert_amount * 0.8
                                            if( year == 2026 ): nfert_amount_temp = nfert_amount * 0.8
                                            if( year == 2027 ): nfert_amount_temp = nfert_amount * 0.8

                                        fileWriteString = fileWriteString + tab6 + "<NApplicationEvent>\n" 
                                        fileWriteString = fileWriteString + tab7 + "<NApplicationDate>" + nfert1_date_str + "</NApplicationDate>\n" 
                                        fileWriteString = fileWriteString + tab7 + "<NApplicationType>" + nfert_type + "</NApplicationType>\n" 
                                        fileWriteString = fileWriteString + tab7 + "<NApplicationAmount>" + str( nfert_amount_temp ) + "</NApplicationAmount>\n" 
                                        fileWriteString = fileWriteString + tab7 + "<NApplicationMethod>" + nfert_application_method + "</NApplicationMethod>\n" 
                                        fileWriteString = fileWriteString + tab7 + "<EEP>" + nfert_eep + "</EEP>\n" 
                                        fileWriteString = fileWriteString + tab6 + "</NApplicationEvent>\n" 

                                    cursor_nfert.close()

                                    fileWriteString = fileWriteString + tab5 + "</NApplicationList>\n" 

                                    #*** Manure/Compost
                                    fileWriteString = fileWriteString + tab5 + "<OMADApplicationList>\n" 
                                    # loop through OMAD events
                                    sql = "SELECT DISTINCT pch.month, pch.day_of_month, pch.day_of_year, pch.omad_type, pch.omad_amount, pch.omad_percent_n, pch.omad_cn_ratio FROM comet.planner_cropland_omad pch JOIN comet.planner_cropland_crops pc ON pch.id_planner_cropland_crops = pc.id WHERE pc.cdl_name not like '%rice%' AND pch.id_planner_cropland_crops = " + str( id_planner_cropland_crops1 ) + " AND pc.sequence = 'summercrop' ORDER BY day_of_year;"
                                    #print "\n      ...sql = " + sql + "\n"
                                    cursor_omad = mariadb_connection.cursor()
                                    cursor_omad.execute( sql )

                                    for( month, day_of_month, day_of_year, omad_type, omad_amount, omad_percent_n, omad_cn_ratio ) in cursor_omad:

                                        fileWriteString = fileWriteString + tab6 + "<OMADApplicationEvent>\n" 
                                        fileWriteString = fileWriteString + tab7 + "<OMADApplicationDate>" + omad1_date_str + "</OMADApplicationDate>\n" 
                                        fileWriteString = fileWriteString + tab7 + "<OMADType>" + omad_type + "</OMADType>\n" 
                                        fileWriteString = fileWriteString + tab7 + "<OMADAmount>" + str( omad_amount ) + "</OMADAmount>\n" 
                                        fileWriteString = fileWriteString + tab7 + "<OMADPercentN>" + str( omad_percent_n ) + "</OMADPercentN>\n" 
                                        fileWriteString = fileWriteString + tab7 + "<OMADCNRatio>" + str( omad_cn_ratio ) + "</OMADCNRatio>\n" 
                                        fileWriteString = fileWriteString + tab6 + "</OMADApplicationEvent>\n" 

                                    cursor_omad.close()

                                    fileWriteString = fileWriteString + tab5 + "</OMADApplicationList>\n" 

                                    #*** Irrigation
                                    fileWriteString = fileWriteString + tab5 + "<IrrigationList>\n" 

                                    if( irrigated == 'Y' ):
                                    # loop through Irrigation events
                                        sql = "SELECT DISTINCT pch.month, pch.day_of_month, pch.day_of_year, pch.irrig_amount FROM comet.planner_cropland_irrig pch JOIN comet.planner_cropland_crops pc ON pch.id_planner_cropland_crops = pc.id WHERE pch.id_planner_cropland_crops = " + str( id_planner_cropland_crops1 ) + " AND ( pc.sequence = 'summercrop' OR pc.cdl_name in ( 'winter wheat', 'winter oats', 'winter barley' ) ) ORDER BY day_of_year;"
                                        #print "\n      ...sql = " + sql + "\n"
                                        cursor_irrigation = mariadb_connection.cursor()
                                        cursor_irrigation.execute( sql )

                                        for( month, day_of_month, day_of_year, irrig_amount ) in cursor_irrigation:

                                            if( int( month ) == 2 and int( day_of_month ) == 29 ):
                                                day_of_month = 28

                                            month_str = str( month )
                                            day_of_month_str = str( day_of_month )

                                            if len( str( month ) ) == 1 : month_str = "0" + str( month ) 
                                            if len( str( day_of_month ) ) == 1: day_of_month_str = "0" + str( day_of_month ) 

                                            date_str = month_str + "/" + day_of_month_str + "/" + year_str

                                            fileWriteString = fileWriteString + tab6 + "<IrrigationEvent>\n" 
                                            fileWriteString = fileWriteString + tab7 + "<IrrigationDate>" + date_str + "</IrrigationDate>\n" 
                                            fileWriteString = fileWriteString + tab7 + "<IrrigationInches>" + str( irrig_amount ) + "</IrrigationInches>\n" 
                                            fileWriteString = fileWriteString + tab6 + "</IrrigationEvent>\n" 

                                        cursor_irrigation.close()

                                    fileWriteString = fileWriteString + tab5 + "</IrrigationList>\n" 

                                    fileWriteString = fileWriteString + tab4 + "</Crop>\n" 

                                    #****************
                                    #cover crop block
                                    #****************

                                    cfarm_cropname2 = ""
                                    if( 
                                        practice.lower().find( 'reserve' ) == -1 and \
                                        current_or_future_management == 'future' and \
                                        ( winter_crop is None or winter_crop == '' ) and \
                                        summer_crop.lower() not in [ 'grass', 'grass-legume mix', 'grass_legume mix', 'grass_clover mix', 'grass_hay', 'alfalfa', 'grass_pasture', 'winter wheat', 'winter oats', 'winter barley', 'winter rye', 'rye' ] and \
                                        next_summer_crop.lower() not in [ 'grass', 'grass-legume mix', 'grass_legume mix', 'grass_clover mix', 'grass_hay', 'alfalfa', 'grass_pasture', 'winter wheat', 'winter oats', 'winter barley', 'winter rye', 'rye' ] and \
                                        ( practice.lower().find( 'cover crop' ) > -1 ) ):
                                        
                                        # initialize the string variables to be used
                                        covercrop_plant_month_str = ""
                                        covercrop_plant_dayofmonth_str = ""

                                        # set the plant date to be one day after the crop 1 harvest date
                                        d = datetime.strptime( crop1_harvest_date_str, '%m/%d/%Y' )
                                        d = d + timedelta( days = 1 )
                                        covercrop_plant_date_str = d.strftime( '%m/%d/%Y' )

                                        # set the cover crop type
                                        if practice.lower().find( 'use of a annual grass cover crop' ) > -1:
                                            cfarm_cropname2 = 'RYE'

                                        if practice.lower().find( 'use of a legume cover crop' ) > -1:
                                            cfarm_cropname2 = 'VETCH'

                                        if practice.lower().find( 'use of a legume - annual grass cover crop' ) > -1:
                                            cfarm_cropname2 = 'RYELG'

                                        # build the cover crop kill date string
                                        covercrop_kill_date_str = next_summer_crop_plant_date_str
                                        d = datetime.strptime( covercrop_kill_date_str, '%m/%d/%Y' )
                                        d = d - timedelta( days = 7 )
                                        covercrop_kill_date_str = d.strftime( '%m/%d/%Y' )

                                        # write the crop data to the .xml file
                                        fileWriteString = fileWriteString + tab4 + "<Crop CropNumber=\"-2\">\n" 
                                        fileWriteString = fileWriteString + tab5 + "<CropName>" + cfarm_cropname2 + "</CropName>\n" 

                                        fileWriteString = fileWriteString + tab5 + "<PlantingDate>" + covercrop_plant_date_str + "</PlantingDate>\n" 
                                        fileWriteString = fileWriteString + tab5 + "<ContinueFromPreviousYear>N</ContinueFromPreviousYear>\n" 
                                        fileWriteString = fileWriteString + tab5 + "<HarvestList>\n" 
                                        fileWriteString = fileWriteString + tab6 + "<HarvestEvent>\n" 
                                        fileWriteString = fileWriteString + tab7 + "<HarvestDate>" + covercrop_kill_date_str + "</HarvestDate>\n" 
                                        fileWriteString = fileWriteString + tab7 + "<Grain>No</Grain>\n" 
                                        fileWriteString = fileWriteString + tab7 + "<yield>1</yield>\n" 
                                        fileWriteString = fileWriteString + tab7 + "<StrawStoverHayRemoval>0</StrawStoverHayRemoval>\n" 
                                        fileWriteString = fileWriteString + tab6 + "</HarvestEvent>\n" 
                                        fileWriteString = fileWriteString + tab5 + "</HarvestList>\n" 

                                        fileWriteString = fileWriteString + tab5 + "<GrazingList>\n" 
                                        fileWriteString = fileWriteString + tab5 + "</GrazingList>\n" 

                                        fileWriteString = fileWriteString + tab5 + "<TillageList>\n" 
                                        fileWriteString = fileWriteString + tab5 + "</TillageList>\n" 

                                        fileWriteString = fileWriteString + tab5 + "<NApplicationList>\n" 
                                        fileWriteString = fileWriteString + tab5 + "</NApplicationList>\n" 

                                        fileWriteString = fileWriteString + tab5 + "<OMADApplicationList>\n" 
                                        fileWriteString = fileWriteString + tab5 + "</OMADApplicationList>\n" 

                                        fileWriteString = fileWriteString + tab5 + "<IrrigationList>\n" 
                                        fileWriteString = fileWriteString + tab5 + "</IrrigationList>\n" 

                                        fileWriteString = fileWriteString + tab4 + "</Crop>\n" 

                            previous_summer_crop = summer_crop
                            previous_summer_crop_class = summer_crop_class

                            #********************************
                            #******** Winter Crop ***********
                            #********************************

                            #not cover crop and not grassland reserve
                            if( \
                            ( winter_crop != '' and practice.lower().find( 'reserve' ) == -1 and practice.lower().find( 'cover crop') == -1 and current_or_future_management == 'future' ) or \
                            ( winter_crop != '' and next_summer_crop_class != "perennial" ) \
                            ):

                                fileWriteString = fileWriteString + tab4 + "<Crop CropNumber=\"2\">\n" 
                                fileWriteString = fileWriteString + tab5 + "<CropName>" + winter_crop_cfarm_cropname + "</CropName>\n" 

                                fileWriteString = fileWriteString + tab5 + "<PlantingDate>" + winter_crop_plant_date_str + "</PlantingDate>\n" 
                                fileWriteString = fileWriteString + tab5 + "<ContinueFromPreviousYear>" + winter_crop_continue_from_previous_year2 + "</ContinueFromPreviousYear>\n" 

                                #***Harvests
                                fileWriteString = fileWriteString + tab5 + "<HarvestList>\n" 

                                # loop through harvest events
                                sql = "SELECT DISTINCT pch.month, pch.day_of_month, pch.day_of_year, pch.number_of_harvests, pch.grain, pch.yield as 'yield1', pch.strawstoverhayremoval FROM comet.planner_cropland_harvests pch JOIN comet.planner_cropland_crops pc ON pch.id_planner_cropland_crops = pc.id WHERE pch.id_planner_cropland_crops = " + str( id_planner_cropland_crops2 ) + " AND pc.sequence = 'wintercrop' ORDER BY day_of_year;"
                                #print "\n      ...sql = " + sql + "\n"
                                cursor_harvests = mariadb_connection.cursor()
                                cursor_harvests.execute( sql )

                                print_winter_crop_harvest_event = "yes"
                                for( month, day_of_month, day_of_year, number_of_harvests, grain, yield1, strawstoverhayremoval ) in cursor_harvests:

                                    if( int( month ) == 2 and int( day_of_month ) == 29 ):
                                        day_of_month = 28

                                    month_str = str( month )
                                    day_of_month_str = str( day_of_month )

                                    if len( str( month ) ) == 1 : month_str = "0" + str( month ) 
                                    if len( str( day_of_month ) ) == 1: day_of_month_str = "0" + str( day_of_month ) 

                                    if( day_of_month_str == "00" ):
                                        day_of_month_str = "01"

                                    winter_crop_harvest_date_str = month_str + "/" + day_of_month_str + "/" + str( year + 1 )
                                    winter_crop_harvest_date_d = d.strptime( winter_crop_harvest_date_str, '%m/%d/%Y' )

                                    # crop sequences where date changes might be needed
                                    if( winter_crop_class == "winter" and next_summer_crop_class in [ "summer" ] ):
                                        winter_crop_harvest_date_d = next_summer_crop_plant_date_d - timedelta( days = 3 )
                                        winter_crop_harvest_date_str = winter_crop_harvest_date_d.strftime( '%m/%d/%Y' )
                                        print_winter_harvest_event = "yes"
                                        
                                    if( ( winter_crop_class == "winter" and next_summer_crop_class == "perennial" ) or year == 2015 or year == 2025 ):
                                        winter_crop_harvest_date_str = "12/28/" + year_str
                                        winter_crop_harvest_date_d = datetime.strptime( winter_crop_harvest_date_str, '%m/%d/%Y' )
                                        print_winter_crop_harvest_event = "yes"

                                    if( winter_crop_class == "winter" and next_summer_crop_class == "winter" ):
                                        winter_crop_harvest_date_str = "12/28/" + year_str
                                        winter_crop_harvest_date_d = datetime.strptime( winter_crop_harvest_date_str, '%m/%d/%Y' )
                                        print_winter_crop_harvest_event = "no"

                                    if( print_winter_crop_harvest_event ):
                                        fileWriteString = fileWriteString + tab6 + "<HarvestEvent>\n" 
                                        fileWriteString = fileWriteString + tab7 + "<HarvestDate>" + winter_crop_harvest_date_str + "</HarvestDate>\n" 
                                        fileWriteString = fileWriteString + tab7 + "<Grain>" + grain + "</Grain>\n" 
                                        fileWriteString = fileWriteString + tab7 + "<yield>" + str( yield1 ) + "</yield>\n" 
                                        fileWriteString = fileWriteString + tab7 + "<StrawStoverHayRemoval>" + str( strawstoverhayremoval ) + "</StrawStoverHayRemoval>\n" 
                                        fileWriteString = fileWriteString + tab6 + "</HarvestEvent>\n" 

                                cursor_harvests.close()

                                fileWriteString = fileWriteString + tab5 + "</HarvestList>\n" 

                                #***Grazing
                                fileWriteString = fileWriteString + tab5 + "<GrazingList>\n" 
                                fileWriteString = fileWriteString + tab5 + "</GrazingList>\n" 

                                #*** Tillage
                                fileWriteString = fileWriteString + tab5 + "<TillageList>\n" 
                                # loop through Tillage events
                                sql = "SELECT DISTINCT pch.month, pch.day_of_month, pch.day_of_year, tillage_type FROM comet.planner_cropland_tillage pch JOIN comet.planner_cropland_crops pc ON pch.id_planner_cropland_crops = pc.id WHERE pch.id_planner_cropland_crops = " + str( id_planner_cropland_crops2 ) + " AND pc.sequence = 'wintercrop' ORDER BY day_of_year;"
                                #print "\n      ...sql = " + sql + "\n"
                                cursor_tillages = mariadb_connection.cursor()
                                cursor_tillages.execute( sql )

                                for( month, day_of_month, day_of_year, tillage_type ) in cursor_tillages:

                                    fileWriteString = fileWriteString + tab6 + "<TillageEvent>\n" 
                                    fileWriteString = fileWriteString + tab7 + "<TillageDate>" + tillage2_date_str + "</TillageDate>\n" 
                                    fileWriteString = fileWriteString + tab7 + "<TillageType>" + tillage_type + "</TillageType>\n" 
                                    fileWriteString = fileWriteString + tab6 + "</TillageEvent>\n" 

                                cursor_tillages.close()

                                fileWriteString = fileWriteString + tab5 + "</TillageList>\n" 

                                #*** N Fertilization
                                fileWriteString = fileWriteString + tab5 + "<NApplicationList>\n" 
                                # loop through Nfert events
                                sql = "SELECT DISTINCT pch.month, pch.day_of_month, pch.day_of_year, pch.nfert_type, pch.nfert_amount, pch.nfert_application_method, pch.nfert_eep FROM comet.planner_cropland_nfert pch JOIN comet.planner_cropland_crops pc ON pch.id_planner_cropland_crops = pc.id WHERE pch.id_planner_cropland_crops = " + str( id_planner_cropland_crops2 ) + " AND pc.sequence = 'wintercrop' ORDER BY day_of_year;"
                                #print "\n      ...sql = " + sql + "\n"
                                cursor_nfert = mariadb_connection.cursor()
                                cursor_nfert.execute( sql )

                                for( month, day_of_month, day_of_year, nfert_type, nfert_amount, nfert_application_method, nfert_eep ) in cursor_nfert:

                                    nfert_amount_temp = nfert_amount
                                    #lower the N rate according to plot defined 
                                    if( practice.lower().find( 'compost' ) > -1 or practice.lower().find( 'manure' ) > -1 ):
                                        if( year == 2018 ): nfert_amount_temp = nfert_amount * ( 1 - 0.10 )
                                        if( year == 2019 ): nfert_amount_temp = nfert_amount * ( 1 - 0.15 )
                                        if( year == 2020 ): nfert_amount_temp = nfert_amount * ( 1 - 0.175 )
                                        if( year == 2021 ): nfert_amount_temp = nfert_amount * ( 1 - 0.1875 )
                                        if( year == 2022 ): nfert_amount_temp = nfert_amount * ( 1 - 0.19375 )
                                        if( year == 2023 ): nfert_amount_temp = nfert_amount * 0.8
                                        if( year == 2024 ): nfert_amount_temp = nfert_amount * 0.8
                                        if( year == 2025 ): nfert_amount_temp = nfert_amount * 0.8
                                        if( year == 2026 ): nfert_amount_temp = nfert_amount * 0.8
                                        if( year == 2027 ): nfert_amount_temp = nfert_amount * 0.8

                                    fileWriteString = fileWriteString + tab6 + "<NApplicationEvent>\n" 
                                    fileWriteString = fileWriteString + tab7 + "<NApplicationDate>" + nfert2_date_str + "</NApplicationDate>\n" 
                                    fileWriteString = fileWriteString + tab7 + "<NApplicationType>" + nfert_type + "</NApplicationType>\n" 
                                    fileWriteString = fileWriteString + tab7 + "<NApplicationAmount>" + str( nfert_amount_temp ) + "</NApplicationAmount>\n" 
                                    fileWriteString = fileWriteString + tab7 + "<NApplicationMethod>" + nfert_application_method + "</NApplicationMethod>\n" 
                                    #fileWriteString = fileWriteString + tab7 + "<EEP>" + nfert_eep + "</EEP>\n" 
                                    #No EEP products are being used 
                                    fileWriteString = fileWriteString + tab7 + "<EEP>" + nfert_eep + "</EEP>\n" 
                                    fileWriteString = fileWriteString + tab6 + "</NApplicationEvent>\n" 

                                cursor_nfert.close()

                                fileWriteString = fileWriteString + tab5 + "</NApplicationList>\n" 

                                #*** Manure/Compost
                                fileWriteString = fileWriteString + tab5 + "<OMADApplicationList>\n" 
                                # loop through OMAD events
                                sql = "SELECT DISTINCT pch.month, pch.day_of_month, pch.day_of_year, pch.omad_type, pch.omad_amount, pch.omad_percent_n, pch.omad_cn_ratio FROM comet.planner_cropland_omad pch JOIN comet.planner_cropland_crops pc ON pch.id_planner_cropland_crops = pc.id WHERE pc.cdl_name not like '%rice%' AND pch.id_planner_cropland_crops = " + str( id_planner_cropland_crops2 ) + " AND pc.sequence = 'wintercrop' ORDER BY day_of_year;"
                                #print "\n      ...sql = " + sql + "\n"
                                cursor_omad = mariadb_connection.cursor()
                                cursor_omad.execute( sql )

                                for( month, day_of_month, day_of_year, omad_type, omad_amount, omad_percent_n, omad_cn_ratio ) in cursor_omad:

                                    fileWriteString = fileWriteString + tab6 + "<OMADApplicationEvent>\n" 
                                    fileWriteString = fileWriteString + tab7 + "<OMADApplicationDate>" + omad2_date_str + "</OMADApplicationDate>\n" 
                                    fileWriteString = fileWriteString + tab7 + "<OMADType>" + omad_type + "</OMADType>\n" 
                                    fileWriteString = fileWriteString + tab7 + "<OMADAmount>" + str( omad_amount ) + "</OMADAmount>\n" 
                                    fileWriteString = fileWriteString + tab7 + "<OMADPercentN>" + str( omad_percent_n ) + "</OMADPercentN>\n" 
                                    fileWriteString = fileWriteString + tab7 + "<OMADCNRatio>" + str( omad_cn_ratio ) + "</OMADCNRatio>\n" 
                                    fileWriteString = fileWriteString + tab6 + "</OMADApplicationEvent>\n" 

                                cursor_omad.close()

                                fileWriteString = fileWriteString + tab5 + "</OMADApplicationList>\n" 

                                #*** Irrigation
                                fileWriteString = fileWriteString + tab5 + "<IrrigationList>\n" 

                                if( irrigated == 'Y' ):
                                # loop through Irrigation events
                                    sql = "SELECT DISTINCT pch.month, pch.day_of_month, pch.day_of_year, pch.irrig_amount FROM comet.planner_cropland_irrig pch JOIN comet.planner_cropland_crops pc ON pch.id_planner_cropland_crops = pc.id WHERE pch.id_planner_cropland_crops = " + str( id_planner_cropland_crops2 ) + " AND ( pc.sequence = 'wintercrop' OR pc.cdl_name in ( 'winter wheat', 'winter oats', 'winter barley' ) ) ORDER BY day_of_year;"
                                    #print "\n      ...sql = " + sql + "\n"
                                    cursor_irrigation = mariadb_connection.cursor()
                                    cursor_irrigation.execute( sql )

                                    for( month, day_of_month, day_of_year, irrig_amount ) in cursor_irrigation:

                                        if( int( month ) == 2 and int( day_of_month ) == 29 ):
                                            day_of_month = 28

                                        month_str = str( month )
                                        day_of_month_str = str( day_of_month )

                                        if len( str( month ) ) == 1 : month_str = "0" + str( month ) 
                                        if len( str( day_of_month ) ) == 1: day_of_month_str = "0" + str( day_of_month ) 

                                        date_str = month_str + "/" + day_of_month_str + "/" + year_str

                                        fileWriteString = fileWriteString + tab6 + "<IrrigationEvent>\n" 
                                        fileWriteString = fileWriteString + tab7 + "<IrrigationDate>" + date_str + "</IrrigationDate>\n" 
                                        fileWriteString = fileWriteString + tab7 + "<IrrigationInches>" + str( irrig_amount ) + "</IrrigationInches>\n" 
                                        fileWriteString = fileWriteString + tab6 + "</IrrigationEvent>\n" 

                                    cursor_irrigation.close()

                                fileWriteString = fileWriteString + tab5 + "</IrrigationList>\n" 

                                fileWriteString = fileWriteString + tab4 + "</Crop>\n" 
                                    
                            #*****************************************************************************************************
                            #******** 2nd "crop" following day of year 288 end of 1st crop in grassland reserve system ***********
                            #*****************************************************************************************************

                            if( practice.lower().find( 'reserve' ) > -1 and current_or_future_management == 'future' ):
                            
                                if( practice.lower().find( 'non-legume' ) > -1 ):
                                    grassland_reserve_crop = 'Grass'
                                else:
                                    grassland_reserve_crop = 'Grass-Legume Mix'

                                fileWriteString = fileWriteString + tab4 + "<Crop CropNumber=\"2\">\n" 
                                fileWriteString = fileWriteString + tab5 + "<CropName>" + grassland_reserve_crop + "</CropName>\n" 

                                fileWriteString = fileWriteString + tab5 + "<PlantingDate>10/20/" + year_str + "</PlantingDate>\n" 
                                fileWriteString = fileWriteString + tab5 + "<ContinueFromPreviousYear>Y</ContinueFromPreviousYear>\n" 

                                #***Harvests
                                fileWriteString = fileWriteString + tab5 + "<HarvestList>\n" 
                                fileWriteString = fileWriteString + tab5 + "</HarvestList>\n" 

                                #***Grazing
                                fileWriteString = fileWriteString + tab5 + "<GrazingList>\n" 
                                fileWriteString = fileWriteString + tab5 + "</GrazingList>\n" 

                                #*** Tillage
                                fileWriteString = fileWriteString + tab5 + "<TillageList>\n" 
                                fileWriteString = fileWriteString + tab5 + "</TillageList>\n" 

                                #*** N Fertilization
                                fileWriteString = fileWriteString + tab5 + "<NApplicationList>\n" 
                                fileWriteString = fileWriteString + tab5 + "</NApplicationList>\n" 

                                #*** Manure/Compost
                                fileWriteString = fileWriteString + tab5 + "<OMADApplicationList>\n" 
                                fileWriteString = fileWriteString + tab5 + "</OMADApplicationList>\n" 

                                #*** Irrigation
                                fileWriteString = fileWriteString + tab5 + "<IrrigationList>\n" 
                                fileWriteString = fileWriteString + tab5 + "</IrrigationList>\n" 

                                fileWriteString = fileWriteString + tab4 + "</Crop>\n" 
                                    
                                # begin a perennial crop in the fall that will be harvested in the following year
                                if( winter_crop == '' and \
                                next_summer_crop_class == "perennial" and \
                                next_summer_crop != summer_cropList[x] ):
                                
                                    if( practice.lower().find( 'reserve' ) == -1 or \
                                        ( practice.lower().find( 'reserve' ) > -1 and current_or_future_management == 'current' ) ):

                                        fileWriteString = fileWriteString + tab4 + "<Crop CropNumber=\"2\">\n" 
                                        fileWriteString = fileWriteString + tab5 + "<CropName>" + next_cfarm_cropname + "</CropName>\n" 

                                        # set the planting date
                                        d = datetime.strptime( summer_crop_harvest_date_str, '%m/%d/%Y' )
                                        d = d + timedelta( days = 3 )
                                        newcrop_plant_date_str = d.strftime( '%m/%d/%Y' )

                                        fileWriteString = fileWriteString + tab5 + "<PlantingDate>" + newcrop_plant_date_str + "</PlantingDate>\n" 
                                        fileWriteString = fileWriteString + tab5 + "<ContinueFromPreviousYear>N</ContinueFromPreviousYear>\n" 

                                        #***Harvests
                                        fileWriteString = fileWriteString + tab5 + "<HarvestList>\n" 
                                        fileWriteString = fileWriteString + tab5 + "</HarvestList>\n" 

                                        #***Grazing
                                        fileWriteString = fileWriteString + tab5 + "<GrazingList>\n" 
                                        fileWriteString = fileWriteString + tab5 + "</GrazingList>\n" 

                                        #*** Tillage
                                        fileWriteString = fileWriteString + tab5 + "<TillageList>\n" 
                                        fileWriteString = fileWriteString + tab5 + "</TillageList>\n" 

                                        #*** N Fertilization
                                        fileWriteString = fileWriteString + tab5 + "<NApplicationList>\n" 
                                        fileWriteString = fileWriteString + tab5 + "</NApplicationList>\n" 

                                        #*** Manure/Compost
                                        fileWriteString = fileWriteString + tab5 + "<OMADApplicationList>\n" 
                                        fileWriteString = fileWriteString + tab5 + "</OMADApplicationList>\n" 

                                        #*** Irrigation
                                        fileWriteString = fileWriteString + tab5 + "<IrrigationList>\n" 
                                        fileWriteString = fileWriteString + tab5 + "</IrrigationList>\n" 

                                        fileWriteString = fileWriteString + tab4 + "</Crop>\n" 
                            
                            previous_winter_crop = winter_crop
                            previous_winter_crop_class = winter_crop_class
                            
                            fileWriteString = fileWriteString + tab3 + "</CropYear>\n" 

                            previous_crop = cropname1

                        fileWriteString = fileWriteString + tab2 + "</CropScenario>\n" 

                    #write to close the Agro and Day XML classes
                    fileWriteString = fileWriteString + "\t</Cropland>\n" 
                    
                    f.write( fileWriteString )
            
                print "      ...id_mcfc points used = " + str( id_mcfc_string )

            #end of file write loop
            f.write( "</Day>\n" )

        f.close()
        print "********************************************************"
        print "Finished writing to file " + str( input_xml_file )

        #create zipfile
        print "Writing zipfile " + str( zipfile_name )
        compression = zipfile.ZIP_DEFLATED
        zf = zipfile.ZipFile( zipfile_name, mode='a' )
        zf.write( input_xml_file, compress_type = compression )
        zf.close()
        print "********************************************************\n"

cursor_practices.close()
cursor_points.close()

mariadb_connection.close()
    
print "     ----------------------------------------------------------------------"
print ""
end = datetime.now( )
print "ending script at " + str( end )
elapsed = end-start
print "elapsed time = " + str( elapsed )
print ""

