# import system modules
import os, sys, pprint

# import functions for extracting data from excel
from openpyxl import load_workbook

# check if argument for workbook has been given
if len(sys.argv) < 1:
    print("\n")
    print("python3 script generate_comet_input_file.py <spreadsheet location>")
    print("\n")
    print("Command-line arguments are as follows:")
    print("  <spreadsheet locatiion> system location of spreadsheet with input data")
    print("    eg /usr/local/name/comet/data.xml")
    print("")
    exit()

wb_dir = sys.argv[1]
wb = load_workbook(filename = wb_dir)
processed_fields_sheet = wb.get_sheet_by_name('processed')
processed_sheets = {}
for row in range(1, processed_fields_sheet.max_row + 1):
    sheet_name = processed_fields_sheet['B' + str(row)].value

    scenario_sheet = wb.get_sheet_by_name(sheet_name)
    scenario_values = {}
    # loop through scenario values
    for row in range(2, scenario_sheet.max_row + 1):
        param  = scenario_sheet['A' + str(row)].value
        param_val  = scenario_sheet['B' + str(row)].value
        scenario_values.setdefault(param, param_val)

    # create XML file
    input_xml_file_name = sheet_name
    input_xml_file = input_xml_file_name + '.xml'

    if (os.path.isfile(input_xml_file)):
        os.remove(input_xml_file)

    # initialize the file content string that will contain the text to be written to the file
    with open(input_xml_file, 'w') as f:
        f.write("<Day cometEmailId=\"" + scenario_values['Email'] + "\">")
        # todo: rename cropland something more meaningful
        f.write("<Cropland name=\"" + scenario_values['crop_scenario_name'] + "\">")
        f.write("<GEOM SRID=\"" + str(scenario_values['SRID']) + "\" AREA=\"" + str(scenario_values['AREA']) + "\">" + scenario_values['GEOM'] + "</GEOM>")
        f.write("<Pre-1980>" + scenario_values['pre_80'] + "</Pre-1980>")
        # CRP always None
        f.write("<CRP>None</CRP><CRPStartYear></CRPStartYear><CRPEndYear></CRPEndYear><CRPType>None</CRPType>")
        # PreCRPManagement fields always empty
        f.write("<PreCRPManagement></PreCRPManagement><PreCRPTillage></PreCRPTillage><PostCRPManagement></PostCRPManagement><PostCRPTillage></PostCRPTillage>")
        # 1980 - 2000
        f.write("<Year1980-2000>" + scenario_values['yr80_2000'] + "</Year1980-2000>")
        f.write("<Year1980-2000_Tillage>" + scenario_values['till80_200'] + "</Year1980-2000_Tillage>")
        # start crop scenario
        f.write("<CropScenario Name=\"" + scenario_values['crop_scenario_name'] + "\">")
        # crop year
        f.write("<CropYear Year=\"" + str(scenario_values['YEAR']) + "\">")
        f.write("<Crop CropNumber=\"1\">")
        f.write("<CropName>" + scenario_values['Ccop_name'] + "</CropName>")
        f.write("<PlantingDate>" + scenario_values['planting_date'].strip('\"') + "</PlantingDate>")
        f.write("<ContinueFromPreviousYear>" + scenario_values['continue_from_previous_year'] + "</ContinueFromPreviousYear>")
        f.write("<DidYouPrune></DidYouPrune>") # todo
        f.write("<RenewOrClearYourOrchard></RenewOrClearYourOrchard>") # todo
        # start harvest list
        f.write("<HarvestList>") # todo should i add conditional
        f.write("<HarvestEvent>") # todo
        f.write("<HarvestDate>10/23/2000</HarvestDate>") # todo
        f.write("<Grain>Yes</Grain>") # todo
        f.write("<yield>167.0</yield>") # todo
        f.write("<StrawStoverHayRemoval>0</StrawStoverHayRemoval>") # todo
        f.write("</HarvestEvent>")
        f.write("</HarvestList>")
        # end harvest list
        # start fertilizer list
        f.write("<NApplicationList>") # todo should i add conditional
        f.write("<NApplicationEvent>")
        f.write("<NApplicationDate>05/07/2000</NApplicationDate>") # todo
        f.write("<NApplicationType>UAN</NApplicationType>") # todo
        f.write("<NApplicationAmount>116.4</NApplicationAmount>") # todo
        f.write("<NApplicationMethod>Surface Band / Sidedress</NApplicationMethod>") # todo
        f.write("<EEP>None</EEP>") # todo
        f.write("</NApplicationEvent>")
        f.write("</NApplicationList>")
        # end fertilizer list
        # start omad application list
        f.write("<OMADApplicationList>")
        f.write("<OMADApplicationEvent>")
        f.write("<OMADApplicationDate></OMADApplicationDate>")
        f.write("<OMADType></OMADType>")
        f.write("<OMADApplicationAmount></OMADApplicationAmount>")
        f.write("<OMADPercentN></OMADPercentN>")
        f.write("<OMADCNRatio></OMADCNRatio>")
        f.write("</OMADApplicationEvent>")
        f.write("</OMADApplicationList>")
        # end omad list
        # start irrigation list
        f.write("<IrrigationList>")
        f.write("<IrrigationApplicationEvent>")
        f.write("<IrrigationApplicationDate></IrrigationApplicationDate>")
        f.write("<IrrigationApplicationAmount></IrrigationApplicationAmount>")
        f.write("</IrrigationApplicationEvent>")
        f.write("</IrrigationList>")
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
        f.write("<BurningList>")
        f.write("<BurningEvent>")
        f.write("<DidYouBurnCropResidue>No Burning</DidYouBurnCropResidue>") # todo
        f.write("</BurningEvent>")
        f.write("</BurningList>")
        # end burning list
        f.write("</Crop>")
        f.write("</CropYear>")
        # end crop 1
        # begin crop 2
        # f.write("<CropYear Year=\"" + str(scenario_values['YEAR']) + "\">")
        # f.write("<Crop CropNumber=\"2\">")
        # f.write("</Crop>")
        # f.write("</CropYear>")
        # end crop 2
        f.write("</CropScenario>")
        # end crop scenario
        f.write("</Cropland>\n")
        f.write("</Day>")
        # end daycent
        f.close()

print('XML file generated')
