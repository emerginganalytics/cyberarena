import json
import logging as logger
from flask import abort, Flask, jsonify, redirect, render_template, request, session
from utilities.gcp.arena_authorizer import ArenaAuthorizer
from utilities.gcp.cloud_env import CloudEnv
from utilities.gcp.datastore_manager import *

# App Blueprints
from admin_app.routes import admin_app
from student_app.routes import student_app
from teacher_app.routes import teacher_app
from faqs_app.routes import faqs_app
from fixed_arena_app.routes import fixed_arena_app

# API Views
from api.classroom import Classroom
from api.fixed_arena import FixedArena
from api.fixed_arena_class import FixedArenaClass
from api.fixed_arena_workspace import FixedArenaWorkspace
from api.unit import Unit
from api.workout import Workout
from api.attack_specs import AttackSpecs
from api.command_and_control import CommandAndControl
from api.iot_device import IoTDevice
from api.user import Users

# --------------------------- FLASK APP --------------------------
app = Flask(__name__)
app.register_blueprint(admin_app)
app.register_blueprint(student_app)
app.register_blueprint(teacher_app)
app.register_blueprint(faqs_app)
app.register_blueprint(fixed_arena_app)
app.config['SECRET_KEY'] = 'XqLx4yk8ZW9uukSCXIGBm0RFFJKKyDDm'
app.jinja_env.globals['project'] = CloudEnv().project


# Default route
@app.route('/')
def default_route():
    return render_template('login.html', auth_config=CloudEnv().auth_config)


@app.route('/home/')
def home():
    if 'user_groups' in session:
        if 'students' in session['user_groups']:
            return redirect("/student/home")
        else:
            return redirect("/teacher/home")
    else:
        return redirect('/unauthorized')


@app.route("/login", methods=['GET', 'POST'])
def login():         
    if request.method == 'POST':
        user_data = request.get_json(force=True)
        if 'user_email' in user_data:
            arena_auth = ArenaAuthorizer()
            user_groups = arena_auth.get_user_groups(user_data['user_email'])
            if user_groups:
                session['user_email'] = user_data['user_email']
                session['user_groups'] = user_groups
                logger.info(msg=f"User {user_data['user_email']} logged in")
                return json.dumps({"redirect": "/home"})
        return json.dumps({'redirect': '/unauthorized'})
    return render_template('login.html', auth_config=CloudEnv().auth_config, error_resp='403')


@app.route('/logout', methods=['POST'])
def logout():
    if request.method == 'POST':
        session.clear()
        return json.dumps({'logged_out': True})


@app.route('/leave_comment', methods=['POST'])
def leave_comment():
    if request.method == 'POST':
        comment_email = request.form['comment_email']
        comment_subject = request.form['comment_subject']
        comment_text = request.form['comment_text']
        # store_comment(comment_email, comment_subject, comment_text)

        return redirect('/')


@app.route('/complete', methods=['POST'])
def complete_verification():
    """
        Workout completion check. Receives post request from workout and updates workout as complete in datastore.
        Request data in form {'workout_id': workout_id, 'token': token,}
    """
    if request.method == 'POST':
        workout_request = request.get_json(force=True)

        workout_id = workout_request['workout_id']
        token = workout_request['token']
        ds_manager = DataStoreManager(key_type=DatastoreKeyTypes.CYBERGYM_WORKOUT, key_id=workout_id)
        workout = ds_manager.get()

        token_exists = next(item for item in workout['assessment']['questions'] if item['key'] == token)
        token_pos = next((i for i, item in enumerate(workout['assessment']['questions']) if item['key'] == token), None)
        if token_exists:
            logger.info("Completion token matches. Setting the workout question %d to complete." % token_pos)
            workout['assessment']['questions'][token_pos]['complete'] = True
            ds_manager.put(workout)
            logger.info('%s workout question %d marked complete.' % (workout_id, token_pos+1))
            return 'OK', 200
        else:
            logger.info("In complete_verification: Completion key %s does NOT exist in assessment dict! Aborting" % token)


@app.route('/arena-functions', methods=['POST'])
def arena_functions():
    """
    Used for interacting between workouts in an arena build. The request data includes the following variables:
    workout_id - The workout on which to perform a given action
    action - The action to perform on the given workout (e.g., deduct-points)
    """
    if request.method == 'POST':
        arena_data = request.get_json(force=True)
        workout_id = arena_data['workout_id'] if 'workout_id' in arena_data else None
        action = arena_data['action'] if 'action' in arena_data else None

        if action == 'deduct-points' and workout_id:
            ds_manager = DataStoreManager(key_type=DatastoreKeyTypes.CYBERGYM_WORKOUT, key_id=workout_id)
            workout = ds_manager.get()

            if 'points_deducted' not in workout:
                if 'points' in workout:
                    workout['points'] -= 100
                else:
                    workout['points'] = -100
                workout['points_deducted'] = True
                return_data = {"msg": f"You deducted 100 points from {workout['student_name']}"}
            else:
                return_data = {"msg": f"Sorry...someone else beat you to it."}
            ds_manager.put(workout)
        else:
            return_data = {"msg": f"Invalid action called: {action} for {workout_id}"}

        return jsonify(return_data), 200


@app.route('/arena-scoreboard/<arena_id>', methods=['GET', 'POST'])
def arena_scoreboard(arena_id):
    ds_manager = DataStoreManager(key_type=DatastoreKeyTypes.CYBERGYM_UNIT, key_id=str(arena_id))
    arena_build = ds_manager.get()
    team_info = {}
    flag_info = {}
    arena_type = ""

    teams = arena_build['teams'] if 'teams' in arena_build else None
    for team in teams:
        team_name = str(team)
        team_workouts_query = DataStoreManager(key_id=DatastoreKeyTypes.CYBERGYM_UNIT.value).query()
        team_workouts_query.add_filter('workout_id', '=', str(arena_id))
        team_workouts = list(team_workouts_query.fetch())
        team_info[team_name] = {}
        team_info[team_name]['members'] = []

        for workout in team_workouts:
            if len(flag_info.values()) == 0:
                flag_info = workout['assessment']
                arena_type = workout['type']
            team_info[team_name]['found_flags'] = []
            submitted_flags = []
            for flag in flag_info['questions']:
                if 'submitted_answers' in workout:
                    for submitted_answer in workout['submitted_answers']:
                        submitted_flags.append({
                            'answer': submitted_answer['answer'],
                            'timestamp': submitted_answer['timestamp'],
                            'first': submitted_answer['first'] if 'first' in submitted_answer else False
                        })
                if next((item for item in submitted_flags if item['answer'] == flag['answer']), False):
                    team_info[team_name]['found_flags'].append(next(item for item in submitted_flags if item['answer'] == flag['answer']))
                else:
                    team_info[team_name]['found_flags'].append(0)
            team_info[team_name]['members'].append(workout.key.name)

            team_info[team_name]['points'] = workout['points'] if 'points' in workout else 0
        if not team_info[team_name]['members']:
            team_info[team_name]['points'] = 0
    team_info = sorted(team_info.items(), key = lambda i: i[1]['points'], reverse=True)
    
    return render_template('arena_scoreboard.html', arena_info=arena_build, team_info=team_info, arena_type=arena_type, flag_info=flag_info)


@app.route('/no-workout', methods=['GET', 'POST'])
def no_workout():
    return render_template("errors/no_workout.html")


@app.route('/unauthorized', methods=['GET', 'POST'])
def unauthorized():
    abort(401)


@app.errorhandler(401)
def handle_401(e):
    message = str({'error': e, 'error_type': 401, 'request': str(request)})
    logger.error(msg=message)
    return render_template('errors/unauthorized.html'), 401


@app.route('/403', methods=['GET', 'POST'])
def forbidden():
    abort(403)


@app.errorhandler(403)
def handle_403(e):
    message = str({'error': e, 'error_type': 403, 'request': str(request)})
    logger.error(msg=message)
    return render_template('errors/403.html'), 403


@app.route('/404', methods=['GET', 'POST'])
def not_found():
    abort(404)


@app.errorhandler(404)
def handle_404(e):
    message = str({'error': e, 'error_type': 404, 'request': str(request)})
    logger.error(msg=message)
    return render_template("errors/404.html")


@app.route('/422', methods=['GET', 'POST'])
def invalid_build_spec():
    abort(422)


@app.errorhandler(422)
def handle_422(e):
    message = str({'error': e, 'error_type': 422, 'request': str(request)})
    logger.error(msg=message)
    return render_template("errors/invalid_build_specification.html"), 422


@app.route('/500', methods=['GET', 'POST'])
def internal_error():
    abort(500)


@app.errorhandler(500)
def handle_500(e):
    message = str({'error': e, 'error_type': 500, 'request': str(request)})
    logger.error(msg=message)
    return render_template("errors/500.html", error=e), 500


@app.route('/privacy', methods=['GET'])
def privacy():
    return render_template('privacy.html')


def register_api(view, endpoint, url, pk='id', pk_type='string'):
    view_func = view.as_view(endpoint)
    app.add_url_rule(url, view_func=view_func, methods=['GET'])
    app.add_url_rule(url, view_func=view_func, methods=['POST'])
    app.add_url_rule(f'{url}<{pk_type}:{pk}>', view_func=view_func,
                     methods=['GET', 'PUT', 'DELETE'])


# Register all API Routes
register_api(view=Classroom, endpoint='classroom', url='/api/classroom/', pk='class_name')
register_api(view=Unit, endpoint='unit', url='/api/unit/', pk='build_id')
register_api(view=Workout, endpoint='workout', url='/api/unit/workout/', pk='build_id')
register_api(view=IoTDevice, endpoint='iot', url='/api/iot/', pk='device_id')
register_api(view=FixedArena, endpoint='fixed-arena', url='/api/fixed-arena/', pk='build_id')
register_api(view=FixedArenaClass, endpoint='class', url='/api/fixed-arena/class/', pk='build_id')
register_api(view=FixedArenaWorkspace, endpoint='workspace', url='/api/fixed-arena/workspace/', pk='build_id')
register_api(view=CommandAndControl, endpoint='inject', url='/api/inject/', pk='build_id')
register_api(view=AttackSpecs, endpoint='templates', url='/api/inject/templates/', pk='build_id')
register_api(view=Users, endpoint='user', url='/api/user', pk='user_id')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080, threaded=True)
