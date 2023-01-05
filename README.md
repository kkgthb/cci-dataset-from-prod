## Work in progress

Do not bother trying to figure out what this repo is for.  It's not done yet.

## Ideas of "validation tables":

- EDA `Account` where `RecordType.DeveloperName` is `Educational_Institution` _(unique external nonrequired ID = `Account.hed__School_Code__c`)_ _(referenced by `hed__Education_History__c.Account__c`)_ _(not sure which record type, but another record type is referenced by `hed__Application__c.hed__Applying_To__c`)_
- `hed__Term__c` _(referenced by `hed__Application__c.hed__Term__c`)_
- `hed__Language__c` _(referenced by `Contact_Language__c.Language__c`)_
- `summit__Summit_Events__c`
- `summit__Summit_Events_Instance__c`
- EASY `Application_Control__c` _(referenced by EASY `Requirement__c.Application_Control__c` and EASY `Application__c.Application_Control__c`)_
- EASY `Requirement__c` _(referenced by EASY `Requirement_Item__c.Requirement__c`)_
- EASY `Requirement_Item__c` _(referenced by EASY `Question__c.Requirement_Item__c`)_
- EASY `Question__c` _(referenced by EASY `Question_Response__c.Question__c`)_

## Commands

```sh
sfdx sfdmu:run --sourceusername cci-dataset-from-prod-demo__feature --targetusername csvfile --path sfdmu-play
```

```sh
cci task run snowfakery --recipe fakes/snowfake.yml --org feature
```

```sh
cci task run load_dataset -o mapping ccidataplay/mp.yml -o sql_path ccidataplay/dt.sql --org feature
```

```sh
cci task run try_a_python --org feature
```

## SFDMU config

Here is an example `export.json` that mostly ignores lookup fields _(`lookup_false`)_ unless they've been deemed important _(don't forget to define their `externalId` elsewhere in `export.json`)_:

```json
{
    "objects": [
        {
            "operation": "Readonly",
            "externalId": "hed__School_Code__c, Name",
            "query": "SELECT updateable_true, lookup_false, hed__Current_Address__c, RecordType.DeveloperName FROM Account",
            "excludedFields": "IsPartner, IsCustomerPortal, CleanStatus, hed__Billing_Address_Inactive__c"
        }
    ]
}
```

## Thoughts

1. I get that my goal is to use the handwritten Python to parse SFDMU files into `mp.yml` and parts of `loadme.sql`.
2. But with what, exactly, am I going to generate the **field datatypes** in `loadme.sql`?
    * Am I going to use some sort of variation on the code found in https://github.com/kkgthb/download-salesforce-objects-and-fields-as-json ?
    * Am I going to admit that this command is pretty darned good at the field type inference and do some sort of back-and-forth between running SFDMU, running custom Python to generate `mp.yml` off the SFDMU, running this command to parse the `mp.yml` into a `.sql`, and then running custom Python to tear the `.sql` to shreds, keeping just greatest hits from the `CREATE TABLE` statements?
        ```sh
        cci task run extract_dataset -o mapping ccidataplay/mp.yml -o sql_path ccidataplay/extracted.sql --org feature
        ```