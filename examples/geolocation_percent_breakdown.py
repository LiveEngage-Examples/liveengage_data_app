from liveengage_data_app import LiveEngageDataApp
from collections import Counter


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
eh_data = app.engagement_history(from_epoch='1522209599000', to_epoch='1522295999000')
print(str(eh_data['errors'])) if eh_data['errors'] else print('ok')

countries = Counter()
for transcript in eh_data['success']:
    try:
        countries[transcript['visitorInfo']['country']] += 1
    except KeyError:
        countries['N/A'] += 1
	

total_countries = sum(countries.values())
for country, count in countries.items():
    pct = round(count * 100.0 / total_countries, 3)
    print(country, pct)
