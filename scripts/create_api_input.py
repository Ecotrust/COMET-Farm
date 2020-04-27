# import system modules
import os, sys, csv, datetime
from datetime import datetime

# import functions for extracting data from excel
from openpyxl import load_workbook

# check if argument for workbook has been given
if len(sys.argv) == 1 or len(sys.argv) > 3:
    print("\nMissing arguments")
    print("expecting 1 or 2 arguments")
    print("  1. GIS data")
    print("  2. spreadsheet v2 (optional)")
    print("\nexpected command (Windows sub `python3` with `py -3`)")
    print("  `python3 ./script/create_api_input.py <GIS data location> <spreadsheet location>`\n")
    print("Command-line arguments are as follows:\n")
    print("  * <GIS data location> system location of comma separated data from GIS")
    print("      e.g.,  /usr/local/name/comet/data.csv\n")
    print("  * <spreadsheet locatiion> system location of spreadsheet to add GIS data")
    print("      e.g.,  /usr/local/name/comet/data.xlsx")
    print("      ** if not given defaults to template_v2.xlsx at repo root\n")
    exit()

if len(sys.argv) == 2:
    script_dir =  sys.argv[0]
    gis_dir =  sys.argv[1]
    script_path = os.path.dirname(os.path.realpath(__file__))
    wb_dir = script_path + '/../template_v2.xlsx'

elif len(sys.argv) == 3:
    script_dir =  sys.argv[0]
    gis_dir =  sys.argv[1]
    wb_dir = sys.argv[2]

wb = load_workbook(filename = wb_dir)
scenario_sheet = wb['scenario']

gis_values = {}

# create sheet for list of processed fields
processed_sheet = wb.create_sheet('processed')

# open GIS data file and save it as dict
with open(gis_dir) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    csv_dict = csv.DictReader(csv_file)
    gis_values = csv_dict

    # for row in gis_values:
        # print(dict(row))
        # param  = scenario_sheet['A' + str(row)].value
        # param_val  = scenario_sheet['B' + str(row)].value
        # scenario_values.setdefault(param, param_val)

    # add gis data to spreadsheet
        # field_ID,CRP,CRPType,GEOM,SRID,AREA,pre_80,yr80_2000,CRP_NUM,CcopName,planting_date,harvest_date,grain,till_date,n_app_date
    for row in gis_values:
        field_sheet = wb.copy_worksheet(scenario_sheet)
        field_sheet.title = 'ready_' + row['field_ID']
        processed_sheet.append(["name", field_sheet.title])

        # field_sheet.cell(row=8, column=2).value = row['CRP_NUM'] #dc added 1/16/20
        field_sheet.cell(row=9, column=2).value = row['field_ID']
        field_sheet.cell(row=10, column=2).value = 'POLYGON (' + row['GEOM'] + ')'
        field_sheet.cell(row=11, column=2).value = row['AREA']
        field_sheet.cell(row=12, column=2).value = row['SRID']
        field_sheet.cell(row=13, column=2).value = field_sheet.cell(row=7, column=2).value + row['CcopName'] + '_' + '_' + row['field_ID']

        for crop_cell in field_sheet.iter_cols(min_col=3,max_col=17,min_row=17,max_row=36):
            for cell in crop_cell:
                if cell.column == 3:
                    cell.value = row['CRP']
                elif cell.column == 4 or cell.column == 6 or cell.column == 11 or cell.column == 13:
                    # get year from template spreadsheet
                    yyyy = cell.value[-5:-1]
                    # get month and day from GIS data
                    # formated as number day of year ex: 32
                    if cell.column == 4:
                        day_num_of_year = row['planting_date']
                    elif cell.column == 5:
                        day_num_of_year = row['harvest_date']
                    elif cell.column == 11:
                        day_num_of_year = row['till_date']
                    elif cell.column == 13:
                        day_num_of_year = row['n_app_date']
                    # combine and format
                    month_day = datetime.strptime(day_num_of_year, '%j')
                    # convert to the orginially expected format of Month, day ex: March 14
                    month_day = month_day.strftime('%B %d')
                    # add the year to month day from the template spreadsheet
                    mmddyyyy = month_day + yyyy
                    # format ex: March 152020
                    mmddyyyy = datetime.strptime(mmddyyyy, '%B %d%Y')
                    # convert to CF API expected format ex: 03/14/2020
                    cfarm_format_date = mmddyyyy.strftime('%m/%d/%Y')
                    # add formated date to template spreadsheet
                    cell.value = cfarm_format_date
                elif cell.column == 8:
                    row_lowercase = row['grain'].lower()
                    if row_lowercase == 'yes' or row_lowercase == 'true':
                        cell.value = 'TRUE'
                    else:
                        cell.value = 'FALSE'


        for crop_cell in field_sheet.iter_cols(min_col=3,max_col=3,min_row=40,max_row=49):
            for cell in crop_cell:
                cell.value = row['CRP']

        for crop_cell in field_sheet.iter_cols(min_col=3,max_col=3,min_row=53,max_row=62):
            for cell in crop_cell:
                cell.value = row['CRP']


                # if rowName == 'crop_number':
                #     field_sheet.cell(row=rowNum, column=2).value = row['CRP_NUM'] #dc added 1/16/20
                # if rowName == 'planting_date':
                #     field_sheet.cell(row=rowNum, column=2).value = row['planting_date']  #dc added 1/16/20
                # if rowName == 'harvest_date':
                #     field_sheet.cell(row=rowNum, column=2).value = row['harvest_date'] #dc added 1/16/20
                # if rowName == 'tillage_date':
                #     field_sheet.cell(row=rowNum, column=2).value = row['till_date']    #dc added 1/16/20
                # if rowName == 'n_application_date':
                #     field_sheet.cell(row=rowNum, column=2).value = row['n_app_date'] #dc added 1/16/20
                # if rowName == 'grain':
                #     field_sheet.cell(row=rowNum, column=2).value = row['grain'] #dc added 1/16/20
                # if rowName == 'pre_80':
                #     pre_1980_sheet = wb['pre1980']
                #     pre_80_gis_val = row['pre_80'] #changed 'pre-80' to 'pre_80'
                #     pre_1980_val = pre_1980_sheet.cell(row=int(pre_80_gis_val), column=1).value
                #     field_sheet.cell(row=rowNum, column=2).value = pre_1980_val
                # if rowName == 'yr80_2000':
                #     year80_sheet = wb['yr80']
                #     year80_sheet_val = row['yr80_2000'] #changed 'Year1980-2000' to 'yr80_2000'
                #     yr_80_val = year80_sheet.cell(row=int(year80_sheet_val), column=1).value
                #     field_sheet.cell(row=rowNum, column=2).value = yr_80_val
                #if rowName == 'till80_200':
                    #till_80_sheet = wb['tillage']
                    #till_80_sheet_val = row['Year1980-2000_Tillage']
                    #till_80_val = till_80_sheet.cell(row=int(till_80_sheet_val), column=1).value
                    #field_sheet.cell(row=rowNum, column=2).value = till_80_val

script_path = os.path.dirname(os.path.realpath(__file__))

wb.save(script_path + "/../combined_data.xlsx")

print("\nSuccessfully merged GIS and Excel template.\n")
print("Creating XML...\n")

if sys.platform.startswith('darwin') or sys.platform.startswith('linux'):
    os.system("python3 " + script_path + "/generate_comet_input_file.py ../combined_data.xlsx")
elif sys.platform.startswith('win32') or sys.platform.startswith('cygwin'):
    os.system("py -3 " + script_path + "/generate_comet_input_file.py ../combined_data.xlsx")
