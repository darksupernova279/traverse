''' A database helper module to hold functions or classes that interact and manage databases in SQL, or SQLLite etc. All database related
    actions are stored here. There are classes for each type of database connection, like Postgre, or SqlLite. There is also a class called
    DatabaseOps which is realted to generic database methods that can be used universally '''

import sqlite3
import psycopg2
import paramiko
from sshtunnel  import SSHTunnelForwarder
from mysql.connector    import Connect as MySqlConnect

def retry(fn):
    retry_limit = 3
    attempt = 0
    while True:
        if attempt <= retry_limit:
            try:
                fn()
            except Exception as err:
                attempt = attempt + 1
                print(f'Tried connecting to DB but got this error: {err}')
        else:
            raise Exception('Unable to connect to Database. See console logs.')


class DatabaseConnInfo:
    ''' This is a helper class to make database connection info standard for connections. '''
    def __init__(self, ssh_key_path=None):
        self.db_name = None
        self.db_host = None
        self.db_port = None
        self.db_username = None
        self.db_password = None
        self.ssh_host = None
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
    @retry
    def connect_to_db(db_conn_info, use_ssh=0):
        ''' Pass in a username and password for the credentials of your MySQL database, along with the host and database name.
            The connection is returned. '''
        if use_ssh == 1:
            with SSHTunnelForwarder(
                    ssh_address_or_host=db_conn_info.ssh_host
                    , ssh_username=db_conn_info.ssh_user
                    , ssh_pkey=db_conn_info.ssh_key
                    , remote_bind_address=(db_conn_info.db_host, db_conn_info.db_port)
            ) as _:
                return MySqlConnect(user=db_conn_info.db_username, password=db_conn_info.db_password,
                                                host=db_conn_info.db_host, database=db_conn_info.db_name, port=db_conn_info.db_port)
        else:
            return MySqlConnect(user=db_conn_info.db_username, password=db_conn_info.db_password,
                                            host=db_conn_info.db_host, database=db_conn_info.db_name, port=db_conn_info.db_port)



    @staticmethod
    def execute_query(conn, script):
        ''' Pass in the connection and the script to be executed. This method does not retrieve any results. '''
        cursor = conn.cursor()
        cursor.execute(script)
        conn.commit()
        return True


    @staticmethod
    def execute_query_return_results(conn, script):
        ''' Pass in the connection and the script to be executed. This method retrieves all results from the query. '''
        cursor = conn.cursor()
        cursor.execute(script)
        return cursor.fetchall()


class PostGre:
    ''' All methods related to PostGre SQL are stored here. '''

    @staticmethod
    @retry
    def connect_to_db(db_conn_info, use_ssh=0):
        ''' Pass in the connection string for the PostGre DB you wish to connect to.
            Example: dbname=test host=redshift-fake-2-me.blahblah.location.redshift.amazonaws.com port=1234 user=root password=mysecret '''
        conn_str = f'''dbname={db_conn_info.db_name}
                         host={db_conn_info.db_host}
                         port={db_conn_info.db_port}
                         user={db_conn_info.db_username}
                         password={db_conn_info.db_password}'''
        if use_ssh == 0:
            return psycopg2.connect(conn_str)
        else:
            with SSHTunnelForwarder(
                    ssh_address_or_host=db_conn_info.ssh_host
                    , ssh_username=db_conn_info.ssh_user
                    , ssh_pkey=db_conn_info.ssh_key
                    , remote_bind_address=(db_conn_info.db_host, int(db_conn_info.db_port))
            ) as _:
                return psycopg2.connect(conn_str)


    @staticmethod
    def execute_query(conn, script):
        ''' Pass in the connection and the script to be executed. This method does not retrieve any results. '''
        cursor = conn.cursor()
        cursor.execute(script)
        conn.close()
        return True


    @staticmethod
    def execute_query_return_results(conn, script):
        ''' Pass in the connection and the script to be executed. This method retrieves all results from the query. '''
        cursor = conn.cursor()
        cursor.execute(script)
        results = cursor.fetchall()
        conn.close()
        return results
