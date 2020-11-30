''' This module will control all initial setup for tests. The profiler runs before the execution of tests. '''

import os
from core.core_details      import TestDefinition
from utilities.json_helper  import LoadJson


class Profiler:
    ''' The Profiler will be responsible for loadings and preparing the queue of tests, along with any global preliminary
        checks or setup's required. '''
    def __init__(self, traverse_config):
        self.t_config = traverse_config

    # This is the entry and exit point for the profiler, this is the method you call to use the profiler, all other methods
    # are just helper methods. I keep this method at the top o this class for easy access and maintainability
    def run_profiler(self):
        ''' This is the entry and exit point for the profiler, this is the method you call to use the profiler, all other
            methods are just helper methods '''

        # Prepare the cartesian product for all the tests
        cartesian = self.get_tests_cartesian_product()

        # Run Global Setup
        self.global_setup()

        return cartesian


    def get_tests_cartesian_product(self):
        ''' Pass in the test json path to retrieve a list of the tests. This will return a cartesian product of the tests'''
        # Get the tests json
        tests_json = LoadJson.using_filepath(self.t_config.tests_folder + self.t_config.tests_json_name)

        # Load the test json's values
        platform = tests_json['platform']
        capabilities = tests_json['capabilities']
        tests = tests_json['tests']

        # Create the tuple
        cartesian = []

        # If capability is -1, then this is a non UI related test, it means driver will not be called
        if capabilities is None or len(capabilities) < 1:
            capabilities = ['Not Applicable']

        # Define the function specifically to wrap the logic of setting the test definition
        def set_test_definition(test, cap, platform, config=None):
            ''' Created just for this task, to wrap the logic and prevent duplicate code. '''
            test_def = TestDefinition() # Initialise our test definition
            pack, suite, testname = test # Unpack the array into independent variables

            # Set the Test Definition values
            test_def.test_pack = pack
            test_def.test_suite = suite
            test_def.test_name = testname
            test_def.capability = cap
            test_def.platform = platform
            test_def.test_configuration = config

            test_def.screenshot_dir = self.t_config.test_result_dir + '\\' + pack + '\\' + suite + '\\'

            return test_def


        # Now for main loops to create our cartesian of test definitions
        for cap in capabilities:
            for test in tests:
                if os.path.exists(self.t_config.tests_folder + test[0] + '\\tests_config.json'):
                    # Load the test config json if exists
                    test_configs = LoadJson.using_filepath(self.t_config.tests_folder + test[0] + '\\tests_config.json')

                    # Attach each config to each test, making the cartesian bigger
                    for key, values in test_configs.items():
                        for value in values:
                            config = (str(key) + ': ' + str(value))
                            test_def = set_test_definition(test, cap, platform, config)
                            cartesian.append(test_def)

                else:
                    test_def = set_test_definition(test, cap, platform)
                    cartesian.append(test_def)

        return cartesian


    def global_setup(self):
        ''' Global Setup will execute a series of pre-test setup tasks before any test executes. This is useful for any form of
            folder creation, test data setup or even a check up to ensure a clean environment '''

