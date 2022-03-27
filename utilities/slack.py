''' This is the slack utility to help make calls to the Slack API a bit easier for automation.'''
import requests

from utilities.string_helper    import StringHelper
from core.core_models           import LoggerConfig


class Slack:
    ''' To use the Slack utility its important to enter the slack options itno the traverse logger config file. '''
    def __init__(self, logger_config: LoggerConfig) -> None:
        self.logger_config = logger_config

    def post_message(self, msg):
        ''' Posted a message via slack to the channel specified in the logger config. '''
        url = 'https://slack.com/api/chat.postMessage'
        users = StringHelper.add_chars_to_list_items_start_end(self.logger_config.slack_user_mentions, '<@', '>')

        headers = {
            'Authorization': f'Bearer {self.logger_config.slack_bearer_token}'
        }

        for channel in self.logger_config.slack_channels:
            body = {
                'channel': f'{channel}',
                'text': f'{StringHelper.convert_to_csv(users)}\n{msg}'
            }

            response = requests.post(headers=headers, json=body, url=url)

            if response.status_code != 200:
                raise Exception('Error occurred posting message to slack. Slack API did not return success')
