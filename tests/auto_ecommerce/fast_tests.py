''' These tests are FAST (Functional Acceptance Simple Tests) for a test commerce site to demonstrate the usage of this framework and to be used
    when testing changes on the framework to ensure nothing is broken. '''
from driver.driver_interface import DriverActions


class Tests:
    ''' This test class holds test methods. The name of the class must reamin exactly "Tests" for the core to pick it up. '''
    def __init__(self, traverse_config, test_definition):
        # The traverse config is avaialble for use in tests for any custom work that may need values stored in the config
        self.t_config = traverse_config

        # The Config you set in the "tests_config" json file are stored in the test definition here and can be accessed by tests.
        self.t_def = test_definition

        # This is where we bring in the selenium driver for use in all tests in this class. Note I am passing a hook file name to Driver Actions,
        # this is for me to make use of a simplified way to write tests. See details in the Hooks class in the driver_interface. Note that passing in
        # the hook file name is optional, and you are welcome to skip using it but then pass in elements and their locators yourself to Driver Actions
        self.driver = DriverActions(self.t_def.platform, self.t_def.capability, 'auto_ecommerce')


    def load_auto_practice(self):
        ''' Launches the website, waits for it to complete loading, then takes a screenshot '''
        self.driver.launch_url('http://automationpractice.com/')

        # Here I simply take a screenshot and pass in the saved screenshot directory from the test definition
        self.driver.take_screenshot(self.t_def.screenshot_dir)


    def search_for_item(self):
        '''  '''
        # Prepare
        # This is a good demonstration where I use a previous test to get to a certain state so I can do this test, good code reuse
        self.load_auto_practice()

        # Execute
        # Now I continue with this test
        self.driver.fill_in_field('Shirt', 'homepageSearchField')
        self.driver.select_element('homepageSearchBtn')
        self.driver.wait_for_element_visible('searchResultFirstItem')

        # Assert
        num_of_results = self.driver.get_element_text('searchResultsCount')
        assert '1 result has been found.' in num_of_results


    def select_category_dresses(self):
        '''  '''
        self.load_auto_practice()
        self.driver.select_element('homepageCatDresses')
        self.driver.wait_for_element_visible('categoryProductCount')
        self.driver.take_screenshot(self.t_def.screenshot_dir)


    def browser_back_to_homepage(self):
        '''  '''
        # Prepare
        self.load_auto_practice()

        # Execute
        self.driver.select_element('homepageCatDresses')
        self.driver.wait_for_element_visible('categoryProductCount')
        self.driver.take_screenshot(self.t_def.screenshot_dir)
        self.driver.browser_back()
        self.driver.wait_for_element_visible('homepageSearchBtn')

        # Assert
        self.driver.take_screenshot() # Notice I pass no screenshot directory here. This makes the driver save to the default which is C:\Driver


    def add_to_cart_and_view_checkout(self):
        ''' This test will search for an item, add it to the cart and begin the checkout process but not complete it. It validates the item
            is added to the cart successfully, and the user can proceed to the checkout and the total ammount to be billed is expected '''
        # Prepare
        self.load_auto_practice()
        self.select_category_dresses()

        # Execute
        self.driver.hover_over_element('categoryFirstItem')
        self.driver.select_element('itemAddToCartBtn')
        self.driver.wait_for_element_visible('itemAddToCartSuccessMsg')
        self.driver.select_element('itemAddToCartProceedToCheckoutBtn')
        self.driver.wait_for_element_visible('checkoutSummaryTitle')

        # Assert
        product_num = self.driver.get_element_text('checkoutSummaryNumOfProducts')
        total_amount = self.driver.get_element_text('checkoutSummaryTotalAmount')

        assert product_num == '1 Product'
        assert total_amount == '$28.00'
