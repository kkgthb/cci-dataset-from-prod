BEGIN TRANSACTION;
CREATE TABLE "sqlt_Account" (
    sqlt___dataload_row_key VARCHAR(255) UNIQUE NOT NULL,
    "sqlt___hed__School_Code__c" VARCHAR(255) UNIQUE NOT NULL,
    "sqlt___Name" VARCHAR(255) NOT NULL,
    PRIMARY KEY (sqlt___dataload_row_key)
);
INSERT INTO "sqlt_Account" (sqlt___dataload_row_key, "sqlt___hed__School_Code__c", "sqlt___Name") VALUES("ac_co_columbia", "ac_co_columbia", "Columbia University");
INSERT INTO "sqlt_Account" (sqlt___dataload_row_key, "sqlt___hed__School_Code__c", "sqlt___Name") VALUES("ac_co_barnard", "ac_co_barnard", "Barnard College");
COMMIT;