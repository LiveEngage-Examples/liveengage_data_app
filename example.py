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

# http://www.epochconverter.com/ - grab the millisecond version
eh_data = app.get_eng_hist_data(from_epoch='1469419200000', to_epoch='1469505599000')
print(str(eh_data[-1]).encode('UTF8'))

rt_data = app.get_rt_operational_data(minute_timeframe='60', in_buckets_of='15')
if rt_data['Error']:
  print(rt_data['Error'])

users_data = app.get_user_data()
skills_data = app.get_skills_data()
agent_groups_data = app.get_agent_groups_data()
print(str(users_data))
print(str(skills_data))
print(str(agent_groups_data))
