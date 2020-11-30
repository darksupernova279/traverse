''' A database helper module to hold functions or classes that interact and manage databases in SQL, or SQLLite etc. All database related
    actions are stored here. There are classes for each type of database connection, like Postgre, or SqlLite. There is also a class called
    DatabaseOps which is realted to generic database methods that can be used universally '''

import sqlite3


class DatabaseOps:
    ''' Generic operations used for databases. '''

    @staticmethod
    def replace_script_tokens(db_script, **tokens_n_values):
        ''' Pass in a list of key value pairs, with keys being the token and the value being the replacement for the token. '''
        for key, value in tokens_n_values.items():
            db_script = db_script.replace(key, value)

        return db_script

class SqlLite3:
    ''' SQL Lite 3 database methods. '''

    @staticmethod
    def create_in_mem_database():
        ''' Creates a connection to a database in memory, currently using SQL3 Lite. Returns the connection.'''
        conn = sqlite3.connect(':memory:')
        return conn


    @staticmethod
    def execute_script(conn, script):
        ''' Pass in the connection and the script to be executed. This method does not retrieve any results. '''
        conn.execute(script)
        return True


    @staticmethod
    def execute_script_get_all_results(conn, script):
        ''' Pass in the connection and the script to be executed. This method does not retrieve any results. '''
        cursor = conn.execute(script)
        rows = cursor.fetchall()
        return rows
