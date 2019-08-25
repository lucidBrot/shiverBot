#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
# any python3 version should work

import mysql.connector
import yaml # pyYaml
import os
import sys # for ui only

# config files
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SECRET_CONFIG_FILE = os.path.join(SCRIPT_DIR, './secret_config.yml')

def load_config():
    """
    loads config from SECRET_CONFIG_FILE into global variables
    """
    global DB_USER, DB_PASS, DB_HOST, DB_NAME, DB_TABLE
    with open(SECRET_CONFIG_FILE) as f:
        secret_config = yaml.safe_load(f)
        query_config = secret_config['queryconfig']
    DB_USER = query_config['dbuser']
    DB_PASS = query_config['dbpass']
    DB_HOST = query_config['dbhost']
    DB_NAME = query_config['dbname']
    DB_TABLE = query_config['table1']

def connect_if_required():
    global CONNECTION
    
    if 'DB_USER' not in globals():
        load_config()
    
    if 'CONNECTION' in globals() \
    and CONNECTION is not None \
    and CONNECTION.is_connected():
        return
    else:
        CONNECTION = mysql.connector.connect(
            user=DB_USER,
            password=DB_PASS,
            host=DB_HOST,
            database=DB_NAME,
            converter_class=MyConverter,
            )

def query_by_email(email, limit = 50):
    # always recreate connection because we do not know how long it would stay around unused otherwise
    connect_if_required()
    try:
        cursor = CONNECTION.cursor()
        cursor.execute("""
            select email, pass from {table} where email = %s limit %s;
        """.format(table=DB_TABLE),
            (email, limit) # %s and tuple makes execute sanitize inputs
        )
        result = cursor.fetchall()
        return result
    finally:
        CONNECTION.close()

# converter class because mysql returns bytestrings instead of unicode/utf-8
# to remove this class again, remove the converter in the connection
class MyConverter(mysql.connector.conversion.MySQLConverter):

    def row_to_python(self, row, fields):
        row = super(MyConverter, self).row_to_python(row, fields)

        def to_unicode(col):
            if type(col) == bytearray:
                return col.decode('utf-8')
            return col

        return[to_unicode(col) for col in row]

if __name__ == "__main__":
    print(query_by_email(sys.argv[1]))
