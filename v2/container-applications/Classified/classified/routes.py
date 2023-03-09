"""
Contains collection of web-based vulnerability workouts:
- xss : /xss/xss_d/<wid>
- 2fa : /tfh/<wid>
- sql injection :  /sql_injection/<wid>
- inspect : /inspect/<wid>
- arena snake : /arena_snake/<wid>
- wireshark : /wireshark/<wid>
"""
from flask import abort, Blueprint, flash, jsonify, make_response, request, redirect, render_template, session, url_for
from flask import current_app as app
from flask_bootstrap import Bootstrap
from io import BytesIO

# app imports
from classified.config import SQLInjection, XSS, RegisterForm, LoginForm
from app_utilities.gcp.datastore_manager import DataStoreManager
from app_utilities.globals import DatastoreKeyTypes

classified_bp = Blueprint(
    'classified', __name__,
    url_prefix='/classified',
    template_folder='./templates',
    static_folder='./static',
)

# Arena Snake Routes
# Inspect Routes
# SQL Injection Routes

# Wireshark Routes

# XSS Routes


@classified_bp.errorhandler(404)
def page_not_found_error(error):
    page_template = 'invalid_workout.html'
    return render_template(page_template, error=error)


@classified_bp.errorhandler(500)
def internal_server_error(error):
    page_template = 'invalid_workout.html'
    return render_template(page_template, error=error)


