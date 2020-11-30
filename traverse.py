''' The main file to begin execution of the automation.
It all starts with traverse.py, from this file, we pass it arguments, and it then takes care of the rest.  '''
import os
import shutil
import argparse
import warnings
from datetime                   import datetime
from os.path                    import realpath, dirname
from utilities.json_helper      import LoadJson, GetJsonValue
from core.test_profiler         import Profiler
from core.test_executor         import Executor
from core.test_reporter         import Reporter


# Initiate the parser
PARSER = argparse.ArgumentParser(description=''' Traverse assists in the execution of automation for web, API and database related automation. ''')
PARSER.add_argument('-R'
                    , '--regression'
                    , help='Runs all regression tests found in the regreession test json file.'
                    , action='store_true')

PARSER.add_argument('-S'
                    , '--specific'
                    , type=str
                    , help='Enter the name of the test bundle you wish to execute.')

# Read arguments from the CMD
ARGS = PARSER.parse_args()


# Get traverse config
CURRENT_DIR = dirname(realpath(__file__))


class TraverseConfig:
    ''' Loads the traverse_config.json file and its values for the app to use. '''
    def __init__(self):
        self._traverse_config = LoadJson.using_filepath(CURRENT_DIR + '\\traverse_config.json')
        self.tests_json_name = None

        self.reports_folder = CURRENT_DIR + GetJsonValue.by_key(self._traverse_config, 'reportsFolder')
        self.tests_folder = CURRENT_DIR + GetJsonValue.by_key(self._traverse_config, 'testsFolder')
        self.test_plan_name = GetJsonValue.by_key(self._traverse_config, 'testPlanName')
        self.parallel_tests = GetJsonValue.by_key(self._traverse_config, 'parallelTests')
        self.debug_enabled = GetJsonValue.by_key(self._traverse_config, 'debugEnabled')
        self.report_type = GetJsonValue.by_key(self._traverse_config, 'reportType')
        self.report_on_the_go = GetJsonValue.by_key(self._traverse_config, 'reportOnTheGo')
        self.nuke_reports = GetJsonValue.by_key(self._traverse_config, 'nukeReports')

        self.test_result_dir = self.reports_folder + '\\' + self.test_plan_name + '_' + str(datetime.now().strftime('%Y-%m-%d_%Hh%Mm%Ss')) + '\\'

        if self.parallel_tests < 0:
            raise Exception('Parallel tests set to less than 0!')

def preliminary_checks(t_config):
    ''' This function will do some checks before starting any work, mainly to be sure everything is in order and ready for traverse to begin. '''
    # If the setting is to nuke reports, we delete and remake the directory
    if t_config.nuke_reports is True:
        if os.path.exists(t_config.reports_folder):
            shutil.rmtree(t_config.reports_folder)
            os.makedirs(t_config.reports_folder)
    else:
        if not os.path.exists(t_config.reports_folder):
            os.makedirs(t_config.reports_folder)

    # Ensure Test Results Folder Exists
    if not os.path.exists(t_config.test_result_dir):
        os.makedirs(t_config.test_result_dir)


#############################################################
#                           Main                            #
#############################################################
if __name__ == '__main__':
    print('''Traverse is an autoamtion framework of sorts written in Python. It initially was an idea to learn Python and automate a product at the
                same time. Copyright (C) 2020 Jade. R. Hancox. This program comes with ABSOLUTELY NO WARRANTY; This is free software, and you are welcome
                to redistribute it under certain conditions. Please see the COPYING.txt file in the root directory for license information. Note that this
                license applies to all source files in this repository. ''')
    traverse_config = TraverseConfig()

    if traverse_config.debug_enabled is True:
        warnings.warn('Debug Enabled! Will only execute debug tests')
        traverse_config.tests_json_name = 'debug.json'
    else:
        if ARGS.regression:
            print('Run Regression')
            traverse_config.tests_json_name = 'regression.json'
        elif ARGS.specific:
            print('Run Specific Test Pack')
            traverse_config.tests_json_name = ARGS.specific + '.json'
        else:
            raise Exception('No argument passed to traverse, unable to predict what you want!')

    # Do some pre checks
    preliminary_checks(traverse_config)

    # Call the Profiler
    profiler = Profiler(traverse_config)
    cartesian = profiler.run_profiler()

    # Call the Executor
    executor = Executor(traverse_config, cartesian)
    completed_tests = executor.run_executor()

    # Call the Reporter
    reporter = Reporter(traverse_config, completed_tests)
    reporter.run_reporter()
