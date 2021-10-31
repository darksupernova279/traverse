''' This is the executor module. It handles anything realted to test execution, singlular, bulk and on the go reporting if its configured. '''
import sys
import os
import traceback
import importlib
import platform

from typing             import List
from datetime           import datetime
from multiprocessing    import Pool

import pyautogui

from tqdm               import tqdm
from core.core_models   import TestStatus, TestDefinition
from core.test_reporter import ReporterTasks


class Executor:
    ''' This is the main Executor class. By initialising this class, it accepts the traverse config and tests cartesian product.
        You can then call the run_executor method and it takes care of the rest.  '''
    def __init__(self, traverse_config, tests_cartesian: List[TestDefinition]):
        self.t_config = traverse_config
        self.t_cartesian = tests_cartesian


    def run_executor(self):
        ''' The main method for the Executor class, by initialising the Executor class, all you would do to execute your
            tests, is call this method, and the tests will all be executed. '''
        num_of_retries = self.t_config.test_retries
        pool = Pool(self.t_config.parallel_tests +1) # Add one, because if you set it to 0, you don't want parallel processing
        completed_tests = []
        incomplete_tests = []

        while num_of_retries >= 0:
            if num_of_retries < self.t_config.test_retries:
                print(f'\nSome tests failed. Retrying them. {num_of_retries} retries are left\n')

            if len(incomplete_tests) > 0:
                tests_to_run = incomplete_tests
                incomplete_tests = []
            else:
                tests_to_run = self.t_cartesian

            for result in tqdm(pool.imap_unordered(self.execute_test, tests_to_run), total=len(tests_to_run)):
                if self.t_config.reporting_on_the_go is True:
                    ReporterTasks.report_test_via_cmd(result)

                if result.test_status == TestStatus.PASSED or result.test_status == TestStatus.BLOCKED:
                    completed_tests.append(result)
                else:
                    if num_of_retries > 0:
                        result.comments = ''

                    result.test_start_time = None
                    result.test_end_time = None
                    incomplete_tests.append(result)

            if len(incomplete_tests) <= 0:
                break

            num_of_retries = num_of_retries - 1

        if len(incomplete_tests) > 0:
            completed_tests.extend(incomplete_tests)

        return completed_tests


    def execute_test(self, test_def: TestDefinition):
        ''' This method will execute a test based on the test definition passed into it. This method only executes 1 test. '''
        try:
            # Start the Timer
            start_time = datetime.now()
            # Setup before starting with the test
            test_def = self.pre_test_setup(test_def)
            if test_def.test_status == TestStatus.BLOCKED:
                return self.update_test_definition(test_def, start_time)
            else:
                # First get the test module .py file
                test_module = importlib.import_module(f'tests.{test_def.test_pack}.{test_def.test_suite}')
                # Get the test class out of the module and store it in a var
                test_class = getattr(test_module, 'Tests')
                # Initialise and store in a var the test class, not forgetting to pass it the required arguments
                init_test_class = test_class(self.t_config, test_def)
                # Get the function under test to execute - Its the raw function, this doesnt execute it, only loads its definition into mem
                test_func = getattr(test_class, test_def.test_name)

                # Execute the test
                test_func(init_test_class)

                # If we make it here it didn't fail, so its a pass, hopefully the test is written to fail correctly for issues :)
                test_def.test_status = TestStatus.PASSED
                return self.update_test_definition(test_def, start_time)

        except AssertionError:
            test_def.test_status = TestStatus.FAILED
            _, _, trace_back = sys.exc_info()
            traceback.print_tb(trace_back) # Fixed format
            tb_info = traceback.extract_tb(trace_back)
            _, line, _, text = tb_info[-1]
            test_def.comments = test_def.comments + 'Assertion error on line {} in statement {}'.format(line, text)

            return self.update_test_definition(test_def, start_time)

        except TimeoutError:
            test_def.test_status = TestStatus.FAILED
            test_def.comments = test_def.comments + 'Timeout Error'

            return self.update_test_definition(test_def, start_time)

        except TypeError:
            test_def.test_status = TestStatus.FAILED
            _, _, trace_back = sys.exc_info()
            traceback.print_tb(trace_back) # Fixed format
            tb_info = traceback.extract_tb(trace_back)
            _, line, _, text = tb_info[-1]
            test_def.comments = test_def.comments + 'Type error on line {} in statement {}'.format(line, text)

            return self.update_test_definition(test_def, start_time)

        except KeyError:
            test_def.test_status = TestStatus.FAILED
            _, _, trace_back = sys.exc_info()
            traceback.print_tb(trace_back) # Fixed format
            tb_info = traceback.extract_tb(trace_back)
            _, line, _, text = tb_info[-1]
            test_def.comments = test_def.comments + 'Key error on line {} in statement {}'.format(line, text)

            return self.update_test_definition(test_def, start_time)

        except Exception as err:
            test_def.test_status = TestStatus.FAILED
            test_def.comments = test_def.comments + str(err)

            _, _, trace_back = sys.exc_info()
            traceback.print_tb(trace_back) # Fixed format
            tb_info = traceback.extract_tb(trace_back)
            _, line, _, text = tb_info[-1]
            test_def.comments = test_def.comments + 'Unhandled error on line {} in statement {}'.format(line, text)

            return self.update_test_definition(test_def, start_time)

        finally:
            try:
                try:
                    if test_def.test_status == TestStatus.FAILED:
                        screenshot = pyautogui.screenshot()

                        if platform.system() == 'Windows':
                            save_path = f'{test_def.screenshot_dir}\\{test_def.test_name}_error.png'
                        else:
                            save_path = f'{test_def.screenshot_dir}/{test_def.test_name}_error.png'

                        screenshot.save(save_path)
                except OSError:
                    pass

                # Try clean up driver, if this works then there was a driver, if not then driver probably not used in the test.
                init_test_class.driver.quit_the_driver()
            except (UnboundLocalError, AttributeError):
                pass


    def update_test_definition(self, test_def, start_time):
        ''' This updates and returns the test definition with all its updates. Wrapped the logic into this function to prevent duplicate code. '''
        end_time = datetime.now()
        test_def.test_start_time = start_time
        test_def.test_end_time = end_time
        return test_def


    def pre_test_setup(self, test_def):
        ''' This method executes right before a test begins execution, this means for any folder creation, file management or setup related
            tasks, this method is used. Do not this setup method is not 'specific' to a test, the logic here should be general setup required
            before any test, but not specific to a product under test.  '''
        # Check the screenshot directory is created
        try:
            if not os.path.exists(test_def.screenshot_dir):
                os.makedirs(test_def.screenshot_dir)

        except Exception as err:
            print(err)

        # Check to ensure if we are on live and if we are safe to execute this
        if (self.t_config.environment == 'live'
            or self.t_config.environment == 'production'
            or self.t_config.environment == 'Live'
            or self.t_config.environment == 'Production'):
            if test_def.production_safe is False:
                test_def.test_status = TestStatus.BLOCKED
                test_def.comments = test_def.comments + 'Skipped, this test is not production safe!'
                return test_def

        test_def.test_status = TestStatus.UNTESTED
        return test_def


    def post_test_cleanup(self):
        ''' This method will be executed after every test to ensure standard clean up operations are conducted. '''
