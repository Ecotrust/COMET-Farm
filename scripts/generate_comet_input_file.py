# import system modules
import os, sys, time

# import functions for extracting data from excel
from openpyxl import load_workbook

# check if argument for workbook has been given
if len(sys.argv) < 1:
    print("\n")
    print("python3 script generate_comet_input_file.py <spreadsheet location>")
    print("\n")
    # print("Command-line arguments are as follows:")
    # print("  <spreadsheet locatiion> system location of spreadsheet with input data")
    # print("    eg /usr/local/name/comet/data.xml")
    # print("")
    exit()

wb_dir = sys.argv[1]
wb = load_workbook(filename = wb_dir)
processed_fields_sheet = wb['processed']
processed_sheets = {}
for row in range(1, processed_fields_sheet.max_row + 1):
    sheet_name = processed_fields_sheet['B' + str(row)].value

    scenario_sheet = wb[sheet_name]

    current_values = {}
    # Current practices - years 2000 - 2019
    current_yearly = []
    # Scenario a practices - future years 2020 - 2029
    scenario_yearly = []
    # Scenario b practices - future years 2020 - 2029
    scenario_b_yearly = []

    # loop through scenario values
    for row in range(1, scenario_sheet.max_row + 1):
        if row < 14:
            param  = scenario_sheet['A' + str(row)].value
            param_val  = scenario_sheet['B' + str(row)].value
            current_values.setdefault(param, param_val)
        elif row > 16 and row < 37:
            current_year = {}
            for col in range(2, scenario_sheet.max_column):
                year_key = scenario_sheet.cell(row=16, column=col).value
                year_value = scenario_sheet.cell(row=row, column=col).value
                current_year.setdefault(year_key, year_value)
            current_yearly.append(current_year)
        elif row > 39 and row < 50:
            scenario_year = {}
            for col in range(2, scenario_sheet.max_column):
                year_key = scenario_sheet.cell(row=39, column=col).value
                year_value = scenario_sheet.cell(row=row, column=col).value
                scenario_year.setdefault(year_key, year_value)
            scenario_yearly.append(scenario_year)
        elif row > 52 and row < 63:
            scenario_b_year = {}
            for col in range(1, scenario_sheet.max_column):
                year_key = scenario_sheet.cell(row=52, column=col).value
                year_value = scenario_sheet.cell(row=row, column=col).value
                scenario_b_year.setdefault(year_key, year_value)
            scenario_b_yearly.append(scenario_b_year)

    current_values.setdefault('yearly_current_data', current_yearly)
    current_values.setdefault('yearly_scenario_data', scenario_yearly)

    scenario_a_name  = scenario_sheet['B38'].value

    scenario_b_name  = scenario_sheet['B51'].value
    if scenario_b_name:
        current_values.setdefault('yearly_scenariob_data', scenario_b_yearly)
    else:
        current_values.setdefault('yearly_scenariob_data', '')

    # set scenario names
    current_values.setdefault('scenario_a_name', scenario_a_name)
    current_values.setdefault('scenario_b_name', scenario_b_name)

    field_number = sheet_name[6:] # assumes sheet_name is 'ready_field#', removes 'ready_'
    processed_sheets.setdefault(field_number, current_values)

# create XML file
timestamp = time.time()
input_xml_file_name = 'cometfarm_api_input' + str(timestamp)
input_xml_file = input_xml_file_name + '.xml'

if (os.path.isfile(input_xml_file)):
    os.remove(input_xml_file)

# initialize the file content string that will contain the text to be written to the file
with open(input_xml_file, 'w') as f:

    print('Writing XML. This could take a minute...')

    # email_address = list(processed_sheets.items())[0][1]['Email']
    # TODO add ID PNAME and USERID
    # f.write("<CometFarm><Project ID=\"" + "\" PNAME=\"" + "\" USERID=\"" + "\">")
    f.write("<CometFarm>")
    f.write("<Project ID=\"123\" PNAME=\"Test Project\" USERID=\"123\">")

    for field in processed_sheets:
        f.write("<Cropland>")
        # f.write("<GEOM PARCELNAME=\"" + str(processed_sheets[field]['Name']) + "\" SRID=\"" + str(processed_sheets[field]['SRID']) + "\" AREA=\"" + str(processed_sheets[field]['AREA']) + "\">" + processed_sheets[field]['GEOM'] + "</GEOM>")
        f.write("<GEOM PARCELNAME=\"New\" SRID=\"" + str(processed_sheets[field]['SRID']) + "\" AREA=\"" + str(processed_sheets[field]['AREA']) + "\">" + processed_sheets[field]['GEOM'] + "</GEOM>")

        f.write("<Pre-1980>" + processed_sheets[field]['pre_80'] + "</Pre-1980>")
        # CRP always None
        f.write("<CRPStartYear>0</CRPStartYear><CRPEndYear>0</CRPEndYear><CRPType>None</CRPType>")
        # PreCRPManagement fields always empty
        # f.write("<PreCRPManagement></PreCRPManagement><PreCRPTillage></PreCRPTillage><PostCRPManagement></PostCRPManagement><PostCRPTillage></PostCRPTillage>")
        # 1980 - 2000
        f.write("<Year1980-2000>" + processed_sheets[field]['yr80_2000'] + "</Year1980-2000>")
        f.write("<Year1980-2000_Tillage>" + processed_sheets[field]['till80_200'] + "</Year1980-2000_Tillage>")

        # start crop scenario
        f.write("<CropScenario Name=\"Current\">")

        # crop years
        for crop_year in processed_sheets[field]['yearly_current_data']:
            # import ipdb; ipdb.set_trace()
            f.write("<CropYear Year=\"" + str(crop_year['Year']) + "\">")
            f.write("<Crop CropNumber=\"1\">")
            f.write("<CropName>" + str(crop_year['Ccop_name']) + "</CropName>")
            f.write("<CropType>CROPS</CropType>")
            f.write("<PlantingDate>" + str(crop_year['planting_date']).strip('\"') + "</PlantingDate>")
            f.write("<ContinueFromPreviousYear>" + str(crop_year['continue_from_previous_year']) + "</ContinueFromPreviousYear>")
            # f.write("<DidYouPrune></DidYouPrune>") # todo
            # f.write("<RenewOrClearYourOrchard></RenewOrClearYourOrchard>") # todo
            # start harvest list
            f.write("<HarvestList>") # todo should i add conditional
            f.write("<HarvestEvent>") # todo
            f.write("<HarvestDate>" + str(crop_year['harvest_date']).strip('\"') + "</HarvestDate>")
            f.write("<Grain>" + str(crop_year['grain']) + "</Grain>")
            f.write("<yield>" + str(crop_year['yield']) + "</yield>")
            f.write("<StrawStoverHayRemoval>" + str(crop_year['straw_stover_hay_removal']) + "</StrawStoverHayRemoval>")
            f.write("</HarvestEvent>")
            f.write("</HarvestList>")
            # end harvest list
            f.write("<GrazingList />")
            f.write("<TillageList>")
            f.write("<TillageEvent>")
            f.write("<TillageType>" + str(crop_year['tillage_type']) + "</TillageType>")
            f.write("<TillageDate>" + str(crop_year['tillage_date']).strip('\"') + "</TillageDate>")
            f.write("</TillageEvent>")
            f.write("</TillageList>")
            # start fertilizer list
            f.write("<NApplicationList>") # todo should i add conditional
            f.write("<NApplicationEvent>")
            f.write("<NApplicationType>" + str(crop_year['n_application_type']) + "</NApplicationType>")
            f.write("<NApplicationMethod>" + str(crop_year['n_application_method']) + "</NApplicationMethod>")
            f.write("<NApplicationDate>" + str(crop_year['n_application_date']).strip('\"') + "</NApplicationDate>")
            f.write("<NApplicationAmount>" + str(crop_year['n_application_amount']) + "</NApplicationAmount>")
            f.write("<PApplicationAmount>" + "0" + "</PApplicationAmount>")
            f.write("<EEP>" + str(crop_year['eep']) + "</EEP>")
            f.write("</NApplicationEvent>")
            f.write("</NApplicationList>")
            # end fertilizer list
            # start omad application list
            f.write("<OMADApplicationList />")
            # end omad list
            # start irrigation list
            f.write("<IrrigationList />")
            # end irrigation list
            # start liming list
            f.write("<LimingList>")
            f.write("<LimingApplicationEvent>")
            f.write("<LimingApplicationDate></LimingApplicationDate>")
            f.write("<LimingMaterial></LimingMaterial>")
            f.write("<LimingApplicationAmount></LimingApplicationAmount>")
            f.write("</LimingApplicationEvent>")
            f.write("</LimingList>")
            # end liming list
            # start burning list
            # f.write("<BurningEvent>")
            # f.write("<DidYouBurnCropResidue>" + 'No' + "</DidYouBurnCropResidue>")
            # f.write("</BurningEvent>")
            f.write("<BurnEvent>")
            f.write("<BurnTime>No burning</BurnTime>")
            f.write("</BurnEvent>")
            # end burning list
            f.write("</Crop>")
            f.write("</CropYear>")

        f.write("</CropScenario>")

        f.write("<CropScenario Name=\"" + processed_sheets[field]['scenario_a_name'] + "\">")

        for crop_year in processed_sheets[field]['yearly_scenario_data']:
            f.write("<CropYear Year=\"" + str(crop_year['Year']) + "\">")
            f.write("<Crop CropNumber=\"1\">")
            f.write("<CropName>" + str(crop_year['Ccop_name']) + "</CropName>")
            f.write("<CropType>CROPS</CropType>")
            f.write("<PlantingDate>" + str(crop_year['planting_date']).strip('\"') + "</PlantingDate>")
            f.write("<ContinueFromPreviousYear>" + str(crop_year['continue_from_previous_year']) + "</ContinueFromPreviousYear>")
            # f.write("<DidYouPrune></DidYouPrune>") # todo
            # f.write("<RenewOrClearYourOrchard></RenewOrClearYourOrchard>") # todo
            # start harvest list
            f.write("<HarvestList>") # todo should i add conditional
            f.write("<HarvestEvent>") # todo
            f.write("<HarvestDate>" + str(crop_year['harvest_date']).strip('\"') + "</HarvestDate>")
            f.write("<Grain>" + str(crop_year['grain']) + "</Grain>")
            f.write("<yield>" + str(crop_year['yield']) + "</yield>")
            f.write("<StrawStoverHayRemoval>" + str(crop_year['straw_stover_hay_removal']) + "</StrawStoverHayRemoval>")
            f.write("</HarvestEvent>")
            f.write("</HarvestList>")
            # end harvest list
            f.write("<GrazingList />")
            f.write("<TillageList>")
            f.write("<TillageEvent>")
            f.write("<TillageType>" + str(crop_year['tillage_type']) + "</TillageType>")
            f.write("<TillageDate>" + str(crop_year['tillage_date']).strip('\"') + "</TillageDate>")
            f.write("</TillageEvent>")
            f.write("</TillageList>")
            # start fertilizer list
            f.write("<NApplicationList>") # todo should i add conditional
            f.write("<NApplicationEvent>")
            f.write("<NApplicationType>" + str(crop_year['n_application_type']) + "</NApplicationType>")
            f.write("<NApplicationMethod>" + str(crop_year['n_application_method']) + "</NApplicationMethod>")
            f.write("<NApplicationDate>" + str(crop_year['n_application_date']).strip('\"') + "</NApplicationDate>")
            f.write("<NApplicationAmount>" + str(crop_year['n_application_amount']) + "</NApplicationAmount>")
            f.write("<PApplicationAmount>" + "0" + "</PApplicationAmount>")
            f.write("<EEP>" + str(crop_year['eep']) + "</EEP>")
            f.write("</NApplicationEvent>")
            f.write("</NApplicationList>")
            # end fertilizer list
            # start omad application list
            f.write("<OMADApplicationList />")
            # end omad list
            # start irrigation list
            f.write("<IrrigationList />")
            # end irrigation list
            # start liming list
            f.write("<LimingList>")
            f.write("<LimingApplicationEvent>")
            f.write("<LimingApplicationDate></LimingApplicationDate>")
            f.write("<LimingMaterial></LimingMaterial>")
            f.write("<LimingApplicationAmount></LimingApplicationAmount>")
            f.write("</LimingApplicationEvent>")
            f.write("</LimingList>")
            # end liming list
            # start burning list
            # f.write("<BurningEvent>")
            # f.write("<DidYouBurnCropResidue>" + 'No' + "</DidYouBurnCropResidue>")
            # f.write("</BurningEvent>")
            f.write("<BurnEvent>")
            f.write("<BurnTime>No burning</BurnTime>")
            f.write("</BurnEvent>")
            # end burning list
            f.write("</Crop>")
            f.write("</CropYear>")

        f.write("</CropScenario>")

        if len(processed_sheets[field]['yearly_scenariob_data']) > 1:

            f.write("<CropScenario Name=\"" + processed_sheets[field]['scenario_b_name'] + "\">")

            for crop_year in processed_sheets[field]['yearly_scenario_data']:
                f.write("<CropYear Year=\"" + str(crop_year['Year']) + "\">")
                f.write("<Crop CropNumber=\"1\">")
                f.write("<CropName>" + str(crop_year['Ccop_name']) + "</CropName>")
                f.write("<CropType>CROPS</CropType>")
                f.write("<PlantingDate>" + str(crop_year['planting_date']).strip('\"') + "</PlantingDate>")
                f.write("<ContinueFromPreviousYear>" + str(crop_year['continue_from_previous_year']) + "</ContinueFromPreviousYear>")
                # f.write("<DidYouPrune></DidYouPrune>") # todo
                # f.write("<RenewOrClearYourOrchard></RenewOrClearYourOrchard>") # todo
                # start harvest list
                f.write("<HarvestList>") # todo should i add conditional
                f.write("<HarvestEvent>") # todo
                f.write("<HarvestDate>" + str(crop_year['harvest_date']).strip('\"') + "</HarvestDate>")
                f.write("<Grain>" + str(crop_year['grain']) + "</Grain>")
                f.write("<yield>" + str(crop_year['yield']) + "</yield>")
                f.write("<StrawStoverHayRemoval>" + str(crop_year['straw_stover_hay_removal']) + "</StrawStoverHayRemoval>")
                f.write("</HarvestEvent>")
                f.write("</HarvestList>")
                # end harvest list
                f.write("<GrazingList />")
                f.write("<TillageList>")
                f.write("<TillageEvent>")
                f.write("<TillageType>" + str(crop_year['tillage_type']) + "</TillageType>")
                f.write("<TillageDate>" + str(crop_year['tillage_date']).strip('\"') + "</TillageDate>")
                f.write("</TillageEvent>")
                f.write("</TillageList>")
                # start fertilizer list
                f.write("<NApplicationList>") # todo should i add conditional
                f.write("<NApplicationEvent>")
                f.write("<NApplicationType>" + str(crop_year['n_application_type']) + "</NApplicationType>")
                f.write("<NApplicationMethod>" + str(crop_year['n_application_method']) + "</NApplicationMethod>")
                f.write("<NApplicationDate>" + str(crop_year['n_application_date']).strip('\"') + "</NApplicationDate>")
                f.write("<NApplicationAmount>" + str(crop_year['n_application_amount']) + "</NApplicationAmount>")
                f.write("<PApplicationAmount>" + "0" + "</PApplicationAmount>")
                f.write("<EEP>" + str(crop_year['eep']) + "</EEP>")
                f.write("</NApplicationEvent>")
                f.write("</NApplicationList>")
                # end fertilizer list
                # start omad application list
                f.write("<OMADApplicationList />")
                # end omad list
                # start irrigation list
                f.write("<IrrigationList />")
                # end irrigation list
                # start liming list
                f.write("<LimingList>")
                f.write("<LimingApplicationEvent>")
                f.write("<LimingApplicationDate></LimingApplicationDate>")
                f.write("<LimingMaterial></LimingMaterial>")
                f.write("<LimingApplicationAmount></LimingApplicationAmount>")
                f.write("</LimingApplicationEvent>")
                f.write("</LimingList>")
                # end liming list
                # start burning list
                # f.write("<BurningEvent>")
                # f.write("<DidYouBurnCropResidue>" + 'No' + "</DidYouBurnCropResidue>")
                # f.write("</BurningEvent>")
                f.write("<BurnEvent>")
                f.write("<BurnTime>No burning</BurnTime>")
                f.write("</BurnEvent>")
                # end burning list
                f.write("</Crop>")
                f.write("</CropYear>")

            f.write("</CropScenario>")

        # begin crop 2
        # f.write("<CropYear Year=\"" + str(current_values['YEAR']) + "\">")
        # f.write("<Crop CropNumber=\"2\">")
        # f.write("</Crop>")
        # f.write("</CropYear>")
        # end crop 2
        # f.write("</CropScenario>")
        # end crop scenario
        f.write("</Cropland>\n")

    f.write("</Project>")
    f.write("</CometFarm>")

f.close()

print('XML file generated')
