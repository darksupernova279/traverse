''' A database helper module to hold functions or classes that interact and manage databases in SQL, or SQLLite etc. All database related
    actions are stored here. There are classes for each type of database connection, like Postgre, or SqlLite. There is also a class called
    DatabaseOps which is realted to generic database methods that can be used universally '''

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
            server = SSHTunnelForwarder(ssh_address_or_host=(conn_info.ssh_host, conn_info.ssh_port)
                                        , ssh_username=conn_info.ssh_user
                                        , ssh_pkey=conn_info.ssh_key
                                        , remote_bind_address=(conn_info.db_host, conn_info.db_port))
            server.start()
            conn_info.db_host = '127.0.0.1'
            conn_info.db_port = server.local_bind_port
            return_obj = func(conn_info, *args)
            server.close()
            return return_obj
        else:
            return func(conn_info, *args)

    return wrapper


def ssh_control_postgre(func):
    def wrapper(conn_info, *args):
        if conn_info.use_ssh is True:
            try:
                server = SSHTunnelForwarder(ssh_address_or_host=(conn_info.ssh_host, conn_info.ssh_port)
                                            , ssh_username=conn_info.ssh_user
                                            , ssh_pkey=conn_info.ssh_key
                                            , remote_bind_address=(conn_info.db_host, int(conn_info.db_port)))
                server.start()
                conn_info.db_host = '127.0.0.1'
                conn_info.db_port = server.local_bind_port
                return_obj = func(conn_info, *args)
                server.close()
                return return_obj
            except Exception:
                raise
        else:
            return func(conn_info, *args)

    return wrapper


class DatabaseConnInfo:
    ''' This is a helper class to make database connection info standard for connections. '''
    def __init__(self, ssh_key_path=None):
        self.db_name = None
        self.db_host = None
        self.db_port = None
        self.db_username = None
        self.db_password = None
        self.use_ssh = False
        self.ssh_host = None
        self.ssh_port = 22
        self.ssh_user = None
        if ssh_key_path is not None:
            self.ssh_key = paramiko.RSAKey.from_private_key_file(ssh_key_path)


class DatabaseOps:
    ''' Generic operations used for databases. '''

    @staticmethod
    def replace_script_tokens(db_script, **tokens_n_values):
        ''' Pass in a list of key value pairs, with keys being the token and the value being the replacement for the token. '''
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
    def connect_to_db(db_conn_info):
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
    def execute_query(conn_info, script):
        ''' Pass in the connection object(class) and the script to be executed. This method does not retrieve any results. '''
        conn = MySql.connect_to_db(conn_info)
        cursor = conn.cursor()
        cursor.execute(script)
        conn.commit()
        return True

    @staticmethod
    @ssh_control_mysql
    def execute_queries(conn_info, script_list):
        ''' Pass in the connection object(class) and the list of scripts to be executed. This method does not retrieve any results. '''
        conn = MySql.connect_to_db(conn_info)
        cursor = conn.cursor()
        for script in script_list:
            cursor.execute(script)
            conn.commit()
        return True

    @staticmethod
    @ssh_control_mysql
    def execute_query_return_results(conn_info, script):
        ''' Pass in the connection object(class) and the script to be executed. This method retrieves all results from the query. '''
        conn = MySql.connect_to_db(conn_info)
        cursor = conn.cursor()
        cursor.execute(script)
        raw_results = cursor.fetchall()
        if raw_results is []:
            raise DatabaseReturnedNothingError
        else:
            return raw_results


class PostGre:
    ''' All methods related to PostGre SQL are stored here. '''

    @staticmethod
    def connect_to_db(conn_info):
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
    def execute_query(conn_info, script):
        ''' Pass in the connection object(class) and the script to be executed. This method does not retrieve any results. '''
        conn = PostGre.connect_to_db(conn_info)
        cursor = conn.cursor()
        cursor.execute(script)
        conn.close()
        return True


    @staticmethod
    @ssh_control_postgre
    def execute_query_return_results(conn_info, script):
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
