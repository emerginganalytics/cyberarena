from flask import abort, jsonify, redirect, render_template, request, escape

import shodan
import shodan.helpers as helpers
import sys
import json

from app import app

# SHODAN_API_KEY = 'BWmELJlT4jH83fFG29sKiKqwouKk7kL8'
SHODAN_API_KEY = 'N81y8YZTBIUfVmrEa1ZL8ywi119Pz1pT'


# TODO: Need to implement error catching for bad queries
@app.route('/', methods=['GET', 'POST'])
def default():
    api = shodan.Shodan(SHODAN_API_KEY)
    result_services = []
    result_count = 0
    page_template = 'index.jinja'
    if request.method == 'POST':
        try:
            query = request.form.get('shodan_query')
            page_num = request.form.get('page_number')
            result = api.search(query, limit=10)
            result_count = api.count(query)
            print(result.keys())
            # for result in api.search_cursor(query):
            #     result_services.append(result)

            return render_template(
                page_template,
                shodanResults=result,
                resultCount=result_count,
                query=query,
                page_num=page_num
            )
        except shodan.APIError as e:
            print(e)
            e_template = 'invalid_query.jinja'
            return render_template(e_template)
    return render_template(page_template)


@app.route('/results/<string:ip>')
def result(ip):
    api = shodan.Shodan(SHODAN_API_KEY)
    ip_list = []
    ip_list.append(ip)
    info = api.host(ip_list, history=True)
    for tmp in info["data"]:
        has_screenshot = helpers.get_screenshot(tmp)
        if has_screenshot is not None:
            info["screenshot"] = has_screenshot["data"]

    page_template = 'results.jinja'

    return render_template(page_template, resultInfo=info)


@app.route('/data/', methods=['GET', 'POST'])
def data():
    page_template = 'raw_data.jinja'
    if request.method == "POST":
        print("POST")
        return render_template(page_template, rawData=request.form.get('data'))
    if request.method == "GET":
        print("GET")
        print(type(request.get_data()))

    # return render_template(page_template, rawData=request.get_json())
    return "failed"


@app.route('/query/<string:query>/<int:page>')
def view_all_query_results(query, page):
    api = shodan.Shodan(SHODAN_API_KEY)
    if request.method == "POST":
        result = api.search(query, page=page)


@app.route('/invalid/<workout_id>')
def invalid(workout_id):
    page_template = 'invalid.html'
    return render_template(page_template)
