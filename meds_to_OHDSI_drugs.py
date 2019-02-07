## convert emerge demographics file to OHDSI data model

import os
import argparse
import math
import csv

parser = argparse.ArgumentParser(
  description='Convert eMERGE drugs CSV to OHDSI data model.'
 )
parser.add_argument(
  'meds_file', type=argparse.FileType('r'), metavar='path',
  help='Demographics CSV file to convert'
)
parser.add_argument(
  '--demo', '-d', required=True, metavar= 'path', type= argparse.FileType('r'),
  help = '''A file containing the demographics to extract year of birth to
            calculate drug start date'''
)
args =  parser.parse_args()

drugs = {
    '221072' : ['1586226','erivastatin sodium'],
    '301542' : ['1510813','rosuvastatin'],
    '36567' : ['1539403', 'simvastatin'],
    '41127' : ['1549686', 'fluvastatin'],
    '42463' : ['1551860', 'pravastatin'],
    '6472' : ['1592085', 'lovastatin'],
    '83367' : ['1545958', 'atorvastatin'],
    '861634' : ['40165636', 'pitavastatin'],
}

output_header = (
    'drug_exposure_id',
    'person_id',
    'drug_concept_id',
    'drug_exposure_start_date',
    'drug_exposure_start_datetime',
    'drug_exposure_end_date',
    'drug_exposure_end_datetime',
    'drug_type_concept_id',
    'stop_reason',
    'refills',
    'quantity',
    'days_supply',
    'sig',
    'route_concept_id',
    'effective_drug_dose',
    'dose_unit_concept_id',
    'lot_number',
    'provider_id',
    'visit_occurrence_id',
    'drug_source_value',
    'drug_source_concept_id',
    'route_source_value',
    'dose_unit_source_value',
)
# values that won't be known from the eMERGE data
drug_exposure_id = ''
drug_exposure_start_datetime = ''
drug_exposure_end_date = ''
drug_exposure_end_datetime = ''
drug_type_concept_id = '38000177'
stop_reason = ''
refills = ''
quantity = ''
days_supply = ''
sig = ''
route_concept_id = ''
effective_drug_dose = ''
dose_unit_concept_id = ''
lot_number = ''
provider_id = ''
visit_occurrence_id = ''
drug_source_concept_id = ''
route_source_value = ''
dose_unit_source_value = ''


input_file =  args.meds_file
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
output_file.write(','.join(output_header) + '\n')

# skip the input file's header
header =  input_file.readline()

# read the file and get all the feilds
for line in input_file_reader:
    subjid, drug_observation_age, drug_rxcui_code = line[:3]

    drug_observation_age = int(float(drug_observation_age))
    drug_year = int(years_of_birth[subjid]) + drug_observation_age
    drug_exposure_start_date = str(drug_year) + '-01-01'

    output = (
        drug_exposure_id,
        subjid,
        drugs[drug_rxcui_code][0], #drug_concept_id,
        drug_exposure_start_date,
        drug_exposure_start_datetime,
        drug_exposure_end_date,
        drug_exposure_end_datetime,
        drug_type_concept_id,
        stop_reason,
        refills,
        quantity,
        days_supply,
        sig,
        route_concept_id,
        effective_drug_dose,
        dose_unit_concept_id,
        lot_number,
        provider_id,
        visit_occurrence_id,
        drugs[drug_rxcui_code][1], #drug_source_value (drug name)
        drug_source_concept_id,
        route_source_value,
        dose_unit_source_value,
    )
    output_file.write(','.join(output) + '\n')
