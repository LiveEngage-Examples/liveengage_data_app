import liveengage_data_app as le_api
import pandas

def get_skills(application):
    skills_data = application.get_skills_data()
    print(str(skills_data['errors'])) if skills_data['errors'] else print('ok')
    account_skills = {}
    for skill in skills_data['success']:
        account_skills.update({
            skill['id']: skill['name']
            })
    return account_skills

def get_users(application):
    users_data = application.get_user_data()
    print(str(users_data['errors'])) if users_data['errors'] else print('ok')
    account_agents = []
    for user in users_data['success']:
        account_agents.append({
            'fullName': user['fullName'],
            'id': user['id'],
            'memberOf': user.get('memberOf', ''),
            'skills': user['skillIds'],
            })
    return account_agents

def get_groups(application):
    agent_groups_data = application.get_agent_groups_data()
    print(str(agent_groups_data['errors'])) if agent_groups_data['errors'] else print('ok')
    account_groups = {}
    for group in agent_groups_data['success']:
        account_groups.update({
            group['id']: group['name'],
            })
    return account_groups

def make_agent_df(agent_activity, engagement_activity, user_data, group_data):
    agent_index = [agent for agent in agent_activity.keys()]
    engag_index = [agent for agent in engagement_activity.keys()]
    index = list(set().union(agent_index, engag_index))
    columns = ['agentName', 'agentGroup', 'totalInteractiveChats', 'totalNonInteractiveChats', 'connectedEngagements', 'totalHandlingTime', 'nonInteractiveTotalHandlingTime', 'Online', 'Back in 5', 'Away', 'Logged in']
    _df = pandas.DataFrame(index=index, columns=columns)
    for agent_id, activity in engagement_activity.items():
        if agent_id in index:
            _df.set_value(agent_id, 'totalInteractiveChats', activity['totalInteractiveChats'])
            _df.set_value(agent_id, 'totalNonInteractiveChats', activity['totalNonInteractiveChats'])
            _df.set_value(agent_id, 'connectedEngagements', activity['connectedEngagements'])
            _df.set_value(agent_id, 'totalHandlingTime', activity['totalHandlingTime'])
            _df.set_value(agent_id, 'nonInteractiveTotalHandlingTime', activity['nonInteractiveTotalHandlingTime'])
    for user in user_data:
        if str(user['id']) in index:
            _df.set_value(str(user['id']), 'agentName', user['fullName'])
            if user['memberOf']:
                _df.set_value(str(user['id']), 'agentGroup', group_data[user['memberOf']['agentGroupId']])
            else:
                _df.set_value(str(user['id']), 'agentGroup', 'None')        
    for agent_id, states in agent_activity.items():
        if agent_id in index:
            for state in states:
                _df.set_value(agent_id, state['name'], state['value'])
            #except KeyError:
            #    _df.set_value(agent_id, 'StateData', 'None')
    return _df

def make_queue_df(queue_data, skills_data):
    index = [skillId for skillId in queue_data.keys()]
    columns = ['skillName', 'avgTimeToAbandon', 'totalTimeToAnswer', 'totalTimeToAbandon', 'enteredQEng', 'avgTimeToAnswer', 'abandonmentRate', 'abandonedEng', 'connectedEng']
    _df = pandas.DataFrame(index=index, columns=columns)
    for skillId, skillName in skills_data.items():
        if str(skillId) in index:
            _df.set_value(str(skillId), 'skillName', skillName)
            _df.set_value(str(skillId), 'avgTimeToAbandon', queue_data[str(skillId)]['avgTimeToAbandon'])
            _df.set_value(str(skillId), 'totalTimeToAnswer', queue_data[str(skillId)]['totalTimeToAnswer'])
            _df.set_value(str(skillId), 'totalTimeToAbandon', queue_data[str(skillId)]['totalTimeToAbandon'])
            _df.set_value(str(skillId), 'enteredQEng', queue_data[str(skillId)]['enteredQEng'])
            _df.set_value(str(skillId), 'avgTimeToAnswer', queue_data[str(skillId)]['avgTimeToAnswer'])
            _df.set_value(str(skillId), 'abandonmentRate', queue_data[str(skillId)]['abandonmentRate'])
            _df.set_value(str(skillId), 'abandonedEng', queue_data[str(skillId)]['abandonedEng'])
            _df.set_value(str(skillId), 'connectedEng', queue_data[str(skillId)]['connectedEng'])
    return _df

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
                                'accountConfigReadOnly_users',
                                'accountConfigReadOnly_agentGroups'
                            ])
print(str(app))

# Grab data for the timeframe of the last 24 hours. Put the data in only one bucket.
rt_data = app.get_rt_operational_data(minute_timeframe='1440', in_buckets_of='1440')
print(str(rt_data['errors'])) if rt_data['errors'] else print('Main data: ok')
for method in rt_data['success']:
    details = method + ' data: '
    print(details + str(rt_data['success'][method]['errors'])) if rt_data['success'][method]['errors'] else print(details + 'ok')

groups_data = get_groups(app)
skills_data = get_skills(app)
agent_data = get_users(app)

queue_df = make_queue_df(rt_data['success']['queueHealth']['success']['skillsMetrics'], skills_data)
with open('queue_data.csv', 'w'):
    queue_df.to_csv(queue_file)

agent_df = make_agent_df(rt_data['success']['agentactivity']['success']['metricsByIntervals'][1]['metricsData']['agentsMetrics']['metricsPerAgent'],
    rt_data['success']['engactivity']['success']['metricsByIntervals'][0]['metricsData']['agentsMetrics']['metricsPerAgent'],
    agent_data,
    groups_data,
    )
with open('agent_data.csv', 'w'):
    agent_df.to_csv(agent_file)

#mail_reports()