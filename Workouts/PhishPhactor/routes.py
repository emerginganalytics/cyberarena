from app import app
from flask import redirect, request, render_template, abort, jsonify, make_response
import requests
import subprocess


@app.route('/login', methods=['GET', 'POST'])
def login():
    page_template = "index.jinja"

   if request.method == 'GET':
        return render_template(page_template)

    elif request.method == 'POST':
        username = request.form.get('username', None)
        password = request.form.get('password', None)

        print(username, password)

        if username is None or password is None:
            login_error = 'You must submit a username and password'

            return render_template(
                page_template,
                login_error=login_error
            )
        elif username == 'root' and password == 'password':
            # These are the correct credentials, so the cookie for "logged_in" is set to true
            resp = make_response(redirect('/home'))
            resp.set_cookie('logged_in', 'true')

            return resp
        else:
            login_error = ' '

            return render_template(
                page_template,
                login_error=login_error,
            )


@app.route('/home')
def home():
    page_template = 'main.jinja'
    return render_template(page_template)


@app.route('/LOGIN', methods=['GET', 'POST'])
def fake_login():
    page_template = 'fake_login.jinja'
    if request.method == 'GET':
        return render_template(page_template)

    elif request.method == 'POST':
        username = request.form.get('username', None)
        password = request.form.get('password', None)

        print(username, password)

        if username is None or password is None:
            login_error = 'You must submit a username and password'

            return render_template(
                page_template,
                login_error=login_error
            )
        elif username == 'root' and password == 'password':
            # These are the correct credentials, so the cookie for "logged_in" is set to true
            resp = make_response(redirect('/fake'))
            resp.set_cookie('logged_in', 'true')

            return resp
        else:
            login_error = ' '
            return render_template(page_template, login_error=login_error)

@app.route('/fake', methods=['GET', 'POST'])
def fake():
    page_template = 'flag.jinja'

    # Handling the workout complete request:
    if request.method == 'POST':
        dns_suffix = subprocess.Popen(['sudo', 'printenv', 'DNS_SUFFIX']) 
        URL = f'https://buildthewarrior{dns_suffix}/complete'
        workout_id = subprocess.Popen(['sudo', 'printenv', 'WORKOUTID'])
        workout_key = subprocess.Popen(['sudo', 'printenv', 'WORKOUTKEY0'])

        status = {
            "workout_id": workout_id,
            "token": workout_key,
        }
        publish = requests.post(URL, json=status)
        print(f'[*] POSTING to {URL} ...') 
        return redirect('/totally-not-malware')

    return render_template(page_template)


@app.route('/totally-not-malware', methods=['GET'])
def end():
    page_template = 'download.jinja'

    if request.method == 'GET':
        return render_template(page_template)
    else:
        return 405


@app.route('/nope', methods=['GET'])
def nope():
    page_template = 'nope.jinja'
    return render_template(page_template)


@app.route('/logout')
def logout():
    # To log a user out, we just need to delete the cookie for "logged_in"
    # Setting a cookie that expires at time 0 is the simplest way to delete a cookie

    resp = make_response(redirect('/login'))
    resp.set_cookie('logged_in', 'false', expires=0)

    return resp