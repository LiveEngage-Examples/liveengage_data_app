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
        self.postheader = {'content-type': 'application/json'}
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

    def _get_request_helper(self, url_string: str):
        req = requests.get(url=url_string, headers=self.postheader, auth=self.oauth)
        if not req.ok:
            return 'HTTP Status: ' + str(req.status_code)
        else:
            return req.json()

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
                    URIs = {}
                    URIs['queueHealth'] = 'https://' + domain_req.json()['baseURI'] + '/operations/api/account/' + self.account_number + '/queuehealth?'
                    URIs['engactivity'] = 'https://' + domain_req.json()['baseURI'] + '/operations/api/account/' + self.account_number + '/engactivity?'
                    URIs['agentactivity'] = 'https://' + domain_req.json()['baseURI'] + '/operations/api/account/' + self.account_number + '/agentactivity?'
                    URI = URIs
                elif service == 'accountConfigReadOnly_users':
                    URI = 'https://' + domain_req.json()['baseURI'] + '/api/account/' + self.account_number + '/configuration/le-users/users'
                elif service == 'accountConfigReadOnly_skills':
                    URI = 'https://' + domain_req.json()['baseURI'] + '/api/account/' + self.account_number + '/configuration/le-users/skills'
                elif service == 'accountConfigReadOnly_agentGroups':
                    URI = 'https://' + domain_req.json()['baseURI'] + '/api/account/' + self.account_number + '/configuration/le-users/agentGroups'
                else:
                    URI = 'Did not understand service name'
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
                    engHistoryResponse = client.post(url=self.services['engHistDomain'], headers=self.postheader, data=json.dumps(body), auth=self.oauth, params=params)
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

    # Returns a Dictionary for the three methods
    # eg. data['queueHealth'], data['agentactivity'], data['engactivity']
    def get_rt_operational_data(self, minute_timeframe: str, in_buckets_of: str):
        print('\nGetting Real Time Operational Data...')
        data = {}
        
        if 'leDataReporting' not in self.services.keys():
            data['Error'] = 'No Real Time Operational Data service found'
            return data
        if int(in_buckets_of) > int(minute_timeframe) or int(minute_timeframe) % int(in_buckets_of) != 0:
            data['Error'] = 'Buckets must be smaller or equal to timeframe and also a divisor of timeframe.'
            return data
        
        params = ''
        for name, URI in self.services['leDataReporting'].items():
            if name == 'queuehealth':
                params = 'timeframe=' + minute_timeframe + '&interval=' + in_buckets_of + 'skillIds=all&v=1'
            else:
                params = 'timeframe=' + minute_timeframe + '&interval=' + in_buckets_of + '&skillIds=all&agentIds=all&v=1'
            
            data[name] = self._get_request_helper(URI + params)
            print('\n\tAdded data from ' + name) 
        return data

    # Returns a Dictionary
    def get_user_data(self):
        print('\nGetting user data...')
        if 'accountConfigReadOnly_users' not in self.services.keys():
            return 'No user data service found'
        return self._get_request_helper(self.services['accountConfigReadOnly_users'])

    # Returns a Dictionary
    def get_skills_data(self):
        print('\nGetting skill data...')
        if 'accountConfigReadOnly_skills' not in self.services.keys():
            return 'No skill data service found'
        return self._get_request_helper(self.services['accountConfigReadOnly_skills'])

    # Returns a Dictionary   
    def get_agent_groups_data(self):
        print('\nGetting agent group data...')
        if 'accountConfigReadOnly_agentGroups' not in self.services.keys():
            return 'No agent groups data service found'
        return self._get_request_helper(self.services['accountConfigReadOnly_agentGroups'])