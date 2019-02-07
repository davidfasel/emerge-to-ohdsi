import os, re
import argparse
import math
import csv

## Script to convert emerge demographics file to OHDSI data model ##

parser = argparse.ArgumentParser(
  description='Convert eMERGE meds CSV to OHDSI data model.'
 )
parser.add_argument(
  'labs_file', type=argparse.FileType('r'), metavar='path',
  help='Demographics CSV file to convert'
)
parser.add_argument(
  '--demo', '-d', required=True, metavar= 'path', type= argparse.FileType('r'),
  help = '''A file containing the demographics to extract year of birth to
            calculate measurement start date'''
)
args =  parser.parse_args()

labs = {
    'serum_total_cholesterol' : ['3027114','8840', 'mg/dl'],
    'ldl' : ['3035899','8840', 'mg/dl'],
    'hdl' : ['3007070','8840', 'mg/dl'],
    'triglyceride' : ['3022192','8840', 'mg/dl'],
    'glucose_fasting' : ['3037110','8840', 'mg/dl'],
    'glucose_nonfasting' : ['3004501','8840', 'mg/dl'],
    'glucose_nonfast' : ['3004501','8840', 'mg/dl'],
    'glucose_unknown' : ['3004501','8840', 'mg/dl'],
    'white_blood_cell' : ['3000905', '9444', '10*9/l'],
}
output_header = (
    'measurement_id',
    'person_id',
    'measurement_concept_id',
    'measurement_date',
    'measurement_datetime',
    'measurement_type_concept_id',
    'operator_concept_id',
    'value_as_number',
    'value_as_concept_id',
    'unit_concept_id',
    'range_low',
    'range_high',
    'provider_id',
    'visit_occurrence_id',
    'measurement_source_value',
    'measurement_source_concept_id',
    'unit_source_value',
    'value_source_value',
)
# values that won't be known from the eMERGE data or are consitent
measurement_id = ''
measurement_datetime = ''
measurement_type_concept_id = '44818702'
operator_concept_id =  ''
value_as_concept_id = ''
range_low = ''
range_high = ''
provider_id = ''
measurement_source_concept_id = ''
unit_source_value = ''
value_source_value = ''


## Open all the input and output files
input_file =  args.labs_file
demographics_file =  args.demo

# use a csv reader in case there are commas in quoted fields
input_file_reader = csv.reader(input_file, delimiter=',', quotechar='"')


dirname = os.path.dirname(input_file.name)

if not os.path.exists(dirname + '/OHDSI_output'):
    os.makedirs(dirname + '/OHDSI_output')

output_file_path =  '%s/OHDSI_output/%s.OHDSI.csv' % \
  (dirname, os.path.basename(input_file.name))

output_file = open(output_file_path, 'w')



## Get the birth years from the demographics files
# this is used to estimate the measurement date using the patients' birth
# year and age at measurement.
years_of_birth = {}
for line in demographics_file:
    subjid, decade_birth, year_birth, remaining = line.split(',', 3)
    years_of_birth[subjid] = year_birth


## Process the eMERGE file and output to OHDSI data model

# skip the input file's header
header =  input_file.readline()

# print the header for the output file
output_file.write(','.join(output_header) + '\n')

# read the file and get all the feilds
for line in input_file_reader:
    # unpack the fields from the line array created by the csv reader
    subjid, labs_observation_age, lab_name, lab_value, visit_number = line

    lab_name = lab_name.lower()

    # Meausrement date is estimated by year of birth plus age at measurement.
    # Could make this more accurate by using the age decimal value to
    # get the approximate days into the year and convert that to a day and month
    measurement_observation_age = int(float(labs_observation_age))
    measurement_year = int(years_of_birth[subjid]) + measurement_observation_age
    measurement_date = str(measurement_year) + '-01-01'

    # don't include lab values other than numbers or decimal point.
    # OHDSI expects float
    if re.search('[^\d\.]', lab_value):
        continue

    # change a single dot indicating "missing" to just and empty string.
    # OHDSI expects float or int respectively.
    lab_value = re.sub('^.$', "", lab_value)
    visit_number = re.sub('^.$', "", visit_number)

    # create the ouput array based on all the variables we have set above
    output = (
        measurement_id,
        subjid,
        labs[lab_name][0],   #measurement_concept_id,
        measurement_date,
        measurement_datetime,
        measurement_type_concept_id,
        operator_concept_id,
        lab_value,           #value_as_number,
        value_as_concept_id,
        labs[lab_name][1],   #unit_concept_id,
        range_low,
        range_high,
        provider_id,
        visit_number,       #visit_occurrence_id,
        lab_name,           #measurement_source_value,
        measurement_source_concept_id,
        labs[lab_name][2],  #unit_source_value,
        value_source_value,
    )
    output_file.write(','.join(output) + '\n')
