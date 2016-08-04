import liveengage_data_app as le_api

app = le_api.LiveEngageDataApp(account_number='xx',
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

# http://www.epochconverter.com/ - grab the millisecond version
eh_data = app.get_eng_hist_data(from_epoch='1469419200000', to_epoch='1469505599000')
print(str(eh_data['errors'])) if eh_data['errors'] else print('ok')

rt_data = app.get_rt_operational_data(minute_timeframe='60', in_buckets_of='15')
print(str(rt_data['errors'])) if rt_data['errors'] else print('Main data: ok')
for method in rt_data['success']:
    details = method + 'data: '
    print(details + str(rt_data['success'][method]['errors'])) if rt_data['success'][method]['errors'] else print(details + 'ok')

users_data = app.get_user_data()
print(str(users_data['errors'])) if users_data['errors'] else print('ok')

skills_data = app.get_skills_data()
print(str(skills_data['errors'])) if skills_data['errors'] else print('ok')

agent_groups_data = app.get_agent_groups_data()
print(str(agent_groups_data['errors'])) if agent_groups_data['errors'] else print('ok')