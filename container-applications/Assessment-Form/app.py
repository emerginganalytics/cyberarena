from collections import OrderedDict
from flask import Flask, render_template, request, jsonify, redirect, session
from flask_assets import Environment, Bundle
from google.cloud import datastore, runtimeconfig
import os

from utilities.globals import auth_config, ds_client
from utilities.assessment_questions import questions, domains

# application instance
app = Flask(__name__)
app.secret_key = os.urandom(16)
assets = Environment(app)
assets.url = app.static_url_path
assets.debug = False

scss = Bundle('assets/scss/completion.scss', filters='pyscss', output='css/level_report.css')
assets.register('scss_all', scss)


@app.route('/')
def default_route():
    return render_template('login.html', auth_config=auth_config)


@app.route('/login', methods=['POST'])
def login():
    if request.method == "POST":
        session['user_email'] = request.json['user_email']

    return render_template('login.html', auth_config=auth_config)


@app.route('/<int:i>', methods=['GET', 'POST'])
def home(i):
    user_email = None
    if 'user_email' in session:
        user_email = str(session['user_email'])
    if i == 0:
        if user_email:
            user_response = datastore.Entity(ds_client.key('cmmc-assessment-response', user_email))
            user_response['score'] = {}
        else:
            return render_template('login.html', auth_config=auth_config)
        for domain in domains:
            user_response['score'][domain] = {'overall': 0}
            for capability in domains[domain]['capabilities']:
                user_response['score'][capability] = {'overall': 0}
        ds_client.put(user_response)
        # Now go to question 1
        i += 1
    else:
        user_response = ds_client.get(ds_client.key('cmmc-assessment-response', user_email))
        if not user_response:
            return redirect(404)

    if request.method == 'POST':
        # points = int(request.form['index'])
        if i == 40:
            i = 40
        else:
            q_score = int(request.form['hopping'])
            q_domain = questions[i]['domain']
            q_capability = questions[i]['capability']
            user_response['score'][q_domain]['overall'] += q_score
            user_response['score'][q_capability]['overall'] += q_score
            i += 1
            ds_client.put(user_response)
    progress_value = i * 2.5 - 2.5
    score = OrderedDict(sorted(user_response['score'].items()))
    index_template = 'index.html'
    score_template = 'score_display.html'
    if i == 40:
        # Get total score
        total_score = 0
        total_capability = 0
        for domain in score:
            total_score += score[domain]['overall']
        for capability in score:
            total_capability += score[capability]['overall']
        return render_template(score_template, questions=questions, score=score, domains=domains, i=i,
                               progress_value=progress_value, total_score=total_score, total_capability=total_capability)
    else:
        return render_template(index_template, questions=questions, score=score, domains=domains, i=i,
                               progress_value=progress_value)


@app.errorhandler(404)
def page_not_found_error(error):
    page_template = '404.html'
    return render_template(page_template, error=error)


@app.errorhandler(500)
def internal_server_error(error):
    page_template = '500.html'
    return render_template(page_template, error=error)


if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=4000)
