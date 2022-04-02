
''' This is a test module where a test class will be stored. '''
from core.core_models                       import TestDefinition, TraverseConfig
from driver.driver_interface                import DriverActions
from utilities.test_data                    import TestData


class Tests:
    ''' This test class holds test methods. The name of the class must remain exactly "Tests" for the core to pick it up. '''
    def __init__(self, traverse_config: TraverseConfig, test_definition: TestDefinition):
        self.trav_con = traverse_config
        self.test_def = test_definition
        self.driver = DriverActions(self.test_def, 'swaglabs') # Add the name of your hooks file here if applicable
        self.test_data = TestData()


    def login_successfully(self):
        ''' Will attempt to login to swag labs and confirm successful navigation to home page. '''
        # Setup
        self.driver.launch_url('https://www.saucedemo.com/')
        self.driver.wait_for_element_visible('signIn_btn')

        # Execute
        self.driver.fill_in_field('standard_user', 'signIn_username')
        self.driver.fill_in_field('secret_sauce', 'signIn_password')
        self.driver.select_element('signIn_btn')

        # Assert
        self.driver.wait_for_element_visible('homepage_productsHeading')
        self.driver.take_screenshot()
