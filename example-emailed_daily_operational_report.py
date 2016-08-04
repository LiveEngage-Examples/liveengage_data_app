import liveengage_data_app as le_api

app = le_api.LiveEngageDataApp(account_number='xx',
                            keys_and_secrets={
                                'consumer_key':'xx',
                                'consumer_secret':'xx',
                                'token_key':'xx',
                                'token_secret':'xx'
                            },
                            services=[
                                #'engHistDomain',
                                'leDataReporting',
                                'accountConfigReadOnly_skills',
                                #'accountConfigReadOnly_users',
                                'accountConfigReadOnly_agentGroups'
                            ])
print(str(app))

# Grab data for the timeframe of the last 24 hours.
# Put the data in only one bucket.
rt_data = app.get_rt_operational_data(minute_timeframe='1440', in_buckets_of='1440')
print(str(rt_data['errors'])) if rt_data['errors'] else print('Main data: ok')
for method in rt_data['success']:
    details = method + 'data: '
    print(details + str(rt_data['success'][method]['errors'])) if rt_data['success'][method]['errors'] else print(details + 'ok')

agent_groups_data = app.get_agent_groups_data()
print(str(agent_groups_data['errors'])) if agent_groups_data['errors'] else print('ok')

skills_data = app.get_skills_data()
print(str(skills_data['errors'])) if skills_data['errors'] else print('ok')
