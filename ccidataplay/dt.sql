BEGIN TRANSACTION;
CREATE TABLE "sqlt_Account" (
    "sqlt___hed__School_Code__c" VARCHAR(255) UNIQUE NOT NULL,
    "sqlt___Name" VARCHAR(255) NOT NULL,
    "sqlt___RecordTypeId" VARCHAR(255) NOT NULL,
    PRIMARY KEY ("sqlt___hed__School_Code__c")
);
INSERT INTO "sqlt_Account" ("sqlt___hed__School_Code__c", "sqlt___Name", "sqlt___RecordTypeId") VALUES("ac_co_columbia", "Columbia University", "Educational_Institution");
INSERT INTO "sqlt_Account" ("sqlt___hed__School_Code__c", "sqlt___Name", "sqlt___RecordTypeId") VALUES("ac_co_barnard", "Barnard College", "Educational_Institution");
CREATE TABLE "Account_rt_mapping" (
	record_type_id VARCHAR(18) NOT NULL, 
	developer_name VARCHAR(255), 
	PRIMARY KEY (record_type_id)
);
INSERT INTO "Account_rt_mapping" (record_type_id, developer_name) VALUES('Educational_Institution','Educational_Institution');
COMMIT;