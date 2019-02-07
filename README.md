Python scripts used to convert eMERGE network CSV files to
files that can be imported into an OMOP Common Data Model (OHDSI) database.

Obtain the eMERGE CSV's from the eMERGE network coordinating center.

```
PATH="< path to files here! >"

python demographics_to_OHDSI_person.py \
  $PATH/EMERGESEQ_DEMO.csv

python meds_to_OHDSI_drugs.py \
  -d $PATH/EMERGESEQ_DEMO.csv \
  $PATH/EMERGESEQ_MEDS.csv \

python labs_to_OHDSI_measurement.py \
  -d $PATH/EMERGESEQ_DEMO.csv \
  $PATH/EMERGESEQ_LABS.csv

python BMI_to_OHDSI_measurement.py \
  -d $PATH/EMERGESEQ_DEMO.csv \
  $PATH/EMERGESEQ_BMI.csv

python CPT_to_OHDSI_procedures.py \
  -d $PATH/EMERGESEQ_DEMO.csv \
  $PATH/EMERGESEQ_CPT.csv.test

python ICD_to_OHDSI_condition_occurence.py \
  -d $PATH/EMERGESEQ_DEMO.csv \
  $PATH/EMERGESEQ_ICD.csv.test

```
