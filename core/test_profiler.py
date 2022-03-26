''' This module will control all initial setup for tests. The profiler runs before the execution of tests. '''
import platform
import os
import sys
import importlib
from typing                 import List
from core.core_models       import TestDefinition, TraverseConfig
from utilities.json_helper  import LoadJson


class Profiler:
    ''' The Profiler will be responsible for loadings and preparing the queue of tests, along with any global preliminary
        checks or setup's required. '''
    def __init__(self, traverse_config: TraverseConfig):
        self.trav_con = traverse_config


    def _get_all_test_cases_in_test_suite(self, test_pack, test_suite_name):
        ''' This returns all test cases in a test suite given the name of the test pack and test suite passed in. '''
        tests_list = []
        module = importlib.import_module(f"{test_pack}.{test_suite_name}")
        test_class = getattr(module, 'Tests')
        test_cases = [func for func in dir(test_class) if callable(getattr(test_class, func)) and not func.startswith('_')]

        for test_case in test_cases:
            tests_list.append([test_pack, test_suite_name, test_case])

        return tests_list


    def _get_all_test_packs(self, tests_dir:str):
        ''' This method simply returns the test packs (directories) in the tests folder path passed in. '''
        test_packs = []

        for _, dirs, _ in os.walk(tests_dir):
            for directory in dirs:
                if '__' not in directory:
                    test_packs.append(directory)

        return test_packs


    def _get_all_test_suites_in_test_pack(self, tests_dir:str, test_pack_name:str):
        ''' This returns a list of test suites in a test pack given the test directory passed in and the test pack name. '''
        if platform.system() == 'Windows':
            return [file for file in os.listdir(f'{tests_dir}\\{test_pack_name}') if '.py' in file and '__' not in file]
        else:
            return [file for file in os.listdir(f'{tests_dir}/{test_pack_name}') if '.py' in file and '__' not in file]


    def run_profiler(self):
        ''' This is the entry and exit point for the profiler, this is the method you call to use the profiler, all other
            methods are just helper methods '''

        # Prepare the cartesian product for all the tests
        cartesian = self.get_cartesian_of_tests()

        # Run Global Setup
        self.global_setup()

        return cartesian


    def get_tests_list(self, trav_con:TraverseConfig, test:List):
        '''
            This method handles determining the * logic in a test. A test is reference to a test pack - test suite - test case
            combination. Using an * in any of the positions in a test run json file will mean 'all'. Determining or getting 'all'
            will be handled in this method.
        '''
        tests_list = []

        if len(test) < 1:
            return []

        elif len(test) == 1:
            if test[0] == '*':
                test_packs = self._get_all_test_packs(trav_con.tests_folder)

                for test_pack in test_packs:
                    test_suites = self._get_all_test_suites_in_test_pack(trav_con.tests_folder, test_pack)

                    for test_suite in test_suites:
                        test_suite_name = test_suite.replace('.py', '')
                        tests_list.extend(self._get_all_test_cases_in_test_suite(test_pack, test_suite_name))

            else:
                raise Exception('Test declared a test pack with no test suite or test case. Check the docs for more info.')

        elif len(test) == 2:
            if test[1] == '*':
                test_suites = self._get_all_test_suites_in_test_pack(trav_con.tests_folder, test[0])

                for test_suite in test_suites:
                    test_suite_name = test_suite.replace('.py', '')
                    tests_list.extend(self._get_all_test_cases_in_test_suite(test[0], test_suite_name))
            else:
                raise Exception('Test declared a test pack and test suite with no test case. Check the docs for more info.')

        elif len(test) == 3:
            if test[2] == '*':
                tests_list.extend(self._get_all_test_cases_in_test_suite(test[0], test[1]))

            else:
                tests_list.extend([[test[0], test[1], test[2]]])

        else:
            raise Exception(f'Test has too many values declared in the test run. The test is: {test}')

        return tests_list


    def get_cartesian_of_tests(self):
        '''
            This returns a list of test definitions to be executed. The list is a cartesian product of all applicable
            tests + capabilities + test configs
        '''
        sys.path.append(f'{self.trav_con.tests_folder}')
        test_definitions_list = []
        tests_list = []

        # Process the tests in the test run. Needed to handle the * symbols.
        for test in self.trav_con.tests:
            tests_list.extend(self.get_tests_list(self.trav_con, test))

        if self.trav_con.capabilities is None or len(self.trav_con.capabilities) < 1:
            self.trav_con.capabilities = [' - ']

        for capability in self.trav_con.capabilities:
            for test_item in tests_list:
                production_safe = False

                if platform.system() == 'Windows':
                    test_config_path = f'{self.trav_con.tests_folder}\\{test_item[0]}\\{test_item[1]}.json'
                    screenshot_dir = f'{self.trav_con.testrun_result_dir}\\{test_item[0]}\\{test_item[1]}'
                else:
                    test_config_path = f'{self.trav_con.tests_folder}/{test_item[0]}/{test_item[1]}.json'
                    screenshot_dir = f'{self.trav_con.testrun_result_dir}/{test_item[0]}/{test_item[1]}'

                if os.path.exists(test_config_path):
                    test_config_json = LoadJson.using_filepath(test_config_path)

                    ## Attempt to load json values from test config(json) file
                    try:
                        test_configs = test_config_json['testConfigurations']
                    except KeyError:
                        test_configs = {}
                    try:
                        excluded_environments = test_config_json['excludedEnvironments']
                    except KeyError:
                        excluded_environments = []
                    try:
                        production_safe = test_config_json['productionSafe']
                    except KeyError:
                        pass

                    if self.trav_con.environment in excluded_environments:
                        continue

                    if len(test_configs.items()) > 0:
                        for key, values in test_configs.items():
                            for value in values:
                                test_definition = TestDefinition()

                                test_definition.test_pack = test_item[0]
                                test_definition.test_suite = test_item[1]
                                test_definition.test_name = test_item[2]
                                test_definition.platform = self.trav_con.platform
                                test_definition.capability = capability
                                test_definition.test_config_title = str(key)
                                test_definition.test_config_value = str(value)
                                test_definition.production_safe = production_safe
                                test_definition.tests_json = test_config_json
                                test_definition.screenshot_dir = screenshot_dir

                                test_definitions_list.append(test_definition)

                    else:
                        test_definition = TestDefinition()

                        test_definition.test_pack = test_item[0]
                        test_definition.test_suite = test_item[1]
                        test_definition.test_name = test_item[2]
                        test_definition.platform = self.trav_con.platform
                        test_definition.capability = capability
                        test_definition.test_config_title = ' - '
                        test_definition.test_config_value = ' - '
                        test_definition.production_safe = production_safe
                        test_definition.tests_json = test_config_json
                        test_definition.screenshot_dir = screenshot_dir

                        test_definitions_list.append(test_definition)

                else:
                    test_definition = TestDefinition()

                    test_definition.test_pack = test_item[0]
                    test_definition.test_suite = test_item[1]
                    test_definition.test_name = test_item[2]
                    test_definition.platform = self.trav_con.platform
                    test_definition.capability = capability
                    test_definition.test_config_title = ' - '
                    test_definition.test_config_value = ' - '
                    test_definition.production_safe = production_safe
                    test_definition.tests_json = {}
                    test_definition.screenshot_dir = screenshot_dir

                    test_definitions_list.append(test_definition)

        return test_definitions_list


    def global_setup(self):
        ''' Global Setup will execute a series of pre-test setup tasks before any test executes. This is useful for any form of
            folder creation, test data setup or even a check up to ensure a clean environment '''

        # TO DO
