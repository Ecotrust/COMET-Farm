#!/usr/bin/python3

import os, sys

# some constants
root_path = os.path.dirname(os.path.abspath(__file__))
script_rel_path = os.path.dirname(os.path.realpath(__file__))
project_path = "G:\\projects\\Moore_Climate2018\\"
master_path = os.path.join(project_path, "COMET-Farm-master")
script_path = os.path.join(master_path, "scripts")
scenario_templates_path = os.path.join(master_path, "scenario_templates")
inputs_path = os.path.join(master_path, "inputs")
integrated_path = os.path.join(master_path, "integrated")
help_text = 'usage: run_comet_crop.py <subject crop> <iso class | all>'

# Figure out what operating system is running script
if sys.platform.startswith('darwin') or sys.platform.startswith('linux'):
    # use python3
    python_interpreter = 'python3'
elif sys.platform.startswith('win32') or sys.platform.startswith('cygwin'):
    # use py -3
    python_interpreter = 'py -3'
else:
    # just hope python works
    python_interpreter = 'python'

# Python 2.7 for running extact geom script
# GIS depends on python 2.7 and can't use python 3 - this is actually the arcgis instance of python under the arcgis folder.
python_2 = 'C:\\Python27\\ArcGIS10.4\\python'

# check for expected arguments
if len(sys.argv) == 3:
    subject_crop = sys.argv[1]
    print(str(subject_crop))
    iso_class = sys.argv[2]
else:
    print("\n")
    print("missing or too many arguments. Expecting two: crop and isoclass.")
    print(help_text)
    print("\n")
    sys.exit()

# Run extract geometry script
# will only run on python 2.7
os.system(python_2 + " " + project_path + "\\util\\scripts\\extract_geom.py " + str(subject_crop) + " " + str(iso_class))

# Assign the path for the crop templates
crop_templates_path = os.path.join(scenario_templates_path, subject_crop)
crop_inputs_path = os.path.join(inputs_path, subject_crop)

# Extract geom created a directory of comet_dat files
# all comet_dat files in that directory need to be combined with the appropriate crop scenario template(s)
# the crop scenario templates path is a directory with one of more templates
# summary: each comet_dat file needs to be combined with each crop scenario template
for dat_file in os.listdir(crop_inputs_path):
    dat_file_path = os.path.join(crop_inputs_path, dat_file)
    if os.path.exists(dat_file_path):
        print('\n' + 'Found dat: ' + dat_file)
        # Loop through scenarios template for the current dat file
        for file_name in os.listdir(crop_templates_path):
            print('Found: ' + file_name)
            if file_name.endswith(".xlsm") or file_name.endswith(".csv") or file_name.endswith(".xls"):
                print('File is in correct format')
            else:
                print('ERROR - Wrong format for file (expecting .xlsm, .csv, or .xls): ' + file_name)
                sys.exit()
            file_path = os.path.join(crop_templates_path, file_name)
            if os.path.exists(file_path):
                print('Combining: \n  * ' + dat_file_path + '\n * ' + file_path + '\n')
                os.system(python_interpreter + " " + script_path + "\\create_api_input.py" + " " + dat_file_path + " " + file_path + " " + file_name)
            else:
                print('Error - File does not exist:' + file_path)
    else:
        print('Error - Dat file path does not exist: ' + dat_file_path)

# Files for each scenario template should now be intergrated with comet dat
# the integrated file(s) is saved in the 'integrated' folder
# loop through each integrated file(s) and call generate comet input script
# provded the integrated file as an arg
for integrated_file in os.listdir(integrated_path):
    print('\nGenerating XML for: ' + integrated_file)
    integrated_file_name = integrated_file[:-5]
    integrated_file_path = os.path.join(integrated_path, integrated_file)
    os.system(python_interpreter + " " + script_path + "\\generate_comet_input_file.py" + " " + integrated_file_path + ' ' + integrated_file_name)

print("\n")
print("All done here. Now sit tight while you wait for Comet-Farm to run.")
print("When Comet-Farm is done a email is sent to the email address used at the bottom of generate_comet_input script.")
print("\n")
print("...")
