import liveengage_api_wrapper.py as le_api

app = le_api.LiveEngageDataApp(account_number='1234',
                            keys_and_secrets={
                                'consumer_key':'fdsafsda'
                                'consumer_secret':'fdsaf'
                                'token_key':'fdas'
                                'token_secret':'fdsa'
                            },
                            services=[
                                'engHistDomain',
                                'leDataReporting',
                                'accountConfigReadOnly_skills'
                            ])
print(app.services)
eh_data = app.get_eng_hist_data()
print(eh_data[0])

