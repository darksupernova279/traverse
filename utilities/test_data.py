''' This module will assist with test data generation, particularly random data such as full names, phone numbers etc. '''
import random
import codecs
from os.path    import realpath, dirname
from csv        import reader


CURRENT_DIR = dirname(realpath(__file__))

class TestData:
    ''' Main test data class that can be imported and used to generate test data easily. '''
    def __init__(self):
        with codecs.open(f'{CURRENT_DIR}\\test_data\\first_names.csv', encoding='utf-8-sig') as open_file:
            self.first_names = tuple(reader(open_file))

        with open(f'{CURRENT_DIR}\\test_data\\last_names.csv', 'r') as open_file:
            self.last_names = tuple(reader(open_file))

        with codecs.open(f'{CURRENT_DIR}\\test_data\\company_names.csv', encoding='utf-8-sig') as open_file:
            self.company_names = tuple(reader(open_file))

    def get_random_first_name(self):
        ''' Gets a random first name and returns it as a string type. '''
        return random.choice(self.first_names)[0]

    def get_random_last_name(self):
        ''' Gets a random last name and returns it as a string type. '''
        return random.choice(self.last_names)[0]

    def get_random_company_name(self):
        ''' Returns a random company name. '''
        return random.choice(self.company_names)[0]

