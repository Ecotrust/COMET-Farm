# import system modules
from datetime import datetime
import os, sys, csv, time, string
import xml.etree.ElementTree as ET
# import ipdb

'''
Running the script
Windows
    py -3 ./scripts/xml2csv.py <XML COMET-Farm API Output Result>.xml
        <XML COMET-Farm Output> system location of XML output file from COMET-Farm
            e.g., /usr/local/name/comet/baseline.xml
'''

'''
    Overview of script
    ==================

    This script takes as an argument a XML file from a COMET-Farm result email,
    then checks if a csv file for crop in results exists, if not creates a csv file for crop,
    then outputs rows for each mapunit in results file
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
            ...

'''

# Most results contain duplicate for first year
def remove_duplicate_years(arr=[]):
    years = [dic["year"] for dic in arr]
    dup_year = ''
    for year in years:
        if years.count(year) > 1:
            # only remove if dup year present
            dup_year = year
    if len(dup_year) > 0:
        for i in arr:
            if dup_year == i.get('year'):
                el = arr.pop(arr.index(i))
    return arr

def calc_greenhouse_gas_balance(*args):
    ghg_balance = 0
    for arg in args:
        if arg:
            ghg_balance += arg
    return ghg_balance

def calc_co2_exchange(arr=[{"output": 0, "year": ""}]):
    # Units are grams of soil carbon per meter squared
    # one hectare (ha) is 100 meters squared
    # arr = remove_duplicate_years(arr) # Most results contain duplicate for first year
    arr_len = len(arr) - 1 # make sure there is at least 1 year(s) available to measure
    if arr_len > 0:
        area = map_unit_area(arr) # get mapunit area for calc
        if arr[0]["output"] != 'None' and arr[arr_len]["output"] != 'None' and area != 'None':
            # HA is actually report in m2
            calc = ((float(arr[0]["output"]) - float(arr[arr_len]["output"])) / arr_len) * (float(area)) * (1/1000000) * (44/12) # see equation at top of doc
            # import ipdb; ipdb.set_trace()
            return calc

def calc_direct_soil_n2o(arr=[{"output": 0, "year": ""}]):
    # n2oflux seems to have 1 less year output than somsc
    year_count = len(arr)
    n2o_avg = 0
    for y in range( year_count ):
        n2o_avg += float(arr[y]['n2oflux'])
    if n2o_avg > 0:
        area = map_unit_area(arr) # get mapunit area for calc
        n2o_avg = n2o_avg/year_count
        calc = n2o_avg * (44/28) * 298 * float(area) * (1/1000000)
        return calc

def calc_volatilized_indirect_soil_n2o(arr=[{"output": 0, "year": ""}]):
    # n2oflux seems to have 1 less year output than somsc
    year_count = len(arr)
    n2o_avg = 0
    for y in range( year_count ):
        n2o_avg += float(arr[y]['volpac'])
    if n2o_avg >= 0:
        area = map_unit_area(arr)
        n2o_avg = n2o_avg/year_count
        calc = n2o_avg * 0.0075 * (44/28) * 298 * float(area) * (1/1000000)
        return calc

def calc_leached_indirect_soil_n2o(arr=[{"output": 0, "year": ""}]):
    # n2oflux seems to have 1 less year output than somsc
    year_count = len(arr)
    n2o_avg = 0
    for y in range( year_count ):
        n2o_avg += float(arr[y]['strmac_2_'])
    if n2o_avg > 0:
        area = map_unit_area(arr)
        n2o_avg = n2o_avg/year_count
        calc = n2o_avg * 0.01 * (44/28) * 298 * float(area) * (1/1000000)
        return calc

def calc_indirect_soil_n2o(arr=[{"output": 0, "year": ""}]):
    # n2oflux seems to have 1 less year output than somsc
    year_count = len(arr)
    n2o_avg = 0
    for y in range( year_count ):
        n2o_avg += float(arr[y]['n2oflux'])
    if n2o_avg > 0:
        area = map_unit_area(arr)
        n2o_avg = n2o_avg/year_count
        calc = n2o_avg * (44/28) * 298 * float(area) * (1/1000000)
        return calc

def map_unit_area(arr=[]):
    # area should be same for each dict in list
    # so we only need the first
    return arr[0]['area']

def write_parsed_mapunits(map_units):
    script_path = os.path.dirname(os.path.realpath(__file__))
    results_file_name = ''
    results_dir_name = script_path + '/../results/'

    if not os.path.isdir(results_dir_name):
        os.mkdir(results_dir_name)

    parsed_mapunit_fieldnames = ['mapunit_id', 'acres']

    # get params to use for results file name
    for map_unit in map_units:
        for k,v in map_unit.items():
            if k not in parsed_mapunit_fieldnames:
                parsed_mapunit_fieldnames.insert(0, k)
            if k == 'crop':
                c_name = str(v).lower()
            if k == 'iso_id':
                iso_name = str(v).lower()
            if k == 'crop_id':
                c_id = str(v).lower()
    results_file_name = c_name + '_' + c_id + '_' + iso_name

    with open(results_dir_name + results_file_name + '.csv', 'w', newline='') as resultsFile:
        writer = csv.DictWriter(resultsFile, fieldnames=parsed_mapunit_fieldnames)
        writer.writeheader()
        for map_unit in map_units:
            writer.writerow(map_unit)

    resultsFile.close()

def get_acres_from_m2(meters):
    meters = float(meters)
    if meters > 0:
        acres = meters * 0.0002471054
    else:
        acres = 0
    return acres

def parse_mapunit(elem, mapunit_id, field_size, scenario, xml_file_name):

    # model_run_data = {}

    for child in elem.iter():
        xml_tag = str(child.tag)
        xml_tag = xml_tag.lower()
        xml_text = str(child.text)

        # if (xml_tag in ( 'aagdefac', 'abgdefac', 'accrst', 'accrste_1_', 'agcprd', 'aglivc', 'bgdefac', 'bglivcm', 'rain', 'cgrain', 'cinput', 'crmvst', 'crootc', 'crpval', 'egracc_1_', 'eupacc_1_', 'fbrchc', 'fertac_1_', 'fertot_1_1_', 'frootcm', 'gromin_1_', 'irrtot', 'metabc_1_', 'metabc_2_', 'metabe_1_1_', 'metabe_2_1_', 'nfixac', 'omadac', 'omadae_1_', 'petann', 'rlwodc', 'somsc', 'somse_1_', 'stdedc', 'stdede_1_', 'strmac_1_', 'strmac_2_', 'strmac_6_', 'strucc_1_', 'struce_1_1_', 'struce_2_1_', 'tminrl_1_', 'tnetmn_1_', 'volpac',  ) ):

        # if ( xml_tag in ('somsc', 'strmac_2_', 'volpac') ) :

            # values = write_end_of_year_daycent_output( xml_tag, xml_text, scenario, mapunit_id, field_size )
            # for value in values:
            #     if xml_tag not in model_run_data.keys():
            #         model_run_data[xml_tag] = []
            #     model_run_data[xml_tag].append(value)
            #
            # if xml_tag == 'somsc':
            #     somsc = model_run_data[xml_tag]
            #     calc_value = calc_co2_exchange(somsc)
            #     calc_tag = 'soil_carbon_exchange'
            #     if calc_tag not in model_run_data.keys():
            #         # model_run_data[calc_tag] = []
            #         model_run_data[calc_tag] = calc_value
            #
            # elif xml_tag == 'strmac_2_':
            #     strmac_2_ = model_run_data[xml_tag]
            #     calc_value = calc_leached_indirect_soil_n2o(strmac_2_)
            #     calc_tag = 'indirect_soil_n2o_leached'
            #     if calc_tag not in model_run_data.keys():
            #         # model_run_data[calc_tag] = []
            #         model_run_data[calc_tag] = calc_value
            #
            # elif xml_tag == 'volpac':
            #     volpac = model_run_data[xml_tag]
            #     calc_value = calc_volatilized_indirect_soil_n2o(volpac)
            #     calc_tag = 'indirect_soil_n2o_volatilized'
            #     if calc_tag not in model_run_data.keys():
            #         # model_run_data[calc_tag] = []
            #         model_run_data[calc_tag] = calc_value

        # elif( xml_tag in ( 'irrigated', 'inputcrop' ) ):
        # elif( xml_tag in ( 'inputcrop' ) ):
            # inputcrop_data = xml_text.split(',')
            # Crop comes in as year,crop repeating.
            # crop_tag = 'crop'
            # crop_value = inputcrop_data[1]

        # elif( xml_tag in ('noflux', 'n2oflux', 'annppt') ):
        # elif( xml_tag in ('n2oflux') ):

            # values = write_yearly_daycent_output92( xml_tag, xml_text, scenario, mapunit_id, field_size )
            # for value in values:
                # if xml_tag not in model_run_data.keys():
                    # model_run_data[xml_tag] = []
                # model_run_data[xml_tag].append(value)

            # if xml_tag == 'n2oflux':
                # n2oflux = model_run_data[xml_tag]
                # if n2oflux:
                    # calc_value = calc_direct_soil_n2o(n2oflux)
                # calc_tag = 'direct_soil_n2o'
                # if calc_tag not in model_run_data.keys():
                    # model_run_data[calc_tag] = calc_value
        if (xml_tag in ('soilcarbon', 'soiln2o')):
            print(xml_tag)
        else:
            continue

    # ghg_balance = calc_greenhouse_gas_balance(model_run_data['soil_carbon_exchange'][0]['output'], model_run_data['direct_soil_n2o'][0]['output'], model_run_data['indirect_soil_n2o_leached'][0]['output'], model_run_data['indirect_soil_n2o_volatilized'][0]['output'])
    # import ipdb; ipdb.set_trace()
    # add together for greenhouse gas balance total
    # ghg_balance = calc_greenhouse_gas_balance(model_run_data['soil_carbon_exchange'], model_run_data['direct_soil_n2o'], model_run_data['indirect_soil_n2o_leached'], model_run_data['indirect_soil_n2o_volatilized'])

    # get crop id and iso id from file name
    # assumes input file was named 'cf_<crop_id>_<iso_id>'

    # --- will need ---
    # xml_file_name = xml_file_name.split('_')
    # if len(xml_file_name) > 1:
    #     crop_id = xml_file_name[-2]
    #     iso_id = xml_file_name[-1]
    #     iso_id = iso_id.split('.')[0] # split off the .xml from iso_id.xml
    # else:
    #     crop_id = 'not provided'
    #     iso_id = 'not provided'

    # acres = get_acres_from_m2(field_size)

    # scenario_emissions_key = scenario + ' ' + 'net emissions'
    # scenario_scse_key = scenario + ' ' + 'soil carbon exchange'
    # scenario_d_n2o_key = scenario + ' ' + 'direct soil n2o'
    # scenario_ind_n2o_l_key = scenario + ' ' + 'indirect soil n2o leached'
    # scenario_ind_n2o_v_key = scenario + ' ' + 'indirect soil n2o volatilized'

    mapunit_row_data = {
        # 'mapunit_id': mapunit_id,
        # crop_tag: crop_value,
        # scenario_emissions_key: ghg_balance,
        # scenario_scse_key: model_run_data['soil_carbon_exchange'],
        # scenario_d_n2o_key: model_run_data['direct_soil_n2o'],
        # scenario_ind_n2o_l_key: model_run_data['indirect_soil_n2o_leached'],
        # scenario_ind_n2o_v_key: model_run_data['indirect_soil_n2o_volatilized'],
        # 'acres': acres,
        # 'iso_id': iso_id,
        # 'crop_id': crop_id,
    }

    # import ipdb; ipdb.set_trace()

    return mapunit_row_data

    #  header fields
    # values_array = ['year', 'scenario', 'id', 'area']
    #
    # for values in model_run_data:
    #     values_array.append(values)

    # # write parsed out to csv
    # csv_file_name = scenario
    # dir_name = './results/' + mapunit_id + '/'
    #
    # if not os.path.isdir(dir_name):
    #     os.mkdir(dir_name)
    #
    # with open(dir_name + csv_file_name + '.csv', 'wt') as csvFile:
    #     writer = csv.DictWriter(csvFile, fieldnames=values_array)
    #     writer.writeheader()
    #
    #     if model_run_data:
    #         org_by_year = organize_by_year(model_run_data)
    #         for k,v in org_by_year.items():
    #             writer.writerow(v)
    # csvFile.close()


# Extract yearly output data from the DayCent variable for end-of-year value
# This function is used for API data with whole numbers representing the yearly output data
# def write_yearly_daycent_output( daycent_variable, arrayText, scenario, mapunit, area ):
#
#     if arrayText.endswith(','):
#         arrayText = arrayText[:-1]
#
#     arrayText = arrayText.replace( ':', ',' )
#     array1 = arrayText.split(',')
#     array1Length = len( array1 )
#     daycent_variable = str(daycent_variable).lower()
#     values = []
#
#     for y in range( 0, (array1Length // 2) ):
#         year_value = str( array1[ y * 2 ] )
#         output_value = str( array1[ int(( y * 2 ) + 1) ] )
#         yearly_output = {
#             "year": year_value,
#             "var": daycent_variable,
#             "output": output_value,
#             daycent_variable: output_value,
#             "id": mapunit,
#             "area": area,
#             "scenario": scenario,
#         }
#         values.append(yearly_output)
#
#     return values

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

    arrayText = arrayText.replace( ':', ',' )
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

def calc_delta_per_scenario(mapunit_results):
    print('\n', mapunit_results)
    # delta_per_scenario = mapunit_results['']


def parse_data_rows(parsed_mapunits):
    combined_results = {}
    for u in parsed_mapunits:
        unit_id = u['mapunit_id']
        if unit_id not in combined_results.keys():
            combined_results[unit_id] = {}

        for k,v in u.items():
            combined_results[u['mapunit_id']][k] = v

    # calc delta scenario v baseline
    for mapunit in combined_results.values():
        # print(mapunit)
        dict_net_emissions = dict(filter(lambda item: 'net emissions' in item[0], mapunit.items())) # get dict of items with k containing 'net emissions'
        for scenario_net in dict_net_emissions.items():
            # calc tonnes per acre
            v_tonnes_per_acre = (((float(scenario_net[1]) / (float(mapunit['acres']) * 100)) * 100) / 1000000)
            k_tonnes_per_acre = 'tonnes per acre - ' + str(scenario_net[0])
            mapunit.update({ str(k_tonnes_per_acre) : v_tonnes_per_acre })

        baseline_net = dict_net_emissions.pop('Baseline net emissions') # get baseline value and remove it from other scenarios
        for scenario_net in dict_net_emissions.items():
            # calculate change from baseline in net emissions
            scenario_delta_baseline = float(scenario_net[1]) - float(baseline_net)
            k_val = 'delta - ' + str(scenario_net[0])
            mapunit.update({ str(k_val) : str(scenario_delta_baseline) })

            # calc change in tonnes per acre from baseline in net emissions
                # note: this script has previously converted area from square meters to acres
            delta_per_acre = (((float(scenario_delta_baseline) / (float(mapunit['acres']) * 100)) * 100) / 1000000)
            k_val_acre = 'delta per acre - ' + str(scenario_net[0])
            mapunit.update({ str(k_val_acre) : str(delta_per_acre) })


    data_rows = []
    for res in combined_results.values():
        data_rows.append(res)

    return data_rows

def parse_aggregate(elem, scenario, model_run_name):

    aggregate_data = {}
    scenario_name = scenario.lower()

    # Add the field id which is the same as model run name
    aggregate_data['fid'] = model_run_name

    for child in elem.iter():
        xml_tag = str(child.tag)
        xml_tag = xml_tag.lower()
        xml_text = str(child.text)

        if (xml_tag == 'scenario'):
            aggregate_data['scenario'] = scenario_name
        elif (xml_tag in ('soilcarbon', 'soiln2o')):
            aggregate_data[xml_tag] = xml_text

    return aggregate_data

def write_aggregate_csv(all_agg, xml_name):
    script_path = os.path.dirname(os.path.realpath(__file__))
    results_file_name = ''
    results_dir_name = script_path + '/../results/'

    if not os.path.isdir(results_dir_name):
        os.mkdir(results_dir_name)

    aggregate_data_fieldnames = []

    xml_file_name = xml_name.split('_')
    if len(xml_file_name) > 1:
        crop_id = xml_file_name[-2]
        iso_id = xml_file_name[-1]
        iso_id = iso_id.split('.')[0] # split off the .xml from iso_id.xml
    else:
        crop_id = 'not provided'
        iso_id = 'not provided'

    results_file_name =  crop_id + '_' + iso_id

    for r in all_agg:
        for k,v in r.items():
            if k not in aggregate_data_fieldnames:
                aggregate_data_fieldnames.append(k)


    with open(results_dir_name + results_file_name + '.csv', 'wt') as csvFile:
        writer = csv.DictWriter(csvFile, fieldnames=aggregate_data_fieldnames)
        writer.writeheader()
        for r in all_agg:
            writer.writerow(r)

    csvFile.close()

def main():
    # check if argument has been given for xml
    if len(sys.argv) < 1:
        print("\nMissing argument")
        print("\n")
        print("expecting 1 argument")
        print("> Results XML file")
        print("\n")
        print("expected command (windows sub `python3` with `py -3`)")
        print("`python3 xml2csv.py <XML COMET-Farm Output>.xml`")
        print("     <XML COMET-Farm Output> system location of XML output file from COMET-Farm")
        print("         e.g., /usr/local/name/comet/Results[...].xml\n")
        print("\n")
        exit()

    xml_name = sys.argv[1]

    start = datetime.now()
    print("\nStarting script at " + str( time.ctime( int( time.time( ) ) ) ) + "\n")
    print("----------------------------------------------------------------------")

    # var to store each mapunits data
    parsed_mapunits = []
    parsed_agg = []
    # open the file passed as an argument
    xml_file = open(xml_name, 'r+')

    # XML Parse
    tree = ET.parse(xml_name)
    root = tree.getroot()

    for elem in tree.iter():
        xmlTag = str( elem.tag )
        xmlAttrib = str( elem.attrib )
        xmlAttribName = str( elem.attrib.get( 'name' ) )
        xmlAttribId = str( elem.attrib.get( 'id' ) )
        xmlAttribArea = str( elem.attrib.get( 'area' ) )
        xmlText = str( elem.text )

        # Model run parameters that we do not want/need to process
        if ( xmlTag in ( 'Day', 'Cropland', 'Carbon', 'CO2', 'N2O', 'CH4', 'BiomassBurningCarbonUncertainty', 'BiomassBurningCH4Uncertainty', 'BiomassBurningN2OUncertainty', 'C02', 'DrainedOrganicSoilsCO2Uncertainty', 'DrainedOrganicSoilsN2OUncertainty', 'LimingCO2Uncertainty', 'SoilCarbonUncertainty', 'SoilCH4Uncertainty', 'SoilN2OUncertainty', 'UreaFertilizationCO2Uncertainty', 'WetlandRiceCultivationCH4Uncertainty', 'WetlandRiceCultivationN2OUncertainty', 'AFDownedDeadWood', 'AFDownedDeadWoodUncertainty', 'AFForestFloor', 'AFForestFloorUncertainty', 'AFLiveTrees', 'AFLiveTreesUncertainty', 'AFStandingDeadTrees', 'AFStandingDeadTreesUncertainty', 'AFUnderstory', 'AFUnderstoryUncertainty', 'Agroforestry', 'Animal', 'FORDownedDeadWood', 'FORDownedDeadWoodUncertainty', 'Forestry', 'FORForestFloorUncertainty', 'FORInLandfills', 'FORInLandfillsUncertainty', 'FORLiveTrees', 'FORLiveTreesUncertainty', 'FORProductsInUse', 'FORProductsInUseUncertainty', 'FORSoilOrganicCarbon', 'FORSoilOrganicCarbonUncertainty', 'FORStandingDeadTreesUncertainty', 'FORUnderstory', 'FORUnderstoryUncertainty' ) ):

            continue

        if ( xmlTag == 'ModelRun' ):
            # get the model run name
            modelRunName = xmlAttribName

        elif( "from reduced" in modelRunName ):
            # continue the loop but don't model this practice with the different baseline scenario
            continue

        # ====== Scenario
        elif( xmlTag == 'Scenario' ):

            # get the sceanrio name and store for later
            scenarioFullName = xmlAttribName
            scenario = xmlAttribName

            aggregate_data = {}
            scenario_name = scenario.lower()

            ### check if this is the raw data from datacent
            if scenarioFullName.find( ' : FILE RESULTS' ) > -1:
                # generate the scenario name
                # used later for DayCent data within mapunit
                scenario = xmlAttribName[:-15]
            ### else it scenario data from comet farm calculations
            else:
                # get a list of fields already in parsed_agg list
                field_ids = [dic["fid"] for dic in parsed_agg]

                # if field already has data append to it
                if modelRunName in field_ids:
                    for s in parsed_agg:
                        if s['fid'] == modelRunName:
                            for child in elem.iter():
                                xml_tag = str(child.tag)
                                xml_tag = xml_tag.lower()
                                xml_text = str(child.text)

                                # add value for scenario
                                if xml_tag == 'soilcarbon':
                                    s['scen1C'] = xml_text
                                elif xml_tag == 'soiln2o':
                                    s['scen1N'] = xml_text

                else:
                    aggregate_data['fid'] = modelRunName
                    aggregate_data['area'] = 0

                    for child in elem.iter():
                        xml_tag = str(child.tag)
                        xml_tag = xml_tag.lower()
                        xml_text = str(child.text)

                        # add value for scenario
                        if xml_tag == 'soilcarbon':
                            aggregate_data['baseC'] = xml_text
                        elif xml_tag == 'soiln2o':
                            aggregate_data['baseN'] = xml_text

                    aggregate_data['scen1C'] = ''
                    aggregate_data['scen1N'] = ''

                    parsed_agg.append(aggregate_data)

        elif( "current" in scenario.lower() ):
            # will be the same as baseline so no need to duplicate
            continue

        elif( xmlTag == "MapUnit" ):

            mapunit = xmlAttribId
            field_size = xmlAttribArea

            for s in parsed_agg:
                if s['fid'] == modelRunName:
                    if 'area' in s.keys():
                        area_float = float(s['area'])
                        area_float += float(field_size)
                        s['area'] = str(area_float)
                    else:
                        s['area'] = field_size

            # print(parsed_agg[scenario])
            # if parsed_agg[scenario]
            # parsed_mapunits['area'] = field_size
            # parsed_mapunit = parse_mapunit(elem, mapunit, field_size, scenario, xml_name)
            # parsed_mapunits.append(parsed_mapunit)

            # give a status update for scipt user
            print("creating records for scenario = [" + str(scenario) + "] and mapunit = [" + str( mapunit ) + "]")

        else:
            continue

    write_aggregate_csv(parsed_agg, xml_name)
    # close the XML input file
    xml_file.close()

    # data_rows = parse_data_rows(parsed_mapunits)

    # write_aggregate_csv()
    # write_parsed_mapunits(data_rows)

    print("----------------------------------------------------------------------")
    End = datetime.now( )
    print("Ending script at " + str( time.ctime( int( time.time( ) ) ) ))
    elapsed = End-start
    print("elapsed time = " + str( elapsed ))

main()
