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
print(wb.sheetnames)
