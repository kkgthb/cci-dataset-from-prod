from cumulusci.tasks.salesforce import BaseSalesforceApiTask
import os
import csv
import sqlite3
from collections import OrderedDict

this_python_codebase_path = os.path.realpath(os.path.dirname(__file__))
up_one_folder = os.path.abspath(os.path.join(this_python_codebase_path, '..'))
sfdmu_play_folder = os.path.abspath(os.path.join(up_one_folder, 'sfdmu-play'))
sfdmu_objects_of_interest = {'Account': {
    'object_api_name': 'Account', 'upsert_mapping_key_api_name': 'hed__School_Code__c'}}
cci_play_folder = os.path.abspath(os.path.join(up_one_folder, 'ccidataplay'))


class YayForPython(BaseSalesforceApiTask):

    def __create_data_table(self, obj_api_name, obj_detls, dest_cur):
        def __generate_field(f_api_nm, f_dtls):
            create_field_script = f'"{f_api_nm}" ' + f_dtls.get('sqlite_data_type')
            if f_dtls.get('unique_constraint') == True:
                create_field_script += ' UNIQUE'
            if f_dtls.get('not_null_constraint') == True:
                create_field_script += ' NOT NULL'
            return create_field_script
        obj_primary_key = obj_detls['upsert_mapping_key_api_name']
        create_table_fields_scriptlets = []
        # First do primary key field
        create_table_fields_scriptlets.append(__generate_field(f_api_nm=obj_primary_key, f_dtls=obj_detls['mapping_field_api_names'][obj_primary_key]))
        # Then do the rest of the fields
        [create_table_fields_scriptlets.append(__generate_field(f_api_nm=field_api_name, f_dtls=field_details)) for field_api_name, field_details in obj_detls['mapping_field_api_names'].items() if field_api_name not in [obj_primary_key]]
        create_table_fields_scriptlets.append(f'PRIMARY KEY ("{obj_primary_key}")')
        create_table_sql = f'CREATE TABLE "{obj_api_name}" (' + '\n\t' + ( '\n\t, '.join(create_table_fields_scriptlets) ) + '\n);'
        dest_cur.executescript(create_table_sql)
        for row_handle, row_fields in obj_detls['table_data'].items():
            ordered_row_fields = OrderedDict(row_fields)
            ordered_row_fields.move_to_end(obj_primary_key, last=False)
            comma_separated_field_api_names = ', '.join(ordered_row_fields.keys())
            comma_separated_cell_values = ', '.join([(f"'{v}'" if ( 'VARCHAR' in obj_detls['mapping_field_api_names'][k]['sqlite_data_type'] ) else v) for k,v in ordered_row_fields.items()])
            insert_record_script = f'''INSERT INTO "{obj_api_name}" 
                ({comma_separated_field_api_names}) 
                VALUES 
                ({comma_separated_cell_values})
            ;
            '''
            dest_cur.executescript(insert_record_script)

    def __create_record_type_table(self, obj_api_name, record_type_developer_names_set, dest_cur):
        create_table_script = f'''CREATE TABLE "{obj_api_name}_rt_mapping" (
	        record_type_id VARCHAR(18) UNIQUE NOT NULL, 
	        developer_name VARCHAR(255) UNIQUE NOT NULL, 
	        PRIMARY KEY (record_type_id)
        );
        '''
        dest_cur.executescript(create_table_script)
        for record_type_developer_name in record_type_developer_names_set:
            insert_record_script = f'''INSERT INTO "{obj_api_name}_rt_mapping" 
                (record_type_id, developer_name) 
                VALUES 
                ('{record_type_developer_name}','{record_type_developer_name}');
            '''
            dest_cur.executescript(insert_record_script)

    def __make_new_sqlite(self, dest_db_conn, dest_db_cur):
        for object_api_name, object_detail_holder in sfdmu_objects_of_interest.items():
            if 'record_type_developer_names' in object_detail_holder:
                self.__create_record_type_table(
                    obj_api_name=object_api_name, record_type_developer_names_set=object_detail_holder['record_type_developer_names'], dest_cur=dest_db_cur)
            self.__create_data_table(obj_api_name=object_api_name,
                    obj_detls=object_detail_holder, dest_cur=dest_db_cur)

    def __process_sqlite_table(self, source_cur, sq_object_api_name):
        for row in source_cur.execute(f"PRAGMA table_info('sqlt_{sq_object_api_name}')"):
            # 6-item tuple:  https://renenyffenegger.ch/notes/development/databases/SQLite/sql/pragma/table_info
            # [0] = autoincrementing row number.  [1] = SQLITE column name.
            # [2] = SQLITE column data type.  [3] = 1/0 indicating whether flagged "not null."
            # [4] = Default value for the column.  [5] = 0/# indicating column's position in a primary key constraint (0 if not involved).
            sqlite_column_name = row[1]
            if sqlite_column_name == 'id':
                continue  # We don't care about CCI's idea of a great ID column
            field_api_name = sqlite_column_name.split('sqlt___')[-1]
            if field_api_name in sfdmu_objects_of_interest[sq_object_api_name]['mapping_field_api_names']:
                sfdmu_objects_of_interest[sq_object_api_name]['mapping_field_api_names'][field_api_name]['sqlite_data_type'] = row[2]

    def __process_csv_row_kvpair(self, field_api_name, cell_value, fd_object_api_name, mapping_field_api_name_collector, record_type_developer_name_collector, row_data_collector, row_pk_val):
        obj_pk_api_name = sfdmu_objects_of_interest[fd_object_api_name]['upsert_mapping_key_api_name']
        if field_api_name in ['Id', 'RecordTypeId']:
            return  # We don't care about org-specific field values.
        if '$' in field_api_name:
            return  # Dollar-sign columns are clutter from SFDMU.
        if cell_value is None or cell_value == '':
            return  # We don't care about blank cells.
        # if '.' in field_api_name: # DEBUG LINE ONLY
        #    print('Next line has a period in it') # DEBUG LINE ONLY -- we want to handle these a special way TBD.
        if '.' not in field_api_name and field_api_name not in mapping_field_api_name_collector:
            mapping_field_api_name_collector[field_api_name] = {
                'field_api_name': field_api_name}
            row_data_collector[field_api_name] = cell_value
        if field_api_name in ['Name', obj_pk_api_name]:
            mapping_field_api_name_collector[field_api_name]['not_null_constraint'] = True
        if field_api_name == obj_pk_api_name:
            mapping_field_api_name_collector[field_api_name]['unique_constraint'] = True
        if field_api_name == 'RecordType.DeveloperName' and 'RecordTypeId' not in mapping_field_api_name_collector:
            mapping_field_api_name_collector['RecordTypeId'] = {
                'field_api_name': 'RecordTypeId', 'not_null_constraint': True}
            record_type_developer_name_collector.add(cell_value)
            row_data_collector['RecordTypeId'] = cell_value
        # print(field_api_name, cell_value) # DEBUG LINE ONLY

    def __process_csv_row(self, csv_row, rw_object_api_name, table_data_collector):
        worthy_mapping_field_api_names = {}
        worthy_record_type_developer_names = set()
        csv_rw_data_collector = {}
        object_primary_key_api_name = sfdmu_objects_of_interest[
            rw_object_api_name]['upsert_mapping_key_api_name']
        row_pk_value = csv_row[object_primary_key_api_name]
        # Skip rows that do not yet have proper PK data.
        # (TODO:  Use SFDMU transformations to make sure bad prod data DOES have proper PK data.)
        if row_pk_value is None or row_pk_value == '':
            return
        # Process cells of row
        [self.__process_csv_row_kvpair(k, v, rw_object_api_name, worthy_mapping_field_api_names,
                                       worthy_record_type_developer_names, csv_rw_data_collector, row_pk_value) for k, v in csv_row.items()]
        # Propagate field API names upward from collector
        sfdmu_objects_of_interest[rw_object_api_name]['mapping_field_api_names'] = worthy_mapping_field_api_names
        # Propagate record types upward from collector
        if len(worthy_record_type_developer_names) > 0:
            sfdmu_objects_of_interest[rw_object_api_name]['record_type_developer_names'] = worthy_record_type_developer_names
        # Propagate row cell values upward from collector
        table_data_collector[row_pk_value] = csv_rw_data_collector

    def __process_csv_reader(self, csv_reader, rd_object_api_name):
        csv_table_data_collector = {}
        # print(csvreader.fieldnames) # DEBUG LINE ONLY
        # Process rows
        [self.__process_csv_row(row, rd_object_api_name,
                                csv_table_data_collector) for row in csv_reader]
        # Propagate table cell values upward from collector
        sfdmu_objects_of_interest[rd_object_api_name]['table_data'] = csv_table_data_collector

    # _run_task function declaration makes this code runnable with a "cci task run" command
    def _run_task(self):
        # "self.sf" & "self.org_config" represent org-login state that the "cci task run" context knows.
        # "self.options" is a dict-like data structure of details you put into your "cumulusci.yml" file.
        self.logger.info('Hello world')
        # TODO:  Run SFDMU
        # Parse SFDMU output into memory
        for object_api_name in sfdmu_objects_of_interest.keys():
            csv_file_path = os.path.abspath(os.path.join(
                sfdmu_play_folder, 'target', f'{object_api_name}_readonly_target.csv'))
            with open(csv_file_path) as csv_file_handle:
                self.__process_csv_reader(csv.DictReader(
                    csv_file_handle), object_api_name)
        # TODO:  Write out a mapping and run CCI extract to "db.db"
        # Parse "db.db" into memory
        source_db_connection_object = sqlite3.connect(
            os.path.abspath(os.path.join(cci_play_folder, 'db.db')))
        source_db_cursor_object = source_db_connection_object.cursor()
        for object_api_name in sfdmu_objects_of_interest.keys():
            self.__process_sqlite_table(
                source_db_cursor_object, object_api_name)
        source_db_connection_object.close()
        self.logger.info(sfdmu_objects_of_interest)
        # Handmake a new SQLite DB from memory
        dest_db_path = os.path.abspath(os.path.join(
            cci_play_folder, 'output.db'))
        if os.path.exists(dest_db_path):
            os.remove(dest_db_path)
        dest_db_connection_object = sqlite3.connect(dest_db_path)
        dest_db_cursor_object = dest_db_connection_object.cursor()
        self.__make_new_sqlite(dest_db_connection_object,
                               dest_db_cursor_object)
        # Extra-fancy:  write new SQLite DB to SQL file
        with open(os.path.abspath(os.path.join(
                cci_play_folder, 'test.sql')), 'w') as f:
            for line in dest_db_connection_object.iterdump():
                f.write('%s\n' % line)
        dest_db_connection_object.close()
