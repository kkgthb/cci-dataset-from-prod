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
            csv_filepath = os.path.abspath(os.path.join(sfdmu_play_folder, f'{object_api_name}.csv'))
            self.logger.info(csv_filepath)