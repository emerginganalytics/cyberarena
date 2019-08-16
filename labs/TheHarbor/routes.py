from app import app
from flask import redirect, request, render_template, abort, jsonify, json
from port_scanner import scan_ports


@app.route('/')
def home():
    load_template = '/pages/index.jinja'
    return render_template(load_template)


@app.route('/home')
def home_alt():
    load_template = '/pages/index.jinja'
    return render_template(load_template)


@app.route('/scanner', methods=['GET'])
def redirect():
    delay = 30
    flag = 'pages/hidden.jinja'
    fw_error = 'pages/error.jinja'

    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        client = request.environ['REMOTE_ADDR']
    else:
        client = request.environ['HTTP_X_FORWARDED_FOR']

    result = scan_ports(client, delay)

    if result == 1:
        return render_template(flag)
    else:
        return render_template(fw_error)


@app.route('/error')
def error():
    load_template = '/pages/error.jinja'
    return render_template(load_template)

# Delete once completed as there is no need to have this open for public
@app.route('/hidden', methods=["GET"])
def hidden():
    load_template = 'pages/hidden.jinja'
    return render_template(load_template)
