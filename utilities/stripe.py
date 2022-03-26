''' This module integrates into the stripe API for us. '''

import json
import requests

class StripeApi:
    '''
        Main class for calling the stripe API.
        Details on the responses expected from stripe can be found at: https://stripe.com/docs/api/
    '''

    def __init__(self, api_key) -> None:
        self.api_key = api_key
        self.base_url = 'https://api.stripe.com'


    def get_customers_all(self):
        '''
            Gets all the customers on stripe.
            Returns a tuple, the first being the response code and 2nd is the response content as a dictionary.
        '''
        response = requests.get(f'{self.base_url}/v1/customers', auth=(self.api_key, ''))
        return response.status_code, json.loads(response.content)


    def get_customer(self, customer_id:str):
        '''
            Gets the customer details for the provided customer id from stripe.
            Returns a tuple, the first being the response code and 2nd is the response content as a dictionary.
        '''
        response = requests.get(f'{self.base_url}/v1/customers/{customer_id}', auth=(self.api_key, ''))
        return response.status_code, json.loads(response.content)


    def get_subscription(self, subscription_id:str):
        '''
            Gets the subscription details for the provided subscription id from stripe.
            Returns a tuple, the first being the response code and 2nd is the response content as a dictionary.
        '''
        response = requests.get(f'{self.base_url}/v1/subscriptions/{subscription_id}', auth=(self.api_key, ''))
        return response.status_code, json.loads(response.content)

    def get_payment_intents(self, **parameters):
        '''
            Returns a list of payment intents from Stripe. You can pass in the parameter 'customer' and this will
            add it as a filter to the API call as per Stripe's documentation.
        '''
        if 'customer' in parameters:
            url = f"{self.base_url}/v1/payment_intents?customer={parameters.get('customer')}"

        response = requests.get(url, auth=(self.api_key, ''))
        return response.status_code, json.loads(response.content)

    def get_invoice(self, invoice_id):
        ''' Gets the invoice from Stripe for the invoice id passed in '''
        response = requests.get(f'{self.base_url}/v1/invoices/{invoice_id}', auth=(self.api_key, ''))
        return response.status_code, json.loads(response.content)
