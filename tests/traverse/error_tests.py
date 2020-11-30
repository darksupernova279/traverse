''' This is a test module where a test class will be stored. '''

class Tests:
    ''' This test class holds test methods. The name of the class must reamin exactly "Tests" for the core to pick it up. '''
    def __init__(self, traverse_config, test_definition):
        self.t_config = traverse_config
        self.t_def = test_definition


    def error_divide_by_zero(self):
        ''' This method triggers a divide by 0 error '''
        print(1 / 0)


    def error_timeout(self):
        ''' This method triggers a timeout error '''
        raise TimeoutError


    def error_type_error(self):
        ''' This method triggers a type error '''
        raise TypeError


    def error_assertion(self):
        ''' This method triggers a type error '''
        assert 1 == 2
