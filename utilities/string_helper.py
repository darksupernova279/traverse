''' This module will hold all string related functions, manipulation and/or operations '''

class StringHelper:
    ''' Main class for String Helper methods. '''
    @staticmethod
    def replace_email_domain(email, domain):
        ''' Pass in the email (original) and the domain you want instead (Not The Extension). This returns the updated email as a string. '''
        pos_a = email.index('@')
        pos_dot = email.rindex('.')
        return email.replace(email[pos_a:pos_dot], domain)

    @staticmethod
    def convert_to_csv(list_items):
        ''' Pass in a list and you will be returned a csv string. '''
        if isinstance(list_items, list):
            return ','.join(map(str, list_items))
