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

# http://www.epochconverter.com/ - grab the millisecond version
eh_data = app.engagement_history(from_epoch='1485177300000', to_epoch='1485213300000')
print(str(eh_data['errors'])) if eh_data['errors'] else print('ok')

rt_data = app.realtime_operational(minute_timeframe='60', in_buckets_of='15')
print(str(rt_data['errors'])) if rt_data['errors'] else print('Main data: ok')
for method in rt_data['success']:
    details = method + 'data: '
    print(details + str(rt_data['success'][method]['errors'])) if rt_data['success'][method]['errors'] else print(details + 'ok')

users_data = app.users()
print(str(users_data['errors'])) if users_data['errors'] else print('ok')

skills_data = app.skills()
print(str(skills_data['errors'])) if skills_data['errors'] else print('ok')

agent_groups_data = app.agent_groups()
print(str(agent_groups_data['errors'])) if agent_groups_data['errors'] else print('ok')
