''' The reporter is responsible to reporting on the test results for the active test run. Depending on settings, it can be used by the
    executor to report on the go or stick to reporting results at the end of execution. '''

import os
import warnings
import subprocess
import platform as PLATFORM
from tqdm               import tqdm
from core.core_details  import TestStatus, ReportType
from utilities.terminal import ColorCodes

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))

class ReporterTasks:
    ''' This class is used to wrap functionality for re-use into methods, and its an entry point for other parts of
        traverse to access static methods for reporting. '''

    @staticmethod
    def report_test_via_cmd(test_def):
        ''' This method accepts a test denition as an argument, and will report the status of that test to the cmd '''
        # Set the color of the terminal text depending on test status
        if test_def.test_status == TestStatus.PASSED:
            color = ColorCodes.OKGREEN
        elif test_def.test_status == TestStatus.FAILED:
            color = ColorCodes.FAIL
        elif test_def.test_status == TestStatus.RETEST:
            color = ColorCodes.YELLOW
        elif test_def.test_status == TestStatus.BLOCKED:
            color = ColorCodes.CITALIC

        test_duration = test_def.test_end_time - test_def.test_start_time
        # Print to Terminal
        tqdm.write(f'''{color}Test: {test_def.test_pack} - {test_def.test_suite} - {test_def.test_name} - {test_def.platform} - {test_def.capability}
                - Test Configuration: {test_def.test_config_title} : {test_def.test_config_value}
                - Status: {test_def.test_status}
                - Duration: {test_duration}
                - Comments: {test_def.comments}{ColorCodes.ENDC}
                ''')


class Reporter:
    ''' The Reporter is responsible for accepting the test results, along with the traverse config, and reporting those
        results as per the method defined. This means if reporting results to cmd is set, it will report all test statuses
        to the terminal/console. '''
    def __init__(self, traverse_config, test_results):
        self.t_config = traverse_config
        self.t_results = test_results
        self.tests_passed = []
        self.tests_failed = []
        self.tests_untested = []
        self.tests_blocked = []
        self.tests_total = len(test_results)

        self.num_tests_passed = sum(test.test_status == TestStatus.PASSED for test in test_results)
        self.num_tests_failed = sum(test.test_status == TestStatus.FAILED for test in test_results)
        self.num_tests_untested = sum(test.test_status == TestStatus.UNTESTED for test in test_results)
        self.num_tests_blocked = sum(test.test_status == TestStatus.BLOCKED for test in test_results)


    def run_reporter(self):
        ''' This is the main entry into the reporter, by calling this method, the reporter will execute and report on all test results. '''
        # First split the results
        self.split_test_results()
        if self.t_config.report_type == ReportType.CMD:
            self.report_results_via_cmd()
        elif self.t_config.report_type == ReportType.HTML:
            self.report_results_via_html()


    def split_test_results(self):
        ''' This method splits the results into seperate lists. This is used for reporting statistics. '''
        for test in self.t_results:
            if test.test_status == TestStatus.PASSED:
                self.tests_passed.append(test)
            elif test.test_status == TestStatus.FAILED:
                self.tests_failed.append(test)
            elif test.test_status == TestStatus.UNTESTED:
                self.tests_untested.append(test)
            elif test.test_status == TestStatus.BLOCKED:
                self.tests_blocked.append(test)
            else:
                warnings.warn('There are tests with statuses which could not be identified, this calls for an audit!')


    def report_results_via_cmd(self):
        ''' The method used to report ALL results to the console, it takes no parameters because the test results are
            passed to the reporter class when the Reporter class is initialised '''
        for test in self.t_results:
            ReporterTasks.report_test_via_cmd(test)


    def report_results_via_html(self):
        ''' This method will report all test results by building an html page and opening up in a browser '''
        # First create an empty string object
        html_combined = ''
        # Now loop and concatenate each row to the html string
        for test in self.t_results:
            test_duration = test.test_end_time - test.test_start_time
            html_fragment = f'''
                        <tr>
                            <td>{test.test_id}</td>
                            <td>{test.test_pack}</td>
                            <td>{test.test_suite}</td>
                            <td>{test.test_name}</td>
                            <td>{test.platform}</td>
                            <td>{test.capability}</td>
                            <td>{test.test_config_title} : {test.test_config_value}</td>
                            <td>{test.test_status}</td>
                            <td>{test_duration}</td>
                            <td>{test.comments}</td>
                        </tr>
                            '''
            html_combined = html_combined + html_fragment

        # Read/Load the template file
        with open(CURRENT_DIR + '\\html_report\\report.html', 'r') as f_in:
            f_data = f_in.read()

        # Replace the token with our string of html markup
        f_data = f_data.replace('_rowToken_', html_combined)

        # Save the final html file
        file_loc = self.t_config.test_result_dir + 'test_report.html'
        with open(file_loc, 'w', encoding="utf-8") as f_out:
            f_out.write(f_data)

        # Determine OS we are on and open the report
        if PLATFORM.system() == "Darwin":
            subprocess.call(('open', file_loc))
        elif PLATFORM.system() == "Windows":
            os.startfile(file_loc)
        else:
            subprocess.call(("xdg-open", file_loc))
