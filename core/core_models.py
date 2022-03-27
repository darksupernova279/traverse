''' core_models is a module which holds classes realted to core features. Such as a class that holds test statuses,
    or the test definition. These classes are usually shared across core modules and re-used often, sometimes by other
    modules not related to core.  '''
import random
import string
import itertools
import platform
from datetime               import datetime
from typing                 import Dict
from utilities.json_helper  import LoadJson


class ReporterConfig:
    ''' Model config for the Reporter configuration file '''
    def __init__(self, reporter_config: Dict, root_dir: str) -> None:
        # Deal with Reports folder
        if reporter_config['reportsFolder'] == '':
            if platform.system() == 'Windows':
                self.reports_folder = f'{root_dir}\\reports'
            else:
                self.reports_folder = f'{root_dir}/reports'
        else:
            self.reports_folder = reporter_config['testsFolder']

        # Rest of Reporter Config
        self.report_methods = reporter_config['reportMethods']
        self.html_template = reporter_config['htmlTemplate']
        self.email_sender = reporter_config['emailSettings']['senderEmail']
        self.email_password = reporter_config['emailSettings']['senderPassword']
        self.email_mailing_list = reporter_config['emailSettings']['mailingList']
        self.email_smtp_server = reporter_config['emailSettings']['smtpServer']
        self.email_smtp_port = reporter_config['emailSettings']['smtpPort']
        self.email_subject = reporter_config['emailSettings']['emailSubject']
        self.on_fail_email_report = reporter_config['onFailure']['emailReport']
        self.on_fail_mailing_list = reporter_config['onFailure']['mailingList']
        self.history_days_to_keep = reporter_config['reportHistory']['daysToKeep']


class LoggerConfig:
    ''' Model config for the Logger configuration file '''
    def __init__(self, logger_config: Dict, root_dir: str) -> None:
        # Deal with Logs folder value
        if logger_config['logsFolder'] == '':
            if platform.system() == 'Windows':
                self.logs_folder = f'{root_dir}\\logs'
            else:
                self.logs_folder = f'{root_dir}/logs'
        else:
            self.logs_folder = logger_config['logsFolder']

        # Rest of Log Config
        self.log_levels = logger_config['logLevels']
        self.log_methods = logger_config['logMethods']
        self.custom_logger_config = logger_config['customLoggerConfig']
        self.email_sender = logger_config['emailSettings']['senderEmail']
        self.email_password = logger_config['emailSettings']['senderPassword']
        self.email_mailing_list = logger_config['emailSettings']['mailingList']
        self.email_smtp_server = logger_config['emailSettings']['smtpServer']
        self.email_smtp_port = logger_config['emailSettings']['smtpPort']
        self.history_days_to_keep = logger_config['logHistory']['daysToKeep']
        self.slack_bearer_token = logger_config['slack']['bearerToken']
        self.slack_channels = logger_config['slack']['channels']
        self.slack_user_mentions = logger_config['slack']['userMentions']


class TraverseConfig:
    '''
        The traverse config model to be used in the framework. Also called trav_con for short.
        First parameter is the loaded json of the traverse config.
        2nd parameter is the main directory(root) that the framework is currently in.
    '''
    def __init__(self, exec_config: Dict, test_run: Dict, root_dir: str):
        try:
            # Deal with Tests folder value
            if exec_config['testsFolder'] == '':
                if platform.system() == 'Windows':
                    self.tests_folder = f'{root_dir}\\tests'
                else:
                    self.tests_folder = f'{root_dir}/tests'
            else:
                self.tests_folder = exec_config['testsFolder']

            # Rest of Executor Config
            self.parallel_tests = exec_config['parallelTests']
            self.test_retries = exec_config['testRetries']
            self.debug_enabled = exec_config['debugEnabled']
            self.test_result_updates = exec_config['testResultUpdates']
            self.live_environment_name = exec_config['liveEnvironmentName']
            self.environment = exec_config['environmentName']

            # Test Run Config
            self.test_run_name = test_run['testRunName']
            self.platform = test_run['platform']
            self.capabilities = test_run['capabilities']
            self.tests = test_run['tests']

            # Load Logger and Reporter config
            logger_config_name = test_run['loggerConfig']
            reporter_config_name = test_run['reporterConfig']

            if platform.system() == 'Windows':
                logger_config = LoadJson.using_filepath(f'{root_dir}\\config\\logger\\{logger_config_name}.json')
                reporter_config = LoadJson.using_filepath(f'{root_dir}\\config\\reporter\\{reporter_config_name}.json')
                if logger_config['customLoggerConfig'] != '':
                    logger_config_custom = LoadJson.using_filepath(f"{root_dir}\\config\\logger\\{logger_config['customLoggerConfig']}.json")
            else:
                logger_config = LoadJson.using_filepath(f'{root_dir}/config/logger/{logger_config_name}.json')
                reporter_config = LoadJson.using_filepath(f'{root_dir}/config/reporter/{reporter_config_name}.json')
                if logger_config['customLoggerConfig'] != '':
                    logger_config_custom = LoadJson.using_filepath(f"{root_dir}/config/logger/{logger_config['customLoggerConfig']}.json")

            self.logger_settings = LoggerConfig(logger_config, root_dir)
            self.reporter_settings = ReporterConfig(reporter_config, root_dir)

            if logger_config['customLoggerConfig'] != '':
                self.logger_custom_settings = LoggerConfig(logger_config_custom, root_dir)
            else:
                self.logger_custom_settings = None

            # Other settings
            self.root_directory = root_dir

            test_run_id = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
            test_run_time = datetime.now().strftime('%Y-%m-%d %Hh%Mm%Ss')
            if platform.system() == 'Windows':
                self.testrun_result_dir = f"{self.reporter_settings.reports_folder}\\{self.test_run_name} - {test_run_id} - {test_run_time}\\"
            else:
                self.testrun_result_dir = f"{self.reporter_settings.reports_folder}/{self.test_run_name} - {test_run_id} - {test_run_time}/"

            # Validation on settings
            if self.parallel_tests < 0:
                raise Exception('Parallel tests set to less than 0!')

        except KeyError as error:
            raise Exception(f'Could not load key {error.args[0]} in Traverse Config') from error


class TestStatus:
    ''' A holding class for all available test statuses. '''
    UNTESTED = 'Untested'
    PASSED = 'Passed'
    FAILED = 'Failed'
    BLOCKED = 'Blocked'
    RETEST = 'Retest'
    IN_PROGRESS = 'InProgress'


class TestDefinition:
    ''' A class used to track, and keep context of test information for preparing, setup, execution and reporting. '''
    id_itr = itertools.count()
    def __init__(self):
        self.test_id = next(self.id_itr)
        self.test_pack = None
        self.test_suite = None
        self.test_name = None
        self.platform = None
        self.capability = None # If -1 is passed in, this will not require a driver
        self.test_config_title = None
        self.test_config_value = None
        self.production_safe = False

        self.test_status = TestStatus.UNTESTED
        self.test_start_time = None
        self.test_end_time = None
        self.comments = ''

        self.screenshot_dir = None
        self.tests_json:Dict = None


class ReportDeliveryType:
    ''' A holding class for the report types we want to use / differentiate or support. '''
    CMD = 'cmd'
    HTML = 'html'
    EMAIL = 'email'
