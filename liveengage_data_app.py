# liveengage_data_app.py
# python=3.5
"""A small, unofficial wrapper for LiveEngage data retrieval APIs
This wrapper module can be imported into your script to
provide a cleaner interface for working with LiveEngage APIs

#Installation
The liveengage_data_app module is not hosted anywhere other than on github. To use it, you should:
- git clone https://github.com/WildYorkies/LiveEngageDataApp
- place the liveengage_data_app.py file in your project
  directory on the same level as your own script
- And import the file into your own python script with
  `import liveengage_data_app` or `from liveengage_data_app import LiveEngageDataApp`

#Dependencies
In order to import and run liveengage_data_app you will need Python 3.
You will also need to install the following Python libraries via conda/pip/etc:
- requests
- requests_oauthlib
"""
import json
import requests
from requests_oauthlib import OAuth1

class LiveEngageDataApp:
    """LiveEngageDataApp has a constructor and 6 methods.
    This class is meant for only retrieving data from LiveEngage.
    It does not yet work for changing or deleting data on your account.
    """

    def __init__(self, account_number, keys_and_secrets, services):
        """Initializer takes in 3 arguments and returns an app object.
        - LiveEngage Account Number
          - You use your LiveEngage account number to log in to the platform.
        - Keys and Secrets for your LiveEngage app
        - This is a Dictionary of strings. You should not change the dictionary
            keys, but you should update the dictionary values with your own.
          - You can get your keys and secrets when you create your own API app in LiveEngage
        - Services that you will use with the app
          - There is a set list of services that you can use. Do not change the names of these
            services, just comment out or remove the ones that you are not using.
          - When you create your own API app in LiveEngage, you can select which services to use.
            You'll see that we only allow the usage of services that retrieve data in this app.
            - Select "advanced" when setting this up in LiveEngage and
              select "read only" for the skills/users/agentGroups
        """

        self.account_number = account_number
        self.keys_and_secrets = keys_and_secrets
        self.postheader = {'content-type': 'application/json'}
        self.services = {service : '' for service in services}
        self._set_service_URIs()
        self.oauth = OAuth1(keys_and_secrets['consumer_key'],
                            client_secret=keys_and_secrets['consumer_secret'],
                            resource_owner_key=keys_and_secrets['token_key'],
                            resource_owner_secret=keys_and_secrets['token_secret'],
                            signature_method='HMAC-SHA1',
                            signature_type='auth_header')

    def __str__(self):
        """Allows you to print a neat representation of your
        LiveEngageDataApp object for debugging purposes.
        """

        string_rep = '\nApp object with the following data:'
        string_rep += '\n  account_number: ' + self.account_number

        for name, token in self.keys_and_secrets.items():
            string_rep += '\n  ' + name + ' : ' + token

        for service, uri in self.services.items():
            string_rep += '\n  ' + service + ' : '
            if isinstance(uri, dict):
                for s, u in uri.items():
                    string_rep += '\n    ' + s + ' : ' + u
            else:
                string_rep += uri

        return string_rep

    def _get_request_helper(self, url_string):
        """Takes in a url,
        Does a get request on it (using the app object's header and oauth),
        Returns a tuple of the HTTP response and any possible errors
        """

        req = requests.get(url=url_string, headers=self.postheader, auth=self.oauth)
        error = ''
        resp = {}

        if not req.ok:
            error = 'HTTP Status: ' + str(req.status_code)
        else:
            resp = req.json()

        return (resp, error)

    def _set_service_URIs(self):
        """Cycles through the list of services that the app is meant to use,
        Matches each service to its appropriate base_uri
        """

        for service, uri  in self.services.items():
            domain_req = ''

            if 'accountConfigReadOnly' in service:
                domain_req = requests.get('https://api.liveperson.net/api/account/' +
                                          self.account_number + '/service/' +
                                          service.split('_')[0] + '/baseURI.json?version=1.0')
            else:
                domain_req = requests.get('https://api.liveperson.net/api/account/' +
                                          self.account_number + '/service/' +
                                          service + '/baseURI.json?version=1.0')

            if not domain_req.ok:
                uri = 'Bad Request: ' + str(domain_req.status_code)
            else:
                domain = domain_req.json()

                if service == 'engHistDomain':
                    uri = ('https://' + domain['baseURI'] + '/interaction_history/api/account/' +
                           self.account_number + '/interactions/search?')
                elif service == 'leDataReporting':
                    uri_list = {}
                    uri_list['queueHealth'] = ('https://' + domain['baseURI'] + '/operations/api/account/' +
                                               self.account_number + '/queuehealth?')
                    uri_list['engactivity'] = ('https://' + domain['baseURI'] + '/operations/api/account/' +
                                               self.account_number + '/engactivity?')
                    uri_list['agentactivity'] = ('https://' + domain['baseURI'] + '/operations/api/account/' +
                                                 self.account_number + '/agentactivity?')
                    uri = uri_list
                elif service == 'accountConfigReadOnly_users':
                    uri = ('https://' + domain['baseURI'] + '/api/account/' +
                           self.account_number + '/configuration/le-users/users')
                elif service == 'accountConfigReadOnly_skills':
                    uri = ('https://' + domain['baseURI'] + '/api/account/' +
                           self.account_number + '/configuration/le-users/skills')
                elif service == 'accountConfigReadOnly_agentGroups':
                    uri = ('https://' + domain['baseURI'] + '/api/account/' +
                           self.account_number + '/configuration/le-users/agentGroups')
                else:
                    uri = 'Did not understand service name'

            self.services[service] = uri

    def engagement_history(self, from_epoch, to_epoch):
        """#Arguments
        This method takes two string arguments of epoch milliseconds. 

        #Returns
        This method returns a dictionary of data['success'] and data['errors']. 
        The 'success' item is a list of dictionaries. Each dictionary representing one chat record. 
        The 'errors' item is a list or errors.
        """

        print('\nGetting engHistDomain data...')

        data = {'success': [], 'errors': []}

        if 'engHistDomain' not in self.services.keys():
            data['errors'].append('No Engagement History service found')
            return data
        else:
            count = 1 # total num of records in the response
            offset = 0 # amount difference between what we've pulled so far and what the total is.
            limit = 100 # max chats to be recieved in one response
            number_chats = 0

            body = {
                'interactive':'true',
                'ended':'true',
                'start':{
                    'from':from_epoch,
                    'to':to_epoch
                },
            }

            with requests.session() as client:
                while offset <= count:
                    params = {'offset':offset, 'limit':limit, 'start':'des'}

                    eng_hist_response = client.post(url=self.services['engHistDomain'],
                                                    headers=self.postheader,
                                                    data=json.dumps(body),
                                                    auth=self.oauth,
                                                    params=params)

                    if not eng_hist_response.ok:
                        data['errors'].append('HTTP Status: ' + str(eng_hist_response.status_code))
                        return data

                    eng_hist_results = eng_hist_response.json()

                    for chat in eng_hist_results['interactionHistoryRecords']:
                        number_chats += 1
                        data['success'].append(chat)

                    count = eng_hist_results['_metadata']['count']
                    offset += limit
                    print(str(offset) + ' <= ' + str(count), end='\r')

                print('Chats Processed: ' + str(number_chats), end='\r')
                print('')

                return data

    def realtime_operational(self, minute_timeframe, in_buckets_of):
        """#Arguments
        This method takes two string arguments. 
        minute_timeframe can be up to 1440 and as low as 5. 
        in_buckets_of is how you want to group the data. 
        If you just want one grouping, make it the same as the timeframe.

        #Returns
        This method returns a dictionary of data['success'] and data['errors']. 
        The 'success' item in the dictionary is a dictionary for the three methods of the Real Time API
            eg. rt_data['success']['queueHealth'], rt_data['success']['agentactivity'], rt_data['success']['engactivity'])
        The 'errors' item is a list of errors.

        Each of the three method returns (queueHealth, agentActivity, engactivity) also 
        have 'success' and 'errors' items attached to them. The main data is in 'success', any errors are in 'errors'.
        """

        print('\nGetting Real Time Operational Data...')

        data = {'success': {}, 'errors': []}

        if 'leDataReporting' not in self.services.keys():
            data['errors'].append('No Real Time Operational Data service found')
            return data

        if int(in_buckets_of) > int(minute_timeframe) or int(minute_timeframe) % int(in_buckets_of) != 0:
            data['errors'].append('Buckets must be smaller or equal to timeframe and also a divisor of timeframe.')
            return data

        params = ''
        for name, uri in self.services['leDataReporting'].items():
            data['success'][name] = {}

            if name == 'queuehealth':
                params = ('timeframe=' + minute_timeframe + '&interval=' +
                          in_buckets_of + 'skillIds=all&v=1')
            elif name == 'agentactivity':
                params = ('timeframe=' + minute_timeframe + '&interval=' +
                          in_buckets_of + '&agentIds=all&v=1')
            else:
                params = ('timeframe=' + minute_timeframe + '&interval=' +
                          in_buckets_of + '&skillIds=all&agentIds=all&v=1')

            data['success'][name]['success'], data['success'][name]['errors'] = self._get_request_helper(uri + params)

            print('\tAdded data from ' + name)

        return data

    def users(self):
        """Returns a dictionary of data['success'] and data['errors']. 
        The 'success' item in the returns will contain the actual data from a successful call of the method.
        """

        print('\nGetting user data...')

        data = {'success': [], 'errors': []}
        enriched_data = {'success': [], 'errors': []}
        num_agents = 0

        if 'accountConfigReadOnly_users' not in self.services.keys():
            data['errors'].append('No user data service found')
            return data

        data['success'], data['errors'] = self._get_request_helper(self.services['accountConfigReadOnly_users'])

        if data['errors']:
            return data

        with requests.session() as client:
            for agent in data['success']:
                url_string = self.services['accountConfigReadOnly_users'] + '/' + str(agent['id'])
                req = client.get(url=url_string, headers=self.postheader, auth=self.oauth)
                if not req.ok:
                    enriched_data['errors'].append('HTTP Status: ' + str(req.status_code))
                else:
                    enriched_data['success'].append(req.json())
                num_agents += 1
                print('Users Processed ' + str(num_agents), end='\r')
        print('')

        return enriched_data

    def skills(self):
        """Returns a dictionary of data['success'] and data['errors']. 
        The 'success' item in the returns will contain the actual data from a successful call of the method.
        """

        print('\nGetting skill data...')

        data = {'success': {}, 'errors': []}

        if 'accountConfigReadOnly_skills' not in self.services.keys():
            data['errors'].append('No skill data service found')
            return data

        data['success'], data['errors'] = self._get_request_helper(self.services['accountConfigReadOnly_skills'])
        return data

    def agent_groups(self):
        """Returns a dictionary of data['success'] and data['errors']. 
        The 'success' item in the returns will contain the actual data from a successful call of the method.
        """

        print('\nGetting agent group data...')

        data = {'success': {}, 'errors': []}

        if 'accountConfigReadOnly_agentGroups' not in self.services.keys():
            data['errors'].append('No agent groups data service found')
            return data

        data['success'], data['errors'] = self._get_request_helper(self.services['accountConfigReadOnly_agentGroups'])

        return data
