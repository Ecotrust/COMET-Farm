# import system modules
import os, sys, csv

# import functions for extracting data from excel
from openpyxl import load_workbook

# check if argument for workbook has been given
if len(sys.argv) < 2:
    print("\npython script generate_comet_input_file.py <GIS data location> <spreadsheet location>\n")
    print("Command-line arguments are as follows:\n")
    print("  <GIS data location> system location of comma separated data from GIS\n")
    print("    eg /usr/local/name/comet/data.csv\n")
    print("  <spreadsheet locatiion> system location of spreadsheet to add GIS data\n")
    print("    eg /usr/local/name/comet/data.xml\n\n")
    exit()

gis_dir =  sys.argv[1]
wb_dir = sys.argv[2]

wb = load_workbook(filename = wb_dir)
scenario_sheet = wb.get_sheet_by_name('scenario')

gis_values = {}

# open GIS data file and save it as dict
with open(gis_dir) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    csv_dict = csv.DictReader(csv_file)
    gis_values = csv_dict
    print(gis_values)
    # for row in csv_dict:
        # print(dict(row))
        # param  = scenario_sheet['A' + str(row)].value
        # param_val  = scenario_sheet['B' + str(row)].value
        # scenario_values.setdefault(param, param_val)

    # add gis data to spreadsheet
    for row in gis_values:
        new_scenario_sheet = wb.copy_worksheet(scenario_sheet)
        print(new_scenario_sheet)
        for rowNum in range(2, new_scenario_sheet.max_row):
            rowName = new_scenario_sheet.cell(row=rowNum, column=1).value
            print(rowName)
            if rowName == 'GEOM':
                new_scenario_sheet.cell(row=rowNum, column=2).value = "Polygon(" + row['geom'] + ")"

wb.save('combined_data.xlsx')
