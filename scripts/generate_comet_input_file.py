# import system modules
import os, sys, pprint

# import functions for extracting data from excel
from openpyxl import load_workbook

# check if argument for workbook has been given
if len(sys.argv) < 1:
    print("\n")
    print("python script generate_comet_input_file.py <spreadsheet location>")
    print("\n")
    print("Command-line arguments are as follows:")
    print("  <spreadsheet locatiion> system location of spreadsheet with input data")
    print("    eg /usr/local/name/comet/data.xml")
    print("")
    exit()

wb_dir = sys.argv[1]
wb = load_workbook(filename = wb_dir)
scenario_sheet = wb.get_sheet_by_name('scenario')
scenario_values = {}
# loop through scenario values
for row in range(2, scenario_sheet.max_row + 1):
    param  = scenario_sheet['A' + str(row)].value
    param_val  = scenario_sheet['B' + str(row)].value
    scenario_values.setdefault(param, param_val)

# create XML file
input_xml_file_name = scenario_values['crop_scenario_name']
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
    f.write("<Year1980-2000>" + scenario_values['yr80_2000'] + "</Year1980-2000>")
    f.write("<Year1980-2000_Tillage>" + scenario_values['till80_200'] + "</Year1980-2000_Tillage>")
    f.write("<CropScenario Name=\"" + scenario_values['crop_scenario_name'] + "\">")

    f.write("</CropScenario>")
    f.write("</Cropland>\n")
    f.write("</Day>")
    f.close()

print('XML file generated')
