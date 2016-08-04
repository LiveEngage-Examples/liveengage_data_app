import liveengage_data_app as le_api

def get_skills(application):
    skills_data = application.get_skills_data()
    print(str(skills_data['errors'])) if skills_data['errors'] else print('ok')
    account_skills = [{}]
    for skill in skills_data:
        account_skills.append({
            'id': skill['id'],
            'name': skill['name'],
            })
    return account_skills

def get_users(application):
    users_data = application.get_user_data()
    print(str(users_data['errors'])) if users_data['errors'] else print('ok')
    account_agents = [{}]
    for user in users_data:
        account_agents.append({
            'fullName': user['fullName'],
            'id': user['id'],
            'memberOf': user['memberOf']['agentGroupId'],
            'skills': user['skillIds'],
            })
    return account_agents

def get_groups(application):
    agent_groups_data = app.get_agent_groups_data()
    print(str(agent_groups_data['errors'])) if agent_groups_data['errors'] else print('ok')
    account_groups = [{}]
    for group in agent_groups_data:
        account_groups.append({
            'id': group['id'],
            'name': group['name'],
            })
    return account_groups

def enrich_users_data(groups, skills, users):
    for user in users:
        for group in groups:
            if user['memberOf'] == group['id']:
                user['memberOf'] = group
        for skill in skills:
            if skill in user['skills']:
                user['skills'] = skill
    return users

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
                                #'accountConfigReadOnly_skills',
                                'accountConfigReadOnly_users',
                                #'accountConfigReadOnly_agentGroups'
                            ])
print(str(app))

# Grab data for the timeframe of the last 24 hours. Put the data in only one bucket.
rt_data = app.get_rt_operational_data(minute_timeframe='1440', in_buckets_of='1440')
print(str(rt_data['errors'])) if rt_data['errors'] else print('Main data: ok')
for method in rt_data['success']:
    details = method + 'data: '
    print(details + str(rt_data['success'][method]['errors'])) if rt_data['success'][method]['errors'] else print(details + 'ok')

agent_data = enrich_users_data(
    get_groups(app), 
    get_skills(app), 
    get_agents(app),
    )

# Need to write functions below this line
agent_csv = build_agent_csv(rt_data['agentactivity'], agent_data)
queue_csv = build_queue_csv(rt_data['queuehealth'], agent_data)
eng_activity_csv = build_eng_activity_csv(rt_data['engactivity'], agent_data)

mail_reports([agent_csv, queue_csv, eng_activity_csv])