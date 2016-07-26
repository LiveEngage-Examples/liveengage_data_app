# liveengage_data_app.py
# python=3.5
import json
import requests
from requests_oauthlib import OAuth1
from typing import Dict, List

class LiveEngageDataApp:
    def __init__(self, account_number: str, keys_and_secrets: Dict[str,str], services: List[str]):
        self.account_number = account_number
        self.keys_and_secrets = keys_and_secrets
        self.services = {}
        for service in services:
            self.services[service] = ''
        self._set_service_URIs()
        self.oauth = OAuth1(keys_and_secrets['consumer_key'],
               client_secret=keys_and_secrets['consumer_secret'],
               resource_owner_key=keys_and_secrets['token_key'],
               resource_owner_secret=keys_and_secrets['token_secret'],
               signature_method='HMAC-SHA1',
               signature_type='auth_header')
        print("\nApp object created with the following data:")
        print('\n\taccount_number: ' + self.account_number)
        print('\n\tkeys_and_secrets: ' + str(self.keys_and_secrets))
        print('\n\tservices: ' + str(self.services))

    def _set_service_URIs(self):
        for service, URI  in self.services.items():
            domain_req = '' # initialize Request object
            if 'accountConfigReadOnly' in service:
                domain_req = requests.get('https://api.liveperson.net/api/account/' + self.account_number + '/service/' + service.split('_')[0] + '/baseURI.json?version=1.0')
            else:
                domain_req = requests.get('https://api.liveperson.net/api/account/' + self.account_number + '/service/' + service + '/baseURI.json?version=1.0')
            if not domain_req.ok:
                URI = 'Bad Request: ' + str(domain_req.status_code)
            else:
                if service == 'engHistDomain':
                    URI = 'https://' + domain_req.json()['baseURI'] + '/interaction_history/api/account/' + self.account_number + '/interactions/search?'
                elif service == 'leDataReporting':
                    URI = 'https://' + domain_req.json()['baseURI']
                elif service == 'accountConfigReadOnly_users':
                    URI = 'https://' + domain_req.json()['baseURI'] + '/api/account/' + self.account_number + '/configuration/le-users/users'
                elif service == 'accountConfigReadOnly_skills':
                    URI = 'https://' + domain_req.json()['baseURI'] + '/api/account/' + self.account_number + '/configuration/le-users/skills'
                elif service == 'accountConfigReadOnly_agentGroups':
                    URI = 'https://' + domain_req.json()['baseURI'] + '/api/account/' + self.account_number + '/configuration/le-users/agentGroups'

            self.services[service] = URI

    # Returns a List of Dictionaries that are chat records
    def get_eng_hist_data(self, from_epoch, to_epoch):
        print('\nGetting engHistDomain data...')
        data = []
        if 'engHistDomain' not in self.services.keys():
            data.append('No Engagement History service found')
            return data
        else:
            count = 1 # total num of records in the response
            offset = 0 # keep track of the amount difference between what we've pulled so far and what the total is.
            limit = 100 # max chats to be recieved in one response
            number_chats = 0
            postheader = {'content-type': 'application/json'}
            body={
                'interactive':'true',
                'ended':'true',
                'start':{
                    'from':from_epoch, 
                    'to':to_epoch
                },
            }
            with requests.session() as client:
                while(offset <= count):
                    params={'offset':offset, 'limit':limit, 'start':'des'}
                    engHistoryResponse = client.post(url=self.services['engHistDomain'], headers=postheader, data=json.dumps(body), auth=self.oauth, params=params)
                    if not engHistoryResponse.ok:
                        data.append('HTTP Status: ' + str(engHistoryResponse.status_code))
                        return data
                    engHistoryResults = engHistoryResponse.json()
                    for chat in engHistoryResults['interactionHistoryRecords']:
                        number_chats += 1
                        data.append(chat)
                    count = engHistoryResults['_metadata']['count']
                    offset += limit
                    print(str(offset) + ' <= ' + str(count))
                print ('Number of chats processed: ' + str(number_chats) + '\n')
                return data