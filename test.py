import liveengage_data_app as le_api

app = le_api.LiveEngageDataApp(account_number='xx',
                            keys_and_secrets={
                                'consumer_key':'xx',
                                'consumer_secret':'xx',
                                'token_key':'xx',
                                'token_secret':'xx'
                            },
                            services=[
                                'engHistDomain'#,
                                #'leDataReporting',
                                #'accountConfigReadOnly_skills'
                            ])
# http://www.epochconverter.com/ - grab the millisecond version
eh_data = app.get_eng_hist_data(from_epoch='1469419200000', to_epoch='1469505599000')
print(str(eh_data[-1]).encode("utf8"))