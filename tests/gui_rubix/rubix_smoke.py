
''' This is a test module where a test class will be stored. '''
from core.core_models                       import TestDefinition, TraverseConfig
from driver.driver_interface                import DriverActions
from utilities.test_data                    import TestData


class Tests:
    ''' This test class holds test methods. The name of the class must remain exactly "Tests" for the core to pick it up. '''
    def __init__(self, traverse_config: TraverseConfig, test_definition: TestDefinition):
        self.trav_con = traverse_config
        self.test_def = test_definition
        self.driver = DriverActions(self.test_def, 'rubix') # Add the name of your hooks file here if applicable
        self.test_data = TestData()


    def login_successfully(self):
        ''' Will attempt to login to rubix and confirm successful navigation to home page. '''
        # Setup
        self.driver.launch_url('https://exchange.staging.rubix.io/auth')
        self.driver.wait_for_element_visible('signIn_btn')

        # Execute
        self.driver.fill_in_field('test1k@yopmail.com', 'signIn_username')
        self.driver.fill_in_field('Test@2006', 'signIn_password')
        self.driver.select_element('signIn_btn')

        # Assert
        self.driver.wait_for_element_visible('dashboard')
        self.driver.wait_for_element_visible('dashboard_fund')
        self.driver.wait_for_element_visible('dashboard_trade')
        self.driver.wait_for_element_visible('dashboard_withdraw')
        self.driver.wait_for_element_visible('dashboard_transaction_trades')
        self.driver.wait_for_element_visible('dashboard_transaction_deposits')
        self.driver.wait_for_element_visible('dashboard_transaction_withdrawals')
        self.driver.wait_for_element_visible('dashboard_explore_market')

        self.driver.take_screenshot()


    def click_market(self):
        '''Will click on market link and will verify market page is open'''
        # Setup
        self.login_successfully()

        # Execute
        self.driver.select_element('market')

         # Assert
        self.driver.wait_for_element_visible('market_page')
        self.driver.take_screenshot()


    def click_portfolio(self):
        '''Will click on market link and will verify market page is open'''
        # Setup
        self.login_successfully()

        # Execute
        self.driver.select_element('portfolio')

         # Assert
        self.driver.wait_for_element_visible('portfolio_page')
        self.driver.take_screenshot()


    def click_receive(self):
        '''Will click on market link and will verify market page is open'''
        # Setup
        self.login_successfully()

        # Execute
        self.driver.select_element('receive')

         # Assert
        self.driver.wait_for_element_visible('receive_popup')
        self.driver.take_screenshot()

    
    def click_send(self):
        '''Will click on market link and will verify market page is open'''
        # Setup
        self.login_successfully()

        # Execute
        self.driver.select_element('send')

         # Assert
        self.driver.wait_for_element_visible('send_popup')
        self.driver.take_screenshot()

    def click_settings(self):
        '''Will click on market link and will verify market page is open'''
        # Setup
        self.login_successfully()

        # Execute
        self.driver.select_element('user_menu')
        self.driver.select_element('settings')

         # Assert
        self.driver.wait_for_element_visible('settings_page')
        self.driver.take_screenshot()

    def click_logout(self):
        '''Will click on market link and will verify market page is open'''
        # Setup
        self.login_successfully()

        # Execute
        self.driver.select_element('user_menu')
        self.driver.select_element('logout')

         # Assert
        self.driver.wait_for_element_visible('signIn_btn')
        self.driver.take_screenshot()
