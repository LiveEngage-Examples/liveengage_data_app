No longer actively maintained. AFAIK, this still works just fine, but see the new developer site for more API information: 

https://developers.liveperson.com/documents.html

# LiveEngageDataApp
A small, *unofficial* wrapper for LiveEngage data retrieval APIs

This wrapper module can be imported into your script to provide a cleaner interface for working with LiveEngage APIs

[![asciicast](https://asciinema.org/a/bj5xttsjper9cbuk88r7ncuou.png)](https://asciinema.org/a/bj5xttsjper9cbuk88r7ncuou)

## Installation

`pip install liveengage_data_app`

### Dependencies

In order to import and run `liveengage_data_app` you will need Python 3. You will also need to install the following Python libraries via conda/pip/etc if pip does not already do that for you:
- requests
- requests_oauthlib

## Usage

This module exposes one `LiveEngageDataApp` class with 6 methods.

### Create an app
```python
from liveengage_data_app import LiveEngageDataApp

app = LiveEngageDataApp(account_number='xx',
                        keys_and_secrets={
                            'consumer_key':'xx',
                            'consumer_secret':'xx',
                            'token_key':'xx',
                            'token_secret':'xx'
                        },
                        services=[
                            'engHistDomain',
                            'leDataReporting',
                            'accountConfigReadOnly_skills',
                            'accountConfigReadOnly_users',
                            'accountConfigReadOnly_agentGroups'
                        ])
print(str(app))
```
#### Arguments
The initializer takes in 3 arguments
- LiveEngage Account Number
  - You use your LiveEngage account number to log in to the platform.
- Keys and Secrets for your LiveEngage app 
  - This is a Dictionary of strings. You should *not* change the dictionary keys, but you should update the dictionary values with your own.
  - You can get your keys and secrets when you create your own API app in LiveEngage
- Services that you will use with the app
  - There is a set list of services that you can use. Do not change the names of these services, just comment out or remove the ones that you are not using.
  - When you create your own API app in LiveEngage, you can select which services you want to use. You'll see that we only allow the usage of services that retrieve data in this app.
    - Select "advanced" when setting this up in LiveEngage and select "read only" for the skills/users/agentGroups

### Get Engagement History Data
```python
eh_data = app.engagement_history(from_epoch='1485177300000', to_epoch='1485213300000')

print(str(eh_data['errors'])) if eh_data['errors'] else print('ok')
```
#### Arguments
This method takes two string arguments of epoch milliseconds. You can use a service like [this one](http://www.epochconverter.com/ - grab the millisecond version) to convert a normal date to epoch milliseconds.

#### Returns
This method returns a dictionary of `data['success']` and `data['errors']`. The 'success' item is a list of dictionaries. Each dictionary representing one chat record. The 'errors' item is a list or errors.


### Get Real Time Operational Data
```python
rt_data = app.realtime_operational(minute_timeframe='60', in_buckets_of='15')

print(str(rt_data['errors'])) if rt_data['errors'] else print('Main data: ok')

for method in rt_data['success']:
    details = method + 'data: '
    print(details + str(rt_data['success'][method]['errors'])) if rt_data['success'][method]['errors'] else print(details + 'ok')
```
#### Arguments 
This method takes two string arguments. `minute_timeframe` can be up to 1440 and as low as 5. `in_buckets_of` is how you want to group the data. If you just want one grouping, make it the same as the timeframe.

#### Returns
This method returns a dictionary of `data['success']` and `data['errors']`. The 'success' item in the dictionary is a dictionary for the three methods of the Real Time API (eg. `rt_data['success']['queueHealth']`, `rt_data['success']['agentactivity']`, `rt_data['success']['engactivity']`). The 'errors' item is a list or errors.

Each of the three method returns (queueHealth, agentActivity, engactivity) also have 'success' and 'errors' items attached to them. The main data is in 'success', any errors are in 'errors'.

### Get Users / Skills / Agent Groups Data
```python
users_data = app.users()
print(str(users_data['errors'])) if users_data['errors'] else print('ok')

skills_data = app.skills()
print(str(skills_data['errors'])) if skills_data['errors'] else print('ok')

agent_groups_data = app.agent_groups()
print(str(agent_groups_data['errors'])) if agent_groups_data['errors'] else print('ok')
```
#### Returns
These methods return a dictionary of `data['success']` and `data['errors']`. The 'success' item in the returns will contain the actual data from a successful call of the method.
