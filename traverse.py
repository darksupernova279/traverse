''' The main file to begin execution of the automation.
It all starts with traverse.py, from this file, we pass it arguments, and it then takes care of the rest.  '''
import platform
import os
import sys
import argparse
from datetime                   import datetime
from os.path                    import realpath, dirname
from utilities.json_helper      import LoadJson
from utilities.file_helper      import FileUtils
from core.test_profiler         import Profiler
from core.test_executor         import Executor
from core.test_reporter         import Reporter
from core.core_models           import TraverseConfig


# Initiate the parser
PARSER = argparse.ArgumentParser(description='''
                                            Traverse assists in the execution of automation for web, API and database related automation.
                                            The framework is also used for production application monitoring and reporting services.
                                            ''')
PARSER.add_argument('-N'
                    , '--newtestsuite'
                    , help='''
                            Creates a new test suite given what you enter. For example if you enter fast_tests/login it will create a new directory 
                            for fast_tests if it does not exist and a new .py file called login inside the fast_tests directory. If the test suite(.py file) 
                            file exists in the directory already this will raise an error. This also can take in a 2nd parameter for the location of the 
                            'tests' folder. If the 2nd paramter is left off then the default tests folder is used in the traverse directory.
                        '''
                    , nargs='+')

PARSER.add_argument('-C'
                    , '--config'
                    , type=str
                    , help='Enter the name of the traverse config you want to use. This is required.')

PARSER.add_argument('-T'
                    , '--testrun'
                    , type=str
                    , help='Enter the name of the test run you want executed. This is required.')


# Read arguments from the CMD
ARGS = PARSER.parse_args()


# Get our root directory
CURRENT_DIR = dirname(realpath(__file__))

TEST_SUITE_FILE = """
''' This is a test module where a test class will be stored. '''
from core.core_models                       import TestDefinition, TraverseConfig
from driver.driver_interface                import DriverActions
from utilities.test_data                    import TestData


class Tests:
    ''' This test class holds test methods. The name of the class must remain exactly "Tests" for the core to pick it up. '''
    def __init__(self, traverse_config: TraverseConfig, test_definition: TestDefinition):
        self.trav_con = traverse_config
        self.test_def = test_definition
        #self.driver = DriverActions(self.test_def, '') # Add the name of your hooks file here if applicable
        self.test_data = TestData()
"""

TEST_JSON_FILE = """
{
    "testConfigurations": {
        "config1": [0]
    },
    "excludedEnvironments": ["live"]
}
"""

#############################################################
#                           Main                            #
#############################################################
if __name__ == '__main__':
    print(f'''
            Traverse is an automation framework written in Python. It initially was an idea to learn Python and automate a product at the same time
            but turned out to become a system in itself to assist making my automation easier. I am sharing this with the world in the hopes it can
            assist others to venture into automation and help build quality products. Copyright (C) {datetime.now().strftime('%Y')} Jade. R. Hancox.
            This program comes with ABSOLUTELY NO WARRANTY; This is free software, and you are welcome to redistribute it under certain conditions.
            Please see the COPYING.txt file in the root directory for license information. Note that this license applies to all source files in this
            repository with the exception of the /tests and /product directories.
        ''')

    # Create new test suite
    if ARGS.newtestsuite:
        new_list = str(ARGS.newtestsuite[0]).split('/')

        if len(new_list) < 2:
            raise Exception('Incorrect syntax for argument -N')

        if len(ARGS.newtestsuite) < 2:
            if platform.system() == 'Windows':
                TESTS_DIR = f'{CURRENT_DIR}\\tests'
            else:
                TESTS_DIR = f'{CURRENT_DIR}/tests'
        else:
            TESTS_DIR = str(ARGS.newtestsuite[1])

        test_pack = new_list[0]
        test_suite = new_list[1]

        if platform.system() == 'Windows':
            new_suite_path = f'{TESTS_DIR}\\{test_pack}\\{test_suite}.py'
            NEW_SUITE_DIR = f'{TESTS_DIR}\\{test_pack}\\'
        else:
            new_suite_path = f'{TESTS_DIR}/{test_pack}/{test_suite}.py'
            NEW_SUITE_DIR = f'{TESTS_DIR}/{test_pack}/'

        if os.path.exists(new_suite_path):
            raise Exception('Test suite already exists!')
        else:
            FileUtils.write_file(new_suite_path, TEST_SUITE_FILE)
            FileUtils.write_file(f'{NEW_SUITE_DIR}__init__.py', '')
            FileUtils.write_file(f'{NEW_SUITE_DIR}{test_suite}.json', TEST_JSON_FILE)

            print('\nNew Test Suite Created!')

        sys.exit()


    # Load the Traverse Config
    if ARGS.config and ARGS.testrun:
        if platform.system() == 'Windows':
            exec_config_path = f'{CURRENT_DIR}\\config\\executor\\{ARGS.config}.json'
            test_run_path = f'{CURRENT_DIR}\\test_runs\\{ARGS.testrun}.json'
        else:
            exec_config_path = f'{CURRENT_DIR}/config/executor/{ARGS.config}.json'
            test_run_path = f'{CURRENT_DIR}/test_runs/{ARGS.testrun}.json'

        exec_config = LoadJson.using_filepath(exec_config_path)
        test_run = LoadJson.using_filepath(test_run_path)
        trav_con = TraverseConfig(exec_config, test_run, CURRENT_DIR)
    else:
        if not ARGS.config:
            raise Exception('No Executor Config specified. Please pass in an executor config to use with the -C argument')
        elif not ARGS.testrun:
            raise Exception('No Test Run specified. Please pass in a test run name with the -T argument')
        else:
            raise Exception('Something else failed, could be an internal bug :(')


    # Call the Profiler
    profiler = Profiler(trav_con)
    cartesian = profiler.run_profiler()

    # Call the Executor
    executor = Executor(trav_con, cartesian)
    completed_tests = executor.run_executor()

    # Call the Reporter
    reporter = Reporter(trav_con, completed_tests)
    reporter.run_reporter()
