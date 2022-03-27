''' This module handles anything realted to logging for the framework. '''
from datetime                   import datetime
import os
import sys
import smtplib
import traceback
import ssl
import platform
from email.mime.text            import MIMEText
from email.mime.multipart       import MIMEMultipart
from tqdm                       import tqdm
from core.core_models           import LoggerConfig, TraverseConfig
from utilities.file_helper      import FileUtils
from utilities.terminal         import ColorCodes
from utilities.slack            import Slack

class LogMethods:
    ''' Available Log Methods for the Log module. '''
    CONSOLE = 'console'
    FILE = 'file'
    EMAIL = 'email'
    SLACK = 'slack'

class LogLevels:
    ''' Available Log Levels for the Log module. '''
    ERROR = 'error'
    WARNING = 'warning'
    ALERT = 'alert'
    DEBUG = 'debug'


class Logger:
    '''
        Levels from highest to lowest are: error -> warning -> alert -> debug . This means if your log level is error then only
        error is reported and all levels below are ignored. The level 'custom' will always log, this is due to it being
        user managed.
    '''
    def __init__(self, traverse_config: TraverseConfig) -> None:
        self.trav_con = traverse_config

        if not os.path.exists(os.path.dirname(self.trav_con.logger_settings.logs_folder)):
            os.makedirs(os.path.dirname(self.trav_con.logger_settings.logs_folder), exist_ok=True)

        if self.trav_con.logger_custom_settings is not None and not os.path.exists(os.path.dirname(self.trav_con.logger_custom_settings.logs_folder)):
            os.makedirs(os.path.dirname(self.trav_con.logger_custom_settings.logs_folder), exist_ok=True)


    def _print_log_to_console(self, msg, time, log_level):
        ''' This method prints the log event to the console. It will change the terminal text color based off the log level. '''
        if log_level == LogLevels.ERROR:
            color = ColorCodes.FAIL
        elif log_level == LogLevels.WARNING:
            color = ColorCodes.YELLOW
        elif log_level == LogLevels.ALERT:
            color = ColorCodes.CYAN
        elif log_level == LogLevels.DEBUG:
            color = ColorCodes.DARK_GREY
        else:
            color = ColorCodes.LIGHT_GREY

        tqdm.write(f'''\n{color}-> {time}: {msg} {ColorCodes.ENDC}''')


    def _write_log_to_file(self, msg, date, time, log_level, logger_config: LoggerConfig):
        '''
            This method writes a log event to a file. The file is stored in the log directory in the logger config (see docs
            for logger config is unsure). The file name is based off the date and log level.
        '''
        log_name = f"{log_level} - {date}"
        log_entry = f'\n-> {time} - {msg}'

        if platform.system() == 'Windows':
            log_file_full_path = f'{logger_config.logs_folder}\\{log_name}.txt'
        else:
            log_file_full_path = f'{logger_config.logs_folder}/{log_name}.txt'

        FileUtils.write_file(log_file_full_path, log_entry)


    def _notify_via_email(self, msg, date, time, log_level, logger_config: LoggerConfig):
        ''' Logs an event via email based off the email settings in the logger config. '''
        sent_from = logger_config.email_sender
        send_to = logger_config.email_mailing_list
        email_msg = MIMEMultipart('alternative')

        email_msg['From'] = sent_from
        email_msg['To'] = ', '.join(send_to)
        email_msg['Subject'] = f'Log - {log_level} - {self.trav_con.test_run_name} - {date}'

        html_body = f'''
            <div>
                <p>A log event has triggered for test run: {self.trav_con.test_run_name}</p>
                <p>Log Time: {time}</p>
                <p>Log Message: {msg}</p>
            </div>
        '''

        part = MIMEText(html_body, 'html')
        email_msg.attach(part)

        context = ssl.create_default_context()
        smtp_port = logger_config.email_smtp_port
        smtp_server = logger_config.email_smtp_server
        with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
            server.login(sent_from, logger_config.email_password)
            server.sendmail(
                sent_from, send_to, email_msg.as_string()
            )


    def _notify_via_slack(self, msg, time, log_level, logger_config: LoggerConfig):
        ''' Logs an event via slack based off the slack settings stored in the logger config. '''
        slack = Slack(logger_config)
        slack_msg = f'{log_level} - {time}:\n{msg}'
        slack.post_message(slack_msg)


    def _log(self, msg, log_level, logger_config: LoggerConfig):
        ''' The log method responsible for determining which log methods will be triggered for this log event. '''
        try:
            now = datetime.now()
            date = now.strftime('%Y-%m-%d')
            time = now.strftime('%H:%M:%S')

            if LogMethods.CONSOLE in logger_config.log_methods:
                self._print_log_to_console(msg, time, log_level)

            if LogMethods.FILE in logger_config.log_methods:
                self._write_log_to_file(msg, date, time, log_level, logger_config)

            if LogMethods.EMAIL in logger_config.log_methods:
                self._notify_via_email(msg, date, time, log_level, logger_config)

            if LogMethods.SLACK in logger_config.log_methods:
                self._notify_via_slack(msg, time, log_level, logger_config)

        except Exception: #  Catch all exceptions and report to console to avoid failing actual tests.
            _, _, trace_back = sys.exc_info()
            traceback.print_tb(trace_back) # Fixed format
            tb_info = traceback.extract_tb(trace_back)
            _, line, _, text = tb_info[-1]

            err_msg = f'Logger failed on line: {line} with error text: {text}'
            self._print_log_to_console(err_msg, time, LogLevels.ERROR)


    def error(self, msg):
        ''' Create a log event with the highest level 'error'. '''
        if LogLevels.ERROR not in self.trav_con.logger_settings.log_levels:
            return
        self._log(msg, LogLevels.ERROR, self.trav_con.logger_settings)


    def alert(self, msg):
        ''' Create a log event on level 'alert'. '''
        if LogLevels.ALERT not in self.trav_con.logger_settings.log_levels:
            return
        self._log(msg, LogLevels.ALERT, self.trav_con.logger_settings)


    def warning(self, msg):
        ''' Create a log event on level 'alert'. '''
        if LogLevels.WARNING not in self.trav_con.logger_settings.log_levels:
            return
        self._log(msg, LogLevels.WARNING, self.trav_con.logger_settings)


    def debug(self, msg):
        '''
            The 'debug' log event level will only trigger a log event if 'debug' is in the log levels in the logger config
            OR if debug is enabled in the executor config.
        '''
        if LogLevels.DEBUG not in self.trav_con.logger_settings.log_levels or self.trav_con.debug_enabled is False:
            return
        self._log(msg, LogLevels.DEBUG, self.trav_con.logger_settings)


    def custom(self, msg):
        '''
            This will log a custom error using the config you defined in your logger config "customLoggerConfig" key. If there is
            no custom log defined this method will do nothing.
        '''
        if self.trav_con.logger_settings.custom_logger_config == '':
            return

        self._log(msg, 'custom', self.trav_con.logger_custom_settings)
