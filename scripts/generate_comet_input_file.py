# import system modules
import os, sys

# import functions for extracting data from excel
from openpyxl import load_workbook

# check if argument for workbook has been given
if len( sys.argv ) < 1:
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

print(input_xml_file_name)
