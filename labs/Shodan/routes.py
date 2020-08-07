from flask import abort, jsonify, redirect, render_template, request, escape
from google.cloud import datastore

import shodan
import shodan.helpers as helpers
import sys
import json

from app import app

# SHODAN_API_KEY = 'BWmELJlT4jH83fFG29sKiKqwouKk7kL8'
SHODAN_API_KEY = 'N81y8YZTBIUfVmrEa1ZL8ywi119Pz1pT'
ds_client = datastore.Client()
runtimeconfig_client = runtimeconfig.Client()
myconfig = runtimeconfig_client.config('cybergym')
project = myconfig.get_variable('project').value.decode("utf-8")


@app.route('/<workout_id>', methods=['GET', 'POST'])
def default(workout_id):
    api = shodan.Shodan(SHODAN_API_KEY)
    page_template = 'index.jinja'

    workout = ds_client.get(ds_client.key('cybergym-workout', workout_id))

    if workout:
        if workout['type'] == 'shodan':
            if request.method == 'POST':
                try:
                    query = request.form.get('shodan_query')
                    page_num = request.form.get('page_number')
                    result = api.search(query, limit=10)
                    result_count = api.count(query)
                    print(result.keys())

                    return render_template(
                        page_template,
                        shodanResults=result,
                        resultCount=result_count,
                        query=query,
                        page_num=page_num,
                        workoutid=workout_id,
                    )
                except shodan.APIError as e:
                    print(e)
                    e_template = 'invalid_query.jinja'
                    return render_template(e_template)
            return render_template(page_template)
        else:
            return redirect('/invalid/' + workout_id)
    else:
        return redirect('/invalid/' + workout_id)


@app.route('/results/<string:ip>/<workout_id>')
def result(ip, workout_id):
    api = shodan.Shodan(SHODAN_API_KEY)
    workout = ds_client.get(ds_client.key('cybergym-workout', workout_id))

    if workout:
        if workout['type'] == 'shodan':

            ip_list = []
            ip_list.append(ip)
            info = api.host(ip_list, history=True)
            for tmp in info["data"]:
                has_screenshot = helpers.get_screenshot(tmp)
                if has_screenshot is not None:
                    info["screenshot"] = has_screenshot["data"]

            page_template = 'results.jinja'

            return render_template(page_template, resultInfo=info, workoutid=workout_id,)
        else:
            return redirect('/invalid/' + workout_id)
    else:
        return redirect('/invalid/' + workout_id)


@app.route('/data/<workout_id>', methods=['GET', 'POST'])
def data(workout_id):
    page_template = 'raw_data.jinja'
    workout = ds_client.get(ds_client.key('cybergym-workout', workout_id))

    if workout:
        if workout['type'] == 'shodan':
            if request.method == "POST":
                print("POST")
                return render_template(page_template, rawData=request.form.get('data'), workoutid=workout_id,)
            if request.method == "GET":
                print("GET")
                print(type(request.get_data()))
        else:
            return redirect('/invalid/' + workout_id)
    else:
        return redirect('/invalid/' + workout_id)


@app.route('/query/<string:query>/<int:page>/<workout_id>')
def view_all_query_results(query, page, workout_id):
    api = shodan.Shodan(SHODAN_API_KEY)
    workout = ds_client.get(ds_client.key('cybergy-workout', workout_id))

    if workout:
        if workout['type'] == 'shodan':
            if request.method == "POST":
                result = api.search(query, page=page)
        else:
            return redirect('/invalid/' + workout_id)
    else:
        return redirect('/invalid/' + workout_id)


# This path is only necessary if dynamically creating assessment questions
# otherwise, ignore
@app.route('/loader/<workout_id>')
def loader(workout_id):
    key = ds_client.key('cybergym-workout', workout_id)
    workout = ds_client.get(key)

    if workout:
        if workout['type'] == 'shodan':
            return redirect('/' + workout_id)
        else:
            return redirect('/invalid/' + workout_id)
    else:
        return redirect('/invalid/' + workout_id)


@app.route('/invalid/<workout_id>')
def invalid(workout_id):
    page_template = 'invalid_workout.html'
    return render_template(page_template)
