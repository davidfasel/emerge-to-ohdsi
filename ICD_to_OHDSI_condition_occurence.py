import os, sys, re
import argparse
import csv


parser = argparse.ArgumentParser(
  description='Convert eMERGE BMI to OHDSI data model.'
 )
parser.add_argument(
  'input_file', type=argparse.FileType('r'), metavar='path',
  help='The eMERGE BMI CSV file to convert.'
)
parser.add_argument(
  '--demo', '-d', required=True, metavar= 'path', type= argparse.FileType('r'),
  help = '''A file containing the demographics to extract year of birth to
            calculate drug start date.'''
)
args =  parser.parse_args()

OMOP_fields = (
    'condition_occurrence_id',
    'person_id',
    'condition_concept_id',
    'condition_start_date',
    'condition_start_datetime',
    'condition_end_date',
    'condition_end_datetime',
    'condition_type_concept_id',
    'stop_reason',
    'provider_id',
    'visit_occurrence_id',
    'condition_source_value',
    'condition_source_concept_id',
)

input_file =  args.input_file
demographics_file =  args.demo

dirname = os.path.dirname(input_file.name)

if not os.path.exists(dirname + '/OHDSI_output'):
    os.makedirs(dirname + '/OHDSI_output')

output_file_path =  '%s/OHDSI_output/%s.OHDSI.csv' % \
  (dirname, os.path.basename(input_file.name))

input_file_reader = csv.reader(input_file, delimiter=',', quotechar='"')
output_file = open(output_file_path, 'w')


# get the birth years from the demographics files
years_of_birth = {}
for line in demographics_file:
    subjid, decade_birth, year_birth, remaining = line.split(',', 3)
    years_of_birth[subjid] = year_birth


# print the header for the output file
output_file.write(','.join(OMOP_fields) + '\n')
# skip the input file's header
header =  input_file.readline()

# read the file and get all the feilds
for i, line in enumerate(input_file_reader):
    # print the line number of the input file (+2 for header and 0 index)
    print('\r%s' % (i+2)),

    # convert "." (missing) to empty string (db null)
    fields = map(lambda x: re.sub('^\.$', '', x), line)
    # get the eMERGE BMI fields
    subjid, icd_age, icd_code, icd_flag = fields

    # figure out an approximate date for the condition based on the age of
    # the participant at the time of the condition.
    condition_date = ''
    if (icd_age != ""):
        condition_year = int(years_of_birth[subjid]) + int(float(icd_age))
        condition_date = str(condition_year) + '-01-01'
    # discard line if age isn't present.  OHDSI requires a measurement_date.
    else:
        continue

    # set all the output fields to empty string initially
    OMOP_fields_dict = {}
    for field in OMOP_fields:
        OMOP_fields_dict[field] = ''

    ICD_code = "I%s:%s" % (icd_flag, icd_code)

    # Fill in the output fields that we know from the OHDSI data.
    # Each of the 3 get their own row.
    OMOP_fields_dict['person_id'] = subjid
    OMOP_fields_dict['condition_start_date'] = condition_date
    OMOP_fields_dict['condition_source_value'] = ICD_code

    output = []
    for field in OMOP_fields:
        output.append(OMOP_fields_dict[field])

    output_file.write(','.join(output) + '\n')
