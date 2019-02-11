-- *************************************************************************
-- ** SQL statements for creating the OHDSI tables
-- *************************************************************************

-- see notes at bottom for statements to create the OHDSI tables

-- ** Import data into the SQL database ** --
declare @import_path varchar(1024) = '< import file path here >'

-- Demographics (person table)
declare @table varchar(255) = 'emerge_network_person';
declare @import_fie varchar(255) = 'EMERGESEQ_DEMO.OHDSI.csv';

declare @import_file_path varchar(1024) = ''''+ @import_path + @import_file +'''';
exec ('TRUNCATE table ' + @table);
exec ('BULK INSERT ' + @table +
     ' FROM ' + @import_file_path +
     ' WITH (FIELDTERMINATOR = '','', ROWTERMINATOR = ''0x0a'', firstrow = 2);');

-- Redo the above exec statements for these tables! --

-- CPT (procedures)
declare @table varchar(255) = 'emerge_network_procedure_occurrence';
declare @import_fie varchar(255) = 'EMERGESEQ_CPT.OHDSI.csv';

--  Meds (drugs)
declare @table varchar(255) = 'emerge_network_drug_exposure';
declare @import_fie varchar(255) = 'EMERGESEQ_MEDS.OHDSI.csv';

-- ICD (conditions)
declare @table varchar(255) = 'emerge_network_condition_occurrence';
declare @import_fie varchar(255) = 'EMERGESEQ_ICD.OHDSI.csv';

-- Labs (measurement)
declare @table varchar(255) = 'emerge_network_measurement';
declare @import_fie varchar(255) = 'EMERGESEQ_LABS.OHDSI.csv';
declare @import_fie varchar(255) = 'EMERGESEQ_BMI.OHDSI.csv';





-- ** Notes ** --
-- For Meds (drug_exposure table), the RxNorm value is the [concept_code]
-- in the concepts table.
-- So the concepts IDs for the drugs can be obtained:
SELECT [concept_code],[concept_id],[concept_name]
FROM [ohdsi_west_cumc_20180326].[dbo].[concept]
WHERE concept_code IN (
  '221072', '301542', '36567', '41127', '42463', '6472', '83367', '861634'
)
AND concept_name LIKE '%statin%'


-- @todo replace this with proper create statements
-- create all the OHDSI tables based on an existing OHDSI database
-- this is MSSQL specific
SELECT top(0) *
  into emerge_shared_20180326.dbo.emerge_network_person
  FROM [person];
SELECT top(0) *
  into emerge_shared_20180326.dbo.emerge_network_drug_exposure
  FROM [drug_exposure];
SELECT top(0) *
  into emerge_shared_20180326.dbo.emerge_network_measurement
  FROM [measurement];
SELECT top(0) *
  into emerge_shared_20180326.dbo.emerge_network_procedure_occurence
  FROM [procedure_occurence];
SELECT top(0) *
  into emerge_shared_20180326.dbo.emerge_network_condition_occurrence
  FROM [condition_occurrence];
