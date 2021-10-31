''' This module will assist with test data generation, particularly random data such as full names, phone numbers etc. '''
import random
import codecs
import platform
from os.path    import realpath, dirname
from csv        import reader


CURRENT_DIR = dirname(realpath(__file__))

class TestData:
    ''' Main test data class that can be imported and used to generate test data easily. '''
    def __init__(self):
        if platform.system() == 'Windows':
            self.first_name_dir = f'{CURRENT_DIR}\\test_data\\first_names.csv'
            self.last_name_dir = f'{CURRENT_DIR}\\test_data\\last_names.csv'
            self.company_name_dir = f'{CURRENT_DIR}\\test_data\\company_names.csv'
        else:
            self.first_name_dir = f'{CURRENT_DIR}/test_data/first_names.csv'
            self.last_name_dir = f'{CURRENT_DIR}/test_data/last_names.csv'
            self.company_name_dir = f'{CURRENT_DIR}/test_data/company_names.csv'

        with codecs.open(self.first_name_dir, encoding='utf-8-sig') as open_file:
            self.first_names = tuple(reader(open_file))

        with open(self.last_name_dir, 'r') as open_file:
            self.last_names = tuple(reader(open_file))

        with codecs.open(self.company_name_dir, encoding='utf-8-sig') as open_file:
            self.company_names = tuple(reader(open_file))

    def get_random_first_name(self):
        ''' Gets a random first name and returns it as a string type. '''
        return random.choice(self.first_names)[0]

    def get_random_last_name(self):
        ''' Gets a random last name and returns it as a string type. '''
        return random.choice(self.last_names)[0]

    def get_random_company_name(self):
        ''' Returns a random company name. '''
        # Remove sql conflicting characters
        name = random.choice(self.company_names)[0].replace("'", "")
        return name
