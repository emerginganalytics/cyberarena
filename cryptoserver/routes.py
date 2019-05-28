# Things to show:
# - Simple GET/POST form
# - Simple AJAX form
# - Getting variables from URL in routes and templates
from app import app
from flask import redirect, request, render_template, abort, jsonify, make_response
from werkzeug.utils import secure_filename

import io
import hashlib


@app.route('/')
def home():
    return 'So far this doesnt do anything'


@app.route('/md5_page', methods=['GET', 'POST'])
def md5_page():
    page_template = 'pages/md5_page.jinja'

    if request.method == 'GET':
        return render_template(page_template)

    elif request.method == 'POST':
        if 'password_file' not in request.files:
            # User did not submit a file.  Show error and let them upload again
            return render_template(
                page_template,
                upload_error="You must choose a file to upload",
            )
        else:
            # Check to be sure that the user has submitted a file.
            input_file = request.files['password_file']

            if input_file.filename == '':
                # User has submitted a blank file.  Show error and let them upload again.
                return render_template(
                    page_template,
                    upload_error="You must choose a file to upload",
                )

            # At this point, we have a csv file to process
            raw_input = io.StringIO(input_file.stream.read().decode("UTF8"), newline=None)

            passwords = raw_input.read().split('\n')

            hashes = []

            for password in passwords:
                hashes.append({
                    'plaintext': password,
                    'hash': hashlib.md5(password.encode('utf-8')).hexdigest()
                })

            return render_template(
                page_template,
                hashed_passwords=hashes,
            )


@app.route('/hidden')
def hidden():
    # This application sets a cookie with the key "logged_in" to true when a user has authenticated
    # They must be authenticated before viewing this page
    logged_in = request.cookies.get('logged_in', None)
    if logged_in is None or logged_in != 'true':
        return redirect('/login')
    else:
        page_template = 'pages/hidden.jinja'

        return render_template(page_template)


@app.route('/login', methods=['GET', 'POST'])
def login():
    page_template = 'pages/login.jinja'

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
        elif username == 'admin' and password == 'password':
            # These are the correct credentials, so the cookie for "logged_in" is set to true
            resp = make_response(redirect('/hidden'))
            resp.set_cookie('logged_in', 'true')

            return resp
        else:
            login_error = 'Please check your username and password and try again'

            return render_template(
                page_template,
                login_error=login_error,
            )


@app.route('/logout')
def logout():
    # To log a user out, we just need to delete the cookie for "logged_in"
    # Setting a cookie that expires at time 0 is the simplest way to delete a cookie

    resp = make_response(redirect('/login'))
    resp.set_cookie('logged_in', 'false', expires=0)

    return resp
