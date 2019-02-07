import os, re, sys
import csv

def openFiles(input_file, output_dir, header):
    input_file_reader = csv.reader(input_file, delimiter=',', quotechar='"')

    input_path = os.path.dirname(input_file.name)

    output_dir = '%s/%s/' %(input_path, output_dir)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_file_path =  '%s/%s.OHDSI.csv' % \
      (output_dir, os.path.basename(input_file.name).replace('.csv', ''))

    output_file = open(output_file_path, 'w')

    # print the header for the output file
    output_file.write(','.join(header) + '\n')

    return (input_file_reader, output_file)

def getYearsOfBirth(demographics_file):
    years_of_birth = {}
    for line in demographics_file:
        subjid, decade_birth, year_birth, remaining = line.split(',', 3)
        years_of_birth[subjid] = year_birth

    return years_of_birth

# set all the output fields to empty string initially
def getOmopDictionary(OMOP_fields):
    OMOP_fields_dict = {}
    for field in OMOP_fields:
        OMOP_fields_dict[field] = ''
    return OMOP_fields_dict

def getEmergeFields(eMERGE_fields, line):
    eMERGE_fields_dict = {}
    for i, field in enumerate(eMERGE_fields):
        eMERGE_fields_dict[field] = line[i]
    return eMERGE_fields_dict

# check that the age is a valid float then add to year of birth
# to get the approximate date of the event
def getDate(subjid, age, years_of_birth):
    date = None
    if (re.search("^\d+(\.\d+)?", age)):
        year = int(years_of_birth[subjid]) + int(float(age))
        date = str(year) + '-01-01'
    return date

def validateNotMissing(data):
    if data == '' or data == '.':
        return False
    return True

def printLineNumber (line_number, line_limit):
    if (line_limit and line_number >= int(line_limit)):
        return False
    # print the line number of the input file (+2 for header and 0 index)
    print('\r%s' % (line_number + 1)),
    if (line_number % 100 == 99):
        sys.stdout.flush()
    return True

def printLineError(line_number, data):
    print "Invalid line:", line_number + 1, "Values:", data

def writeToOutputFile(OMOP_fields, OMOP_fields_dict, output_file):
    output = []
    for field in OMOP_fields:
        output.append(OMOP_fields_dict[field])

    try:
        output_file.write(','.join(output) + '\n')
    except:
        printLineError(i, output)
