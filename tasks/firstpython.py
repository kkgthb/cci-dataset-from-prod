from cumulusci.tasks.salesforce import BaseSalesforceApiTask
import os
import csv

this_python_codebase_path = os.path.realpath(os.path.dirname(__file__))
up_one_folder = os.path.abspath(os.path.join(this_python_codebase_path, '..'))
sfdmu_play_folder = os.path.abspath(os.path.join(up_one_folder, 'sfdmu-play'))
sfdmu_objects_of_interest = ['Account']

class YayForPython(BaseSalesforceApiTask):
    # _run_task function declaration makes this code runnable with a "cci task run" command
    def _run_task(self):
        # "self.sf" & "self.org_config" represent org-login state that the "cci task run" context knows.
        # "self.options" is a dict-like data structure of details you put into your "cumulusci.yml" file.
        self.logger.info('Hello world')
        for object_api_name in sfdmu_objects_of_interest:
            csv_file_path = os.path.abspath(os.path.join(sfdmu_play_folder, 'target', f'{object_api_name}_readonly_target.csv'))
            with open(csv_file_path) as csv_file_handle:
                csvreader = csv.DictReader(csv_file_handle)
                #print(csvreader.fieldnames) # DEBUG LINE ONLY
                for row in csvreader:
                    print()
                    for field_api_name, cell_value in row.items():
                        if field_api_name in ['Id', 'RecordTypeId']:
                            continue # We don't care about org-specific field values.
                        if '$' in field_api_name:
                            continue # Dollar-sign columns are clutter from SFDMU.
                        if cell_value is None or cell_value == '':
                            continue # We don't care about blank cells.
                        #if '.' in field_api_name: # DEBUG LINE ONLY
                        #    print('Next line has a period in it') # DEBUG LINE ONLY -- we want to handle these a special way TBD.
                        print(field_api_name, cell_value) # DEBUG LINE ONLY
