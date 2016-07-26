# liveengage_data_app.py
# python=3.5
import json
import requests
from requests_oauthlib import OAuth1
from requests_oauthlib import OAuth1Session
from typing import Dict, List

class LiveEngageDataApp:
    def __init__(self, account_number: str, keys_and_secrets: Dict[str,str], services: List[str]):
        self.account_number = account_number
        self.keys_and_secrets = keys_and_secrets
        self.services = {}
        for service in services:
            self.services[service] = ''
        self._set_service_URIs(self.services)
        self.oauth = OAuth1(keys_and_secrets['consumer_key'],
               client_secret=keys_and_secrets['consumer_secret'],
               resource_owner_key=keys_and_secrets['access_token'],
               resource_owner_secret=keys_and_secrets['access_token_secret'],
               signature_method='HMAC-SHA1',
               signature_type='auth_header')

    def _set_service_URIs(self):
        for service, URI  in self.services.items():
            domain_req = '' # initialize Request object
            if 'accountConfigReadOnly' in service:
                domain_req = requests.get('https://api.liveperson.net/api/account/' + self.account_number + '/service/' + service.split('_')[0] + '/baseURI.json?version=1.0')
            else:
                domain_req = requests.get('https://api.liveperson.net/api/account/' + self.account_number + '/service/' + service + '/baseURI.json?version=1.0')
            if not domain_req.ok:
                URI = 'Bad Request: ' + str(domainReq.status_code)
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
        data = []
        if 'engHistDomain' not in self.services.keys():
            data.append('No Engagement History service found')
            return data
        else:
            count = 1 # Count is the total num of records in the response
            offset = 0 # offset is to keep track of the amount difference between what we've pulled so far and what the total is.
            limit = 100 # max chats to be recieved in one response
            num_records = 0
            client = requests.session()
            postheader = {'content-type': 'application/json'}
            # Customize the body for what you want 
            body={
                'interactive':'true',
                'ended':'true',
                'start':{
                    # http://www.epochconverter.com/ - grab the millisecond version
                    'from':from_epoch, 
                    'to':to_epoch
                },
            }
            params={'offset':offset, 'limit':limit, 'start':'des'}
            while(offset <= count):
                engHistoryResponse = client.post(url=services['engHistDomain'], headers=postheader, data=json.dumps(body), auth=self.oauth, params=params)
                if not engHistoryResponse.ok:
                    data.append(engHistoryResponse.status_code)
                    return data
                engHistoryResults = engHistoryResponse.json()
                data.append(engHistoryResults['interactionHistoryRecords'])
                count = engHistoryResults['_metadata']['count']
                offset += limit
            return data