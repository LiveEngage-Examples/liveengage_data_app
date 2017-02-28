from liveengage_data_app import LiveEngageDataApp
from bokeh.charts import Histogram, output_file, show
from bokeh.layouts import row
import pandas

app = LiveEngageDataApp(account_number='xx',
                        keys_and_secrets={
                            'consumer_key':'xx',
                            'consumer_secret':'xx',
                            'token_key':'xx',
                            'token_secret':'xx'
                        },
                        services=[
                            'engHistDomain',
                            #'leDataReporting',
                            #'accountConfigReadOnly_skills',
                            #'accountConfigReadOnly_users',
                            #'accountConfigReadOnly_agentGroups'
                        ])
print(str(app))

# http://www.epochconverter.com/ - grab the millisecond version
eh_data = app.engagement_history(from_epoch='1487894401000', to_epoch='1487937600000')
print(str(eh_data['errors'])) if eh_data['errors'] else print('ok')


agent_lines = []
visitor_lines = []

for chat in eh_data['success']:
    num_from_agent = 0
    num_from_visitor = 0
    for line in chat['transcript']['lines']:
        if line['source'] == 'agent':
            num_from_agent += 1
        elif line['source'] == 'visitor':
            num_from_visitor += 1
    agent_lines.append(num_from_agent)
    visitor_lines.append(num_from_visitor)

agent_df = pandas.DataFrame({'agent_lines': agent_lines})
visitor_df = pandas.DataFrame({'visitor_lines': visitor_lines})

agent_hist = Histogram(agent_df, title="Num Lines sent by Agent", plot_width=400)
visitor_hist = Histogram(visitor_df, title="Num Lines sent by Visitor", plot_width=400)

output_file('lines_from_each_side.html')
show(row(agent_hist, visitor_hist))
