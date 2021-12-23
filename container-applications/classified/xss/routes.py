from flask import Blueprint, render_template, redirect, request
from globals import ds_client
from xss.config import *

# Blueprint Configuration
xss_bp = Blueprint(
    'xss_bp', __name__,
    url_prefix='/xss',
    template_folder='templates',
    static_folder='static'
)


@xss_bp.route("/xss_d/<workout_id>", methods=["GET", "POST"])
def xss(workout_id):
    key = ds_client.key('cybergym-workout', workout_id)
    workout = ds_client.get(key)

    if workout['type'] == 'xss':
        page_template = 'xss.html'
        name = 'Stranger'
        bad_request = 'bad request'
        if request.args.get('bad_request'):
            bad_request = request.args.get('bad_request')

        return render_template(page_template, name=name, bad_request=bad_request, workout_id=workout_id)
    else:
        return redirect(404)


@xss_bp.route("/xss_r/<workout_id>", methods=['GET', 'POST'])
def xss_r(workout_id):
    key = ds_client.key('cybergym-workout', workout_id)
    workout = ds_client.get(key)
    if workout['type'] == 'xss':
        page_template = 'xss_r.html'
        name = 'Stranger'
        if request.method == 'POST':
            name = request.form['name']
        return render_template(page_template, name=name, workout_id=workout_id)
    else:
        return redirect(404)


@xss_bp.route("/xss_s/<workout_id>", methods=['GET', 'POST'])
def xss_s(workout_id):
    key = ds_client.key('cybergym-workout', workout_id, use_cache=False, use_memcache=False)
    workout = ds_client.get(key)
    if workout['type'] == 'xss':
        page_template = 'xss_s.html'
        if request.method == 'POST':
            add_feedback(request.form['feedback'], workout_id)

        search_query = request.args.get('query')
        feedbacks = get_feedbacks(workout_id, search_query)
        return render_template(page_template, feedbacks=feedbacks, search_query=search_query, workout_id=workout_id)
    else:
        return redirect(404)
