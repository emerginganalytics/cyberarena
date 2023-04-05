import json
import logging as logger
from flask import abort, Flask, jsonify, redirect, render_template, request, session, url_for
from main_app_utilities.gcp.arena_authorizer import ArenaAuthorizer
from main_app_utilities.gcp.cloud_env import CloudEnv
from cloud_fn_utilities.send_mail.send_mail import SendMail

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
from api.agency import Agency, AgencyTelemetry, AttackSpecs
from api.iot_device import IoTDevice
from api.user import Users
from api.escape_room import EscapeRoomUnit, EscapeRoomWorkout

cloud_env = CloudEnv()

# --------------------------- FLASK APP --------------------------
app = Flask(__name__)
app.register_blueprint(admin_app)
app.register_blueprint(student_app)
app.register_blueprint(teacher_app)
app.register_blueprint(faqs_app)
app.register_blueprint(fixed_arena_app)
app.config['SECRET_KEY'] = 'XqLx4yk8ZW9uukSCXIGBm0RFFJKKyDDm'
app.jinja_env.globals['project'] = cloud_env.project


# Default route
@app.route('/')
def default_route():
    return render_template('v2-login.html', auth_config=cloud_env.auth_config)


@app.route('/home/')
def home():
    if 'user_groups' in session:
        if ArenaAuthorizer.UserGroups.INSTRUCTOR.value in session['user_groups'] \
                or ArenaAuthorizer.UserGroups.ADMIN.value in session['user_groups']:
            return redirect('/teacher/home')
        else:
            return redirect("/student/join/")
    else:
        return redirect('/unauthorized')


@app.route("/login", methods=['GET', 'POST'])
def login():         
    if request.method == 'POST':
        user_data = request.get_json(force=True)
        if 'user_email' in user_data:
            arena_auth = ArenaAuthorizer()
            if user := arena_auth.get_user(email=user_data['user_email']):
                session['user_email'] = user_data['user_email']
                session['user_groups'] = user['permissions']
                logger.info(msg=f"User {user_data['user_email']} logged in")
                return json.dumps({"redirect": "/home"})
        return json.dumps({'redirect': '/unauthorized'})
    return render_template('v2-login.html', auth_config=cloud_env.auth_config, error_resp='')


@app.route('/logout', methods=['POST'])
def logout():
    if request.method == 'POST':
        session.clear()
        return json.dumps({'logged_out': True})


@app.route('/leave_comment', methods=['POST'])
def leave_comment():
    if request.method == 'POST':
        user_email = request.form['email']
        comment_subject = request.form['subject']
        comment_text = request.form['comment']
        attachment = request.files['image']

        SendMail().help_form(usr_email=user_email, usr_subject=comment_subject,
                             usr_message=comment_text, usr_image=attachment)

        return redirect(request.referrer)


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
register_api(view=Agency, endpoint='agency', url='/api/agency/', pk='build_id')
register_api(view=AgencyTelemetry, endpoint='telemetry', url='/api/agency/telemetry/', pk='build_id')
register_api(view=AttackSpecs, endpoint='templates', url='/api/agency/templates/', pk='build_id')
register_api(view=Users, endpoint='user', url='/api/user', pk='user_id')
register_api(view=EscapeRoomUnit, endpoint='escape-room', url='/api/escape-room/', pk='build_id')
register_api(view=EscapeRoomWorkout, endpoint='team', url='/api/escape-room/team/', pk='build_id')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080, threaded=True)
