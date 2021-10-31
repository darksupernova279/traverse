''' The main file to begin execution of the automation.
It all starts with traverse.py, from this file, we pass it arguments, and it then takes care of the rest.  '''
import os
import platform
import sys
import shutil
import argparse
import warnings
from datetime                   import datetime
from os.path                    import realpath, dirname
from utilities.json_helper      import LoadJson, GetJsonValue, WriteJsonFile
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

PARSER.add_argument('-T'
                    , '--tconfig'
                    , type=str
                    , help='Uses a specific traverse config. Pass in the name. Will error if not found.')

PARSER.add_argument('-G'
                    , '--generate'
                    , type=str
                    , help='Creates a new traverse config with default settings.')

# Read arguments from the CMD
ARGS = PARSER.parse_args()


# Get traverse config
CURRENT_DIR = dirname(realpath(__file__))


class TraverseConfig:
    ''' Loads the traverse_config.json file and its values for the app to use. '''
    def __init__(self, config_name=''):
        if config_name == '':
            if platform.system() == 'Windows':
                self.tests_folder = '\\tests\\'
                self.reporting_folder = '\\reports\\'
            else:
                self.tests_folder = '/tests/'
                self.reporting_folder = '/reports/'

            self.test_plan_name = 'traverse_test'
            self.parallel_tests = 0
            self.test_retries = 1
            self.debug_enabled = False
            self.environment = 'dev'
            self.reporting_delivery_type = 'cmd' # Options are 'html' OR 'cmd' OR 'email'
            self.reporting_on_the_go = True
            self.reporting_nuke_reports = False
            self.reporting_html_template = ''
            self.reporting_email_sender = ''
            self.reporting_email_password = ''
            self.reporting_email_mailing_list = []
            self.reporting_email_smtp_server = ''
            self.reporting_email_smtp_port = 465
            self.reporting_email_subject = ''
        else:
            if platform.system() == 'Windows':
                self._traverse_config = LoadJson.using_filepath(CURRENT_DIR + '\\' + config_name + '.json')
            else:
                self._traverse_config = LoadJson.using_filepath(CURRENT_DIR + '/' + config_name + '.json')

            self.tests_folder = CURRENT_DIR + GetJsonValue.by_key(self._traverse_config, 'testsFolder')
            self.test_plan_name = GetJsonValue.by_key(self._traverse_config, 'testPlanName')
            self.parallel_tests = GetJsonValue.by_key(self._traverse_config, 'parallelTests')
            self.test_retries = GetJsonValue.by_key(self._traverse_config, 'testRetries')
            self.debug_enabled = GetJsonValue.by_key(self._traverse_config, 'debugEnabled')
            self.environment = GetJsonValue.by_key(self._traverse_config, 'environment')
            self.reporting_folder = CURRENT_DIR + GetJsonValue.by_key(self._traverse_config, 'reporting', 'reportsFolder')
            self.reporting_delivery_type = GetJsonValue.by_key(self._traverse_config, 'reporting', 'reportDeliveryType')
            self.reporting_on_the_go = GetJsonValue.by_key(self._traverse_config, 'reporting', 'reportOnTheGo')
            self.reporting_nuke_reports = GetJsonValue.by_key(self._traverse_config, 'reporting', 'nukeReports')
            self.reporting_html_template = GetJsonValue.by_key(self._traverse_config, 'reporting', 'htmlTemplate')
            self.reporting_email_sender = GetJsonValue.by_key(self._traverse_config, 'reporting', 'emailSettings', 'senderEmail')
            self.reporting_email_password = GetJsonValue.by_key(self._traverse_config, 'reporting', 'emailSettings', 'senderPassword')
            self.reporting_email_mailing_list = GetJsonValue.by_key(self._traverse_config, 'reporting', 'emailSettings', 'reportMailingList')
            self.reporting_email_smtp_server = GetJsonValue.by_key(self._traverse_config, 'reporting', 'emailSettings', 'smtpServer')
            self.reporting_email_smtp_port = GetJsonValue.by_key(self._traverse_config, 'reporting', 'emailSettings', 'smtpPort')
            self.reporting_email_subject = GetJsonValue.by_key(self._traverse_config, 'reporting', 'emailSettings', 'emailSubject')

        self.tests_json_name = None
        timestamp = str(datetime.now().strftime('%Y-%m-%d_%Hh%Mm%Ss'))
        if platform.system() == 'Windows':
            self.test_result_dir = f'{self.reporting_folder}\\{self.test_plan_name}_{timestamp}\\'
        else:
            self.test_result_dir = f'{self.reporting_folder}/{self.test_plan_name}_{timestamp}/'

        if self.parallel_tests < 0:
            raise Exception('Parallel tests set to less than 0!')

def preliminary_checks(t_config):
    ''' This function will do some checks before starting any work, mainly to be sure everything is in order and ready for traverse to begin. '''
    # If the setting is to nuke reports, we delete and remake the directory
    if t_config.reporting_nuke_reports is True:
        if os.path.exists(t_config.reporting_folder):
            shutil.rmtree(t_config.reporting_folder)
            os.makedirs(t_config.reporting_folder)
    else:
        if not os.path.exists(t_config.reporting_folder):
            os.makedirs(t_config.reporting_folder)

    # Ensure Test Results Folder Exists
    if not os.path.exists(t_config.test_result_dir):
        os.makedirs(t_config.test_result_dir)


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

    if ARGS.generate:
        default_config = {
            'testsFolder': '\\tests\\',
            'testPlanName': 'traverse_test',
            'parallelTests': 0,
            'testRetries': 1,
            'debugEnabled': False,
            'environment': 'dev',
            'reporting': {
                'reportsFolder': '\\reports\\',
                'reportDeliveryType': 'html',
                'reportOnTheGo': True,
                'nukeReports': True,
                'htmlTemplate': '',
                'emailSettings': {
                    'senderEmail': '',
                    'senderPassword': '',
                    'reportMailingList': [''],
                    'smtpServer': 'smtp.gmail.com',
                    'smtpPort': 465,
                    'emailSubject': ''
                }
            }
        }
        if platform.system() == 'Windows':
            config_path = CURRENT_DIR + '\\' + ARGS.generate + '.json'
        else:
            config_path = CURRENT_DIR + '/' + ARGS.generate + '.json'

        if os.path.exists(config_path):
            while True:
                proceed = input(f'\nThere is already a {ARGS.generate} config. Do you want to overwrite?\nY/n? ')

                if proceed == 'Y' or proceed == '':
                    WriteJsonFile.write(default_config, config_path)
                    break
                elif proceed == 'n':
                    sys.exit()
                else:
                    print('\nInput not recognised. Please try again!')
                    continue
        else:
            WriteJsonFile.write(default_config, config_path)
            if os.path.exists(config_path):
                print('\nT Config Created!')
                sys.exit()
            else:
                raise Exception('Config generation failed!')

    # Load the Traverse Config
    if ARGS.tconfig:
        traverse_config = TraverseConfig(ARGS.tconfig)
    else:
        traverse_config = TraverseConfig()

    # If debug is enabled we only load tests in the debug config. This is for development purposes.
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
