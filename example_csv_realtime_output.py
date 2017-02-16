from liveengage_data_app import LiveEngageDataApp
import time
import datetime
import pandas

####################
### Boiler Plate ###
####################

# Grab the time when the script starts.
start_time_epoch = time.time()

# gather date and time
current_date = datetime.date.today()
_current_time = time.strftime('%H:%M', time.localtime(start_time_epoch))
_time_15_before = time.strftime('%H:%M', time.localtime(start_time_epoch - 900))
report_timeframe = _time_15_before + ' - ' + _current_time
timezone = time.strftime('%Z', time.localtime(start_time_epoch))

# Timeframe for the Real Time API's is 15 minutes
dataTimeframe = '15'

# Create App object and print to make sure it's good.
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

##########################
### Get real time data ###
##########################

rt_data = app.realtime_operational(minute_timeframe=dataTimeframe, in_buckets_of=dataTimeframe)

# Check to make sure Real Time Data is ok
print(str(rt_data['errors'])) if rt_data['errors'] else print('Main data: ok')
for method in rt_data['success']:
    details = method + 'data: '
    print(details + str(rt_data['success'][method]['errors'])) if rt_data['success'][method]['errors'] else print(details + 'ok')

agent_activity = rt_data['success']['agentactivity']['success']
engagement_activity = rt_data['success']['engactivity']['success']
queue_health = rt_data['success']['queueHealth']['success']


######################
### Get skill data ###
######################

skill_response = app.skills()

# Check to make sure Real Time Data is ok
print(str(skill_response['errors'])) if skill_response['errors'] else print('ok')

skill_results = skill_response['success']

########################
## Gather KPI Data   ###
## & Build DataFrame ###
########################

# Build a list of our skills
active_skill_ids = []
for skill in queue_health['skillsMetrics']:
    active_skill_ids.append(skill)

# Print skills to console, just to confirm.
print("We're working with these skills: " + ', '.join(active_skill_ids))

if active_skill_ids:

    # Construct our dataframe. The rows are our skills. The columns are our KPI's.
    df = pandas.DataFrame(index=active_skill_ids,
                          columns=["skill_name", "date", "timeframe", "timezone",
                                   "staff", "chats", "chats_answered", "abandoned",
                                   "average_speed_to_answer", "total_handling_time",
                                   "average_handling_time"])

    # Match skill ID to skill name. Input the skill name in our dataframe.
    for skill_data in skill_results:
        for skill in active_skill_ids:
            if str(skill_data['id']) == skill:
                df.set_value(skill, "skill_name", skill_data['name'])

    # Insert our date and time info into the dataframe using our start_time_epoch
    for skill in active_skill_ids:
        df.set_value(skill, "date", current_date)
        df.set_value(skill, "timeframe", report_timeframe)
        df.set_value(skill, "timezone", timezone)


    # Add Chats, ChatsAnswered, abandoned, & Average Speed to Answer to our dataframe
    for skill in queue_health['skillsMetrics']:

        # Grab our values from the data. Calculate abandoned manually.
        chats = queue_health['skillsMetrics'][skill]['enteredQEng']
        chatsAnswered = queue_health['skillsMetrics'][skill]['connectedEng']
        abandoned = chats - chatsAnswered
        avgTimeToAnswer = queue_health['skillsMetrics'][skill]["avgTimeToAnswer"]

        # Set our values in the correct spot in our dataframe.
        # eg. dataframe.set_value(index, column, myDataToPutThere)
        if chats:
            df.set_value(skill, "chats", chats)
        else:
            df.set_value(skill, "chats", 0)
        if chatsAnswered:
            df.set_value(skill, "chats_answered", chatsAnswered)
        else:
            df.set_value(skill, "chats_answered", 0)
        df.set_value(skill, "abandoned", abandoned)
        if avgTimeToAnswer:
            df.set_value(skill, "average_speed_to_answer", avgTimeToAnswer)
        else:
            df.set_value(skill, "average_speed_to_answer", 0)

    # Calculate & add Average Handling Time to our dataframe
    for skill in engagement_activity['skillsMetricsPerAgent']['metricsPerSkill']:

        # Get total handling time and put it in our data frame
        totalHandlingTime = engagement_activity['skillsMetricsPerAgent']['metricsPerSkill'][skill]['metricsTotals']['totalHandlingTime']

        if totalHandlingTime:
            df.set_value(skill, "total_handling_time", totalHandlingTime)
        else:
            df.set_value(skill, "total_handling_time", 0)

        # avg_handling_time = totalHandlingTime / number_of_chats
        # numChatsAnswered is already in our dataframe. We grab that data with dataframe.loc[index][column]
        numChatsAnswered = df.loc[skill]['chats_answered']
        avg_handling_time = totalHandlingTime / numChatsAnswered
        df.set_value(skill, "average_handling_time", avg_handling_time)

    # Determine number of interactive Staff. Input into dataframe.
    for skill in engagement_activity['skillsMetricsPerAgent']['metricsPerSkill']:

        total_active_agents = 0

        # For each agent in our data, if they have any amount of interactive handling time, add them to number of staff.
        for agent in engagement_activity['skillsMetricsPerAgent']['metricsPerSkill'][skill]['metricsPerAgent']:
            if engagement_activity['skillsMetricsPerAgent']['metricsPerSkill'][skill]['metricsPerAgent'][agent]['totalHandlingTime'] != '0':
                total_active_agents += 1
        df.set_value(skill, "staff", total_active_agents)

#if there are no skills active, build a dummy table
else:
    null_index = ["N/A"]

    df = pandas.DataFrame(index=null_index,
                          columns=["skill_name", "date", "timeframe", "timezone",
                                   "staff", "chats", "chats_answered", "abandoned",
                                   "average_speed_to_answer", "total_handling_time",
                                   "average_handling_time"])

    df.set_value("N/A", "skill_name", "All Offline")
    df.set_value("N/A", "date", current_date)
    df.set_value("N/A", "timeframe", report_timeframe)
    df.set_value("N/A", "timezone", timezone)
    df.set_value("N/A", "staff", 0)
    df.set_value("N/A", "chats", 0)
    df.set_value("N/A", "chats_answered", 0)
    df.set_value("N/A", "abandoned", 0)
    df.set_value("N/A", "average_speed_to_answer", 0)
    df.set_value("N/A", "total_handling_time", 0)
    df.set_value("N/A", "average_handling_time", 0)

#########################
### Output DataFrame ####
#########################

# Construct our output file name
timestr = time.strftime("%Y%m%d-%H%M%S")
outfile = 'C:\\chat_data\\' + timestr + '.csv'

with open(outfile, 'w') as f:
    # We could write the date and timeframe to the header, or just put it in the table itself. I think putting it in the table may be the better choice.
    #f.write('Date: ' + str(current_date) + '\nTimeframe: ' + report_timeframe + '\n\n')
    # Add dataframe to output file
   df.to_csv(f)

# Print to console.
print("Output file: " + outfile)
print("--- %s seconds to complete script." % (time.time() - start_time_epoch))

