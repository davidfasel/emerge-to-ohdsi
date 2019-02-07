import os, sys, re
import argparse
import csv
import OHDSI_Helper as helper


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
parser.add_argument(
    '-t', '--test',  metavar='lines',  #action='store_true',
    help = 'Only process the first n lines'
)
args =  parser.parse_args()

OMOP_fields = (
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

bmi_fields = {
  'height': {
    'measurement_concept_id' : '3023540',
    'measurement_type_concept_id': '44818701',
    'unit_concept_id': '8582', #cm
    'unit_source_value' : 'cm'
  },
  'weight': {
    'measurement_concept_id' : '3025315',
    'measurement_type_concept_id': '44818701',
    'unit_concept_id': '9529', #kg
    'unit_source_value' : 'kg'
  },
  'bmi': {
    'measurement_concept_id' : '3038553',
    'measurement_type_concept_id': '45754907',
    'unit_concept_id': '9531', #kg/m^2
    'unit_source_value' : 'kg/m2'
  }
}

eMERGE_fields = \
  ('subjid', 'bmi_observation_age', 'weight', 'height', 'bmi', 'visit_number')

# set all the output fields to empty string initially
OMOP_fields_dict = helper.getOmopDictionary(OMOP_fields)

# get the birth years from the demographics files
years_of_birth = helper.getYearsOfBirth(args.demo)

# get input csv reader and output file
input_file_reader, output_file = \
  helper.openFiles(args.input_file, '/OHDSI_output', header=OMOP_fields)

# skip the header
input_file_reader.next()

# read the input file
for i, line in enumerate(input_file_reader):
    # print the line number of the input file
    if (helper.printLineNumber(i, args.test) == False):
        sys.exit()

    # create a dictionary based on the eMERGE CPT fields
    eMergeData = helper.getEmergeFields(eMERGE_fields, line)
    # get the eMERGE BMI fields
    # subjid, bmi_observation_age, weight, height, bmi, visit_number = fields

    # figure out an approx date based on the age of the participant
    # discard line if age isn't present because OHDSI requires a date.
    measurement_date = helper.getDate(
      eMergeData['subjid'], eMergeData['bmi_observation_age'], years_of_birth
    )
    if (not measurement_date):
        helper.printLineError(i, eMergeData)
        continue

    # Fill in the output fields that we know from the OHDSI data.
    # Each of the 3 measurements get their own row.
    for row in ('weight', 'height', 'bmi'):
        OMOP_fields_dict['person_id'] = eMergeData['subjid']
        OMOP_fields_dict['measurement_date'] = measurement_date
        OMOP_fields_dict['visit_occurrence_id'] = eMergeData['visit_number']
        OMOP_fields_dict['measurement_concept_id'] = bmi_fields[row]['measurement_concept_id']
        OMOP_fields_dict['measurement_type_concept_id'] = bmi_fields[row]['measurement_type_concept_id']
        OMOP_fields_dict['unit_source_value'] = bmi_fields[row]['unit_source_value']

        if row == 'weight':
            OMOP_fields_dict['value_as_number'] = eMergeData['weight']
        elif row == 'height':
            OMOP_fields_dict['value_as_number'] = eMergeData['height']
        elif row == 'bmi':
            OMOP_fields_dict['value_as_number'] = eMergeData['bmi']

        helper.writeToOutputFile(OMOP_fields, OMOP_fields_dict, output_file)
        # output = []
        # for field in OMOP_fields:
        #     output.append(OMOP_fields_dict[field])
        #
        # output_file.write(','.join(output) + '\n')
