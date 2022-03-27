
''' This is a test module where a test class will be stored. '''
import requests
import json
from core.core_models                       import TestDefinition, TraverseConfig
from driver.driver_interface                import DriverActions
from utilities.test_data                    import TestData


class Tests:
    ''' This test class holds test methods. The name of the class must remain exactly "Tests" for the core to pick it up. '''
    def __init__(self, traverse_config: TraverseConfig, test_definition: TestDefinition):
        self.trav_con = traverse_config
        self.test_def = test_definition
        #self.driver = DriverActions(self.test_def, '') # Add the name of your hooks file here if applicable
        self.test_data = TestData()


    def get_name_only(self):
        ''' Ensure valid response from API using a name only. '''
        # Setup
        url = f'https://api.agify.io?name={self.test_def.test_config_value}'

        # Execute
        response = requests.get(url)
        response_body = json.loads(response.content)

        # Assert
        assert response.status_code == 200
        assert response_body['name'] == self.test_def.test_config_value
        assert response_body['age'] > 0
        assert response_body['count'] > 0


    def get_name_and_country(self):
        ''' Ensure valid response from API using a name and country parameter. '''
        # Setup
        country_code = 'US'
        url = f'https://api.agify.io?name={self.test_def.test_config_value}&country_id={country_code}'

        # Execute
        response = requests.get(url)
        response_body = json.loads(response.content)

        # Assert
        assert response.status_code == 200
        assert response_body['name'] == self.test_def.test_config_value
        assert response_body['age'] > 0
        assert response_body['count'] > 0
        assert response_body['country_id'] == country_code
