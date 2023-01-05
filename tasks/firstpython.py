from cumulusci.tasks.salesforce import BaseSalesforceApiTask
import os

this_python_codebase_path = os.path.realpath(os.path.dirname(__file__))
up_one_folder = os.path.abspath(os.path.join(this_python_codebase_path, '..'))

class YayForPython(BaseSalesforceApiTask):
    # _run_task function declaration makes this code runnable with a "cci task run" command
    def _run_task(self):
        # "self.sf" & "self.org_config" represent org-login state that the "cci task run" context knows.
        # "self.options" is a dict-like data structure of details you put into your "cumulusci.yml" file.
        # get_org_schema() returns a Python object called "cumulusci.salesforce_api.org_schema.Schema".
        self.logger.info('Hello world')