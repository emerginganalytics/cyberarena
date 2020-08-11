"""
    What this function will do:
    Populate the datastore with information on 3-4 preset query results.
    Can store service names, cve's, ips, etc.

    Last option will be a wildcard where students create their own query
    on a object they want to find and submit a screenshot
    of 1 result from the query results page. We don't need to store any
    data for this query.

    Data will be validated on the Student / Teacher Landing pages
"""
import shodan
import shodan.helpers as helpers

from google.cloud import datastore, runtimeconfig

# Globals
# SHODAN_API_KEY = 'BWmELJlT4jH83fFG29sKiKqwouKk7kL8'
SHODAN_API_KEY = 'N81y8YZTBIUfVmrEa1ZL8ywi119Pz1pT'
ds_client = datastore.Client()
runtimeconfig_client = runtimeconfig.Client()
myconfig = runtimeconfig_client.config('cybergym')
project = myconfig.get_variable('project').value.decode("utf-8")

def populate_datastore(workout_id):
    api = shodan.Shodan(SHODAN_API_KEY)
    workout_key = ds_client.key('cybergym-workout', workout_id)
    workout = ds_client.get(workout_key)

    # Queries Run to Satisfy Assessment Questions
    query_list = [
        'port:25565 city:"Dallas"',
        'os:"FreeBSD" country:"US"',
        'city:"Phoenix" "Apache"',
        'vuln:"CVE-2014-0160"',
    ]
    query_results = ["", "", "", ""]

    # Query and insert result data into list for future parsing
    for pos in range(len(query_list)):
        try:
            data = api.search(query_list[pos], limit=10)
            total_results = api.count(query_list[pos])
            if pos == 0:
                query_results[pos] = data['matches'][2]['org']
            elif pos == 1:
                query_results[pos] = data['matches'][0]['ip_str']
            elif pos == 2 or pos == 3:
                query_results[pos] = data['total']
        except shodan.APIError as e:
            print(e)

    # Update the Datastore with query results:
    workout['assessment']['questions'][0]['answer'] = query_results[0]
    workout['assessment']['question2'][1]['answer'] = query_results[1]
    workout['assessment']['question3'][2]['answer'] = query_results[2]
    workout['assessment']['question4'][3]['answer'] = query_results[3]
    ds_client.put(workout)

    print(query_results)
    
    return print('Datastore Populated for workout %s' % workout_id)
# populate_datastore(workout_id='mrujptbiaa')