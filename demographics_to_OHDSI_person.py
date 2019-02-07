import sys, os, re
import argparse
import csv

parser = argparse.ArgumentParser(
  description='Convert eMERGE demographics CSV to OHDSI data model.'
 )
parser.add_argument(
  'demographics_file', type=argparse.FileType('r'), metavar='path',
  help='Demographics CSV file to convert'
)
args =  parser.parse_args()


gender_ids = {
    'C46109': ['8507', 'M'],
    'C46110': ['8532','F'],
    'U': ['8551','U',],
    '.': ['8551','U',],
    'NA': ['8551','U',],
}
race_ids = {
    'C16352': ['8516', 'B'],
    'C41259': ['8657', 'I'],
    'C41260': ['8515', 'A'],
    'C41261': ['8527', 'W'],
    'C41219': ['8557', 'P'],
    'C17998': ['8552', 'U'],
    'C43234': ['8552', 'U'],
    '.': ['8552', 'U'],
    'NA': ['8552', 'U'],
}
ethnicity_ids = {
    'C17459': ['38003563', 'H'],
    'C41222': ['38003564', 'N'],
    'C41221': ['0', 'U'],
    '.': ['0', 'U'],
    'NA': ['0', 'U'],
}
output_header = (
    'person_id',
    'gender_concept_id',
    'year_of_birth',
    'month_of_birth',
    'day_of_birth',
    'birth_datetime',
    'race_concept_id',
    'ethnicity_concept_id',
    'location_id',
    'provider_id',
    'care_site_id',
    'person_source_value',
    'gender_source_value',
    'gender_source_concept_id',
    'race_source_value',
    'race_source_concept_id',
    'ethnicity_source_value',
    'ethnicity_source_concept_id'
)
# values that won't be known from the eMERGE data
month_of_birth = ''
day_of_birth = ''
birth_datetime = ''
location_id = ''
provider_id = ''
care_site_id = ''
person_source_value = ''
gender_source_concept_id = ''
race_source_concept_id = ''
ethnicity_source_concept_id = ''


input_file =  args.demographics_file
# use a csv reader in case there are commas in quoted fields
input_file_reader = csv.reader(input_file, delimiter=',', quotechar='"')

dirname = os.path.dirname(input_file.name)

if not os.path.exists(dirname + '/OHDSI_output'):
    os.makedirs(dirname + '/OHDSI_output')

output_file_path =  '%s/OHDSI_output/%s.OHDSI.csv' % \
  (dirname, os.path.basename(input_file.name))

# use a csv reader in case there are commas in quoted fields
input_file_reader = csv.reader(input_file, delimiter=',', quotechar='"')
output_file = open(output_file_path, 'w')

# print the header for the output file
output_file.write(','.join(output_header) + '\n')

# skip header of input file
header =  input_file_reader.next()

# read the file and get all the feilds
for i, line in enumerate(input_file_reader):
    print "%s \r" % (i + 1)
    subjid, decade_birth, year_birth, sex, race, ethnicity = line[0:6]
    #exit()

    output = (                            #OHDSI field (if different):
        subjid,                           #person_id
        gender_ids[sex][0],            #gender_concept_id
        year_birth,                       #year_of_birth
        month_of_birth,
        day_of_birth,
        birth_datetime,
        race_ids[race][0],             #race_concept_id
        ethnicity_ids[ethnicity][0],   #ethnicity_concept_id
        location_id,
        provider_id,
        care_site_id,
        person_source_value,
        gender_ids[sex][1],            #gender_source_value
        gender_source_concept_id,
        race_ids[race][1],             #race_source_value
        race_source_concept_id,
        ethnicity_ids[ethnicity][1],   #ethnicity_source_value
        ethnicity_source_concept_id
    )
    output_file.write(','.join(output) + '\n')
