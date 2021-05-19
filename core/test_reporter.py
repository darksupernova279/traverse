''' The reporter is responsible to reporting on the test results for the active test run. Depending on settings, it can be used by the
    executor to report on the go or stick to reporting results at the end of execution. '''

import os
import warnings
import subprocess
import smtplib
import ssl
import platform as PLATFORM
from email.mime.text        import MIMEText
from email.mime.multipart   import MIMEMultipart
from tqdm                   import tqdm
from core.core_details      import TestStatus, ReportDeliveryType
from utilities.terminal     import ColorCodes

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))

class ReporterTasks:
    ''' This class is used to wrap functionality for re-use into methods, and its an entry point for other parts of
        traverse to access static methods for reporting. '''

    @staticmethod
    def report_test_via_cmd(test_def):
        '''
            This method accepts a test denition as an argument, and will report the status of that test to the cmd.
            This is a static method for a reason and should be seperate from the Reporter class.
        '''
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
        tqdm.write(f'''\n{color}
                Test: {test_def.test_pack} - {test_def.test_suite} - {test_def.test_name} - {test_def.platform} - {test_def.capability}
                - Test Configuration: {test_def.test_config_title} : {test_def.test_config_value}
                - Status: {test_def.test_status}
                - Duration: {test_duration}
                - Comments: {test_def.comments}
                {ColorCodes.ENDC}
                ''')

    @staticmethod
    def build_test_results_html(test_results):
        ''' This method builds and returns the default html code stored in report.html '''
        # First create an empty string object
        html_combined = ''
        css_class_passed = 'background-color: #3cc47c;'
        css_class_failed = 'background-color: #e24e42;'
        css_class_blocked = 'background-color: #cccccc;'
        css_class_retest = 'background-color: #ffe400;'
        # Now loop and concatenate each row to the html string
        for test in test_results:
            if test.test_status == TestStatus.PASSED:
                css_for_row = css_class_passed
            elif test.test_status == TestStatus.FAILED:
                css_for_row = css_class_failed
            elif test.test_status == TestStatus.RETEST:
                css_for_row = css_class_retest
            elif test.test_status == TestStatus.BLOCKED:
                css_for_row = css_class_blocked

            test_duration = test.test_end_time - test.test_start_time
            html_fragment = f'''
                        <tr style="{css_for_row}">
                            <td style="padding: 2px;">{test.test_id}</td>
                            <td style="padding: 2px;">{test.test_pack}</td>
                            <td style="padding: 2px;">{test.test_suite}</td>
                            <td style="padding: 2px;">{test.test_name}</td>
                            <td style="padding: 2px;">{test.platform}</td>
                            <td style="padding: 2px;">{test.capability}</td>
                            <td style="padding: 2px;">{test.test_config_title} : {test.test_config_value}</td>
                            <td style="padding: 2px; font-weight: bold;">{test.test_status}</td>
                            <td style="padding: 2px;">{test_duration}</td>
                            <td style="padding: 2px;">{test.comments}</td>
                        </tr>
                            '''
            html_combined = html_combined + html_fragment

        # Read/Load the template file
        with open(CURRENT_DIR + '\\html_report\\report.html', 'r') as f_in:
            f_data = f_in.read()

        # Replace the token with our string of html markup
        f_data = f_data.replace('_rowToken_', html_combined)

        return f_data

    @staticmethod
    def build_custom_html_comments_only(test_results, template_name):
        '''
            This method is for use cases where you want to send an email but want to have your own template and are formatting or
            customising the test comments in the actual tests. This is common when using the framework for reporting instead of testing.
        '''
        html_combined = ''

        for test in test_results:
            html_fragment = f'''
                        <p>
                            {test.comments}
                        </p>
                            '''
            html_combined = html_combined + html_fragment

        # Read/Load the template file
        with open(f'{CURRENT_DIR}\\html_report\\{template_name}.html', 'r') as f_in:
            f_data = f_in.read()

        # Replace the token with our string of html markup
        f_data = f_data.replace('_rowToken_', html_combined)

        return f_data


class Reporter:
    '''
        The Reporter is responsible for accepting the test results, along with the traverse config, and reporting those
        results as per the method defined. This means if reporting results to cmd is set, it will report all test statuses
        to the terminal/console.
    '''
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
        if self.t_config.reporting_delivery_type == ReportDeliveryType.CMD:
            self.report_via_cmd()
        elif self.t_config.reporting_delivery_type == ReportDeliveryType.HTML:
            self.report_via_html_file()
        elif self.t_config.reporting_delivery_type == ReportDeliveryType.EMAIL:
            self.report_via_email()


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


    def report_via_cmd(self):
        ''' The method used to report ALL results to the console, it takes no parameters because the test results are
            passed to the reporter class when the Reporter class is initialised '''
        for test in self.t_results:
            ReporterTasks.report_test_via_cmd(test)


    def report_via_html_file(self):
        ''' This method will report all test results by building an html page and opening up in a browser '''

        html_data_file = ReporterTasks.build_test_results_html(self.t_results)

        # Save the final html file
        file_loc = self.t_config.test_result_dir + 'test_report.html'
        with open(file_loc, 'w', encoding="utf-8") as f_out:
            f_out.write(html_data_file)

        # Determine OS we are on and open the report
        if PLATFORM.system() == "Darwin":
            subprocess.call(('open', file_loc))
        elif PLATFORM.system() == "Windows":
            os.startfile(file_loc)
        else:
            subprocess.call(("xdg-open", file_loc))


    def report_via_email(self):
        '''
            This method uses standard python libraries to send an email to the settings in the traverse config.
            If you entered the name of a html template then it will be used over the default one and sent in the email.
        '''
        sent_from = self.t_config.reporting_email_sender
        send_to = self.t_config.reporting_email_mailing_list

        email_msg = MIMEMultipart('alternative')
        if self.t_config.reporting_email_subject == '':
            email_msg['Subject'] = self.t_config.test_plan_name
        else:
            email_msg['Subject'] = self.t_config.reporting_email_subject

        email_msg['From'] = self.t_config.reporting_email_sender
        email_msg['To'] = ', '.join(self.t_config.reporting_email_mailing_list)

        if self.t_config.reporting_html_template == '':
            email_body = ReporterTasks.build_test_results_html(self.t_results)
        else:
            email_body = ReporterTasks.build_custom_html_comments_only(self.t_results, self.t_config.reporting_html_template)

        # Convert and attach!
        part = MIMEText(email_body, 'html')
        email_msg.attach(part)

        # Create an SSL connection and send the email!
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(self.t_config.reporting_email_smtp_server, self.t_config.reporting_email_smtp_port, context=context) as server:
            server.login(sent_from, self.t_config.reporting_email_password)
            server.sendmail(
                sent_from, send_to, email_msg.as_string()
            )
