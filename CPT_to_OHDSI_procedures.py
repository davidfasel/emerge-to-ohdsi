import os, sys
import argparse
import csv
import OHDSI_Helper as helper


parser = argparse.ArgumentParser(
  description='Convert eMERGE Procedures to OHDSI data model.'
 )
parser.add_argument(
    'input_file', type=argparse.FileType('r'), metavar='input_file',
    help='eMERGE Procedures CSV file to convert'
)
parser.add_argument(
  '-d', '--demo', required=True, metavar='demographics_file',
  type= argparse.FileType('r'),
  help = '''A required file containing the demographics to extract year of birth to calculate drug start date'''
)
parser.add_argument(
    '-t', '--test',  metavar='lines',  #action='store_true',
    help = 'Only process the first n lines'
)
args =  parser.parse_args()

OMOP_fields = [
    'procedure_occurrence_id',
    'person_id',
    'procedure_concept_id',
    'procedure_date',
    'procedure_datetime',
    'procedure_type_concept_id',
    'modifier_concept_id',
    'quantity',
    'provider_id',
    'visit_occurrence_id',
    'procedure_source_value',
    'procedure_source_concept_id',
    'qualifier_source_value'
]

eMERGE_fields = ('subjid', 'cpt_age', 'cpt_code')

OMOP_fields_dict = helper.getOmopDictionary(OMOP_fields)

# get input csv reader and output file
input_file_reader, output_file = \
  helper.openFiles(args.input_file, '/OHDSI_output', header=OMOP_fields)
# skip the header
input_file_reader.next()

# get the birth years from the demographics files
years_of_birth = helper.getYearsOfBirth(args.demo)

# read the file and get all the feilds
for i, line in enumerate(input_file_reader):
    if (helper.printLineNumber(i, args.test) == False):
        sys.exit()

    # create a dictionary based on the eMERGE CPT fields
    eMergeData = helper.getEmergeFields(eMERGE_fields, line)

    # Calculate an approx date based on the age of the participant.
    # Discard line if age isn't present because OHDSI requires a date.
    procedure_date = \
      helper.getDate(eMergeData['subjid'], eMergeData['cpt_age'], years_of_birth)

    if (not procedure_date or not helper.validateNotMissing(eMergeData['cpt_code'])):
        helper.printLineError(i, eMergeData)
        continue

    # fill in the output fields that we know from the OHDSI data
    OMOP_fields_dict['person_id'] = eMergeData['subjid']
    #OMOP_procedure_fields[procedure_concept_id} = xxx
    OMOP_fields_dict['procedure_date'] = procedure_date
    OMOP_fields_dict['procedure_source_value'] = \
      'C4:'+ eMergeData['cpt_code']

    #OMOP_procedure_fields{procedure_source_concept_id} = xxx

    output = []
    for field in OMOP_fields:
        output.append(OMOP_fields_dict[field])

    try:
        output_file.write(','.join(output) + '\n')
    except:
        helper.printLineError(i, output)
