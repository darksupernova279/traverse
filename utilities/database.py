''' A database helper module to hold functions or classes that interact and manage databases in SQL, or SQLLite etc. All database related
    actions are stored here. There are classes for each type of database connection, like Postgre, or SqlLite. There is also a class called
    DatabaseOps which is realted to generic database methods that can be used universally '''

from typing import List
import warnings
import time
import sqlite3
import psycopg2
import paramiko
from sshtunnel          import SSHTunnelForwarder
from mysql.connector    import Connect as MySqlConnect


class DatabaseReturnedNothingError(Exception):
    ''' This exception is when we query the database and no results are returned. '''
    def __init__(self):
        self.err_msg = 'No results returned from the database.'
        super().__init__(self.err_msg)


def ssh_control_mysql(func):
    def wrapper(conn_info, *args):
        if conn_info.use_ssh is True:
            if conn_info.ssh_local_bind_port > 0:
                conn_info.db_host = conn_info.original_db_host
                conn_info.db_port = conn_info.original_db_port
            else:
                conn_info.original_db_host = conn_info.db_host
                conn_info.original_db_port = conn_info.db_port

            with SSHTunnelForwarder(ssh_address_or_host=(conn_info.ssh_host, conn_info.ssh_port)
                                    , ssh_username=conn_info.ssh_user
                                    , ssh_pkey=conn_info.ssh_key
                                    , remote_bind_address=(conn_info.db_host, conn_info.db_port)
            ) as tunnel:
                conn_info.db_host = '127.0.0.1'
                conn_info.db_port = tunnel.local_bind_port
                conn_info.ssh_local_bind_port = tunnel.local_bind_port
                return_obj = func(conn_info, *args)
                return return_obj
        else:
            return func(conn_info, *args)

    return wrapper


def ssh_control_postgre(func):
    def wrapper(conn_info, *args):
        if conn_info.use_ssh is True:
            if conn_info.ssh_local_bind_port > 0:
                conn_info.db_host = conn_info.original_db_host
                conn_info.db_port = conn_info.original_db_port
            else:
                conn_info.original_db_host = conn_info.db_host
                conn_info.original_db_port = conn_info.db_port

            with SSHTunnelForwarder(ssh_address_or_host=(conn_info.ssh_host, conn_info.ssh_port)
                                    , ssh_username=conn_info.ssh_user
                                    , ssh_pkey=conn_info.ssh_key
                                    , remote_bind_address=(conn_info.db_host, int(conn_info.db_port))
            ) as tunnel:
                conn_info.db_host = '127.0.0.1'
                conn_info.db_port = tunnel.local_bind_port
                conn_info.ssh_local_bind_port = tunnel.local_bind_port
                return_obj = func(conn_info, *args)
                return return_obj
        else:
            return func(conn_info, *args)

    return wrapper


class DatabaseConnInfo:
    ''' This is a helper class to make database connection info standard for connections. '''
    def __init__(self, ssh_key_path=None):
        self.db_name = None
        self.db_host = None
        self.db_port = 0
        self.db_username = None
        self.db_password = None
        self.use_ssh = False
        self.ssh_host = None
        self.ssh_port = 0
        self.ssh_user = None
        self.ssh_local_bind_port = 0
        self.original_db_host = '' # Not used outside of this. Internal tracking purposes
        self.original_db_port = 0 # Not used outside of this. Internal tracking purposes
        if ssh_key_path is not None:
            self.ssh_key = paramiko.RSAKey.from_private_key_file(ssh_key_path)


class DatabaseOps:
    ''' Generic operations used for databases. '''

    @staticmethod
    def replace_script_tokens(db_script, **tokens_n_values):
        '''
            Pass in a list of key value pairs, this is parameters and their values as per pythons kwargs,
            with keys being the token and the value being the replacement for the token.
        '''
        for key, value in tokens_n_values.items():
            db_script = db_script.replace(key, value)

        return db_script

    @staticmethod
    def convert_sql_results_to_list(raw_results):
        ''' Pass in your raw results and it retuns a list of every row in that column. Ensure to only pass one column in. '''
        result_list = []
        for res in raw_results:
            result_list.append(res[0])

        return result_list

    @staticmethod
    def load_sql_file_with_tokens(file_path, identifier=None, **tokens_n_values):
        '''
            Pass in the full path to the sql file then a dictionary of tokens and their values. Returns the sql file with tokens replaced.
            If you use an identifier for your tokens then pass in the identifier you use, for example $$user_id$$ where the $ signs are the
            identifier, you must pass in '$$' so it is added to the start and end of the token value. Or leave blank and no identifier is assumed.
        '''
        file = open(file_path, 'r')
        sql = file.read()
        file.close()

        for key, value in tokens_n_values.items():
            if identifier is not None:
                sql = sql.replace(f'{identifier}{key}{identifier}', str(value))
            else:
                sql = sql.replace(key, value)

        return sql

    @staticmethod
    def load_sql_file(file_path):
        ''' Pass in the full path to the sql file and this method returns the sql script as a string. '''
        file = open(file_path, 'r')
        sql = file.read()
        file.close()
        return sql


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


class MySql:
    ''' All methods related to MySQL are stored in this class. '''

    @staticmethod
    def connect_to_db(db_conn_info: DatabaseConnInfo):
        ''' Pass in the connection object(class) for this module and it returns a connection. '''
        attempt = 0
        retry_limit = 3
        delay = 2
        while True:
            if attempt <= retry_limit:
                try:
                    return MySqlConnect(user=db_conn_info.db_username
                        , password=db_conn_info.db_password
                        , host=db_conn_info.db_host
                        , database=db_conn_info.db_name
                        , port=db_conn_info.db_port
                        , connect_timeout=60)

                except Exception as err:
                    attempt = attempt + 1
                    warnings.warn(f'Tried connecting to DB but got this error: {err}')
                    time.sleep(delay)
            else:
                raise Exception('Unable to connect to MySQL Database. See console logs.')

    @staticmethod
    @ssh_control_mysql
    def execute_query(conn_info: DatabaseConnInfo, script):
        ''' Pass in the connection object(class) and the script to be executed. This method does not retrieve any results. '''
        conn = MySql.connect_to_db(conn_info)
        cursor = conn.cursor()
        cursor.execute(script)
        conn.commit()
        return True

    @staticmethod
    @ssh_control_mysql
    def execute_queries(conn_info: DatabaseConnInfo, script_list):
        ''' Pass in the connection object(class) and the list of scripts to be executed. This method does not retrieve any results. '''
        conn = MySql.connect_to_db(conn_info)
        cursor = conn.cursor()
        for script in script_list:
            cursor.execute(script)
            conn.commit()
        return True

    @staticmethod
    @ssh_control_mysql
    def execute_query_return_results_raw(conn_info: DatabaseConnInfo, script) -> List:
        ''' Pass in the connection object(class) and the script to be executed. This method retrieves all results from the query. '''
        conn = MySql.connect_to_db(conn_info)
        cursor = conn.cursor()
        cursor.execute(script)
        raw_results = cursor.fetchall()
        if raw_results is []:
            raise DatabaseReturnedNothingError
        else:
            return raw_results


    @staticmethod
    @ssh_control_mysql
    def execute_query_return_results(conn_info: DatabaseConnInfo, script) -> List:
        ''' Pass in the connection object(class) and the script to be executed. This method retrieves all results from the query. '''
        conn = MySql.connect_to_db(conn_info)
        cursor = conn.cursor()
        cursor.execute(script)
        raw_results = cursor.fetchall()
        if raw_results is []:
            raise DatabaseReturnedNothingError

        results_final = []
        col_names = [i[0] for i in cursor.description]

        for row in raw_results:
            new_dict = {}
            for idx, col in enumerate(row):
                new_dict[col_names[idx]] = col

            results_final.append(new_dict)

        return results_final


class PostGre:
    ''' All methods related to PostGre SQL are stored here. '''

    @staticmethod
    def connect_to_db(conn_info: DatabaseConnInfo):
        ''' Pass in the connection object(class) for this module and it returns a connection. '''
        conn_str = f'''dbname={conn_info.db_name}
                        host={conn_info.db_host}
                        port={conn_info.db_port}
                        user={conn_info.db_username}
                        password={conn_info.db_password}'''
        attempt = 0
        retry_limit = 3
        delay = 2
        while True:
            if attempt <= retry_limit:
                try:
                    return psycopg2.connect(conn_str)
                except Exception as err:
                    attempt = attempt + 1
                    warnings.warn(f'Tried connecting to DB but got this error: {err}')
                    time.sleep(delay)
            else:
                raise Exception('Unable to connect to PostGre Database. See console logs.')


    @staticmethod
    @ssh_control_postgre
    def execute_query(conn_info: DatabaseConnInfo, script):
        ''' Pass in the connection object(class) and the script to be executed. This method does not retrieve any results. '''
        conn = PostGre.connect_to_db(conn_info)
        cursor = conn.cursor()
        cursor.execute(script)
        conn.close()
        return True


    @staticmethod
    @ssh_control_postgre
    def execute_query_return_results(conn_info: DatabaseConnInfo, script):
        ''' Pass in the connection object(class) and the script to be executed. This method retrieves all results from the query. '''
        conn = PostGre.connect_to_db(conn_info)
        cursor = conn.cursor()
        cursor.execute(script)
        results = cursor.fetchall()
        if results is []:
            conn.close()
            raise DatabaseReturnedNothingError
        else:
            conn.close()
            return results
