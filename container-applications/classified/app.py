import base64
import onetimepass
import os
from flask import abort, Flask, redirect
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, UserMixin
from flask_sqlalchemy import SQLAlchemy
from globals import ds_client
from werkzeug.security import check_password_hash, generate_password_hash

# App Blueprint imports
from arena_snake.routes import arena_snake_bp
from inspect_workout.routes import inspect_bp
from sql_injection.routes import sql_injection_bp
from twofactorauth.routes import twofactorauth_bp
from wireshark.routes import wireshark_bp
from xss.routes import xss_bp

# Application instance
app = Flask(__name__)
app.secret_key = os.urandom(12)
bootstrap = Bootstrap(app)

# db Config
db = SQLAlchemy(app)
lm = LoginManager(app)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


class User(UserMixin, db.Model):
    """User model."""
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True)
    password_hash = db.Column(db.String(128))
    otp_secret = db.Column(db.String(16))

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.otp_secret is None:
            # generate a random secret
            self.otp_secret = base64.b32encode(os.urandom(10)).decode('utf-8')

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_totp_uri(self):
        return 'otpauth://totp/CyberGym:{0}?secret={1}&issuer=CyberGym2FA'.format(self.username, self.otp_secret)

    def verify_totp(self, token):
        return onetimepass.valid_totp(token, self.otp_secret)


@lm.user_loader
def load_user(user_id):
    """User loader callback for Flask-Login."""
    return User.query.get(int(user_id))


# Register app blueprints
app.register_blueprint(arena_snake_bp)
app.register_blueprint(inspect_bp)
app.register_blueprint(sql_injection_bp)
app.register_blueprint(twofactorauth_bp)
app.register_blueprint(wireshark_bp)
app.register_blueprint(xss_bp)


@app.route('/<workout_id>')
def loader(workout_id):
    key = ds_client.key('cybergym-workout', workout_id)
    workout = ds_client.get(key)

    # Verify that request is for a valid workout and redirect based on type
    valid_types = {
        'wireshark': '/%s' % workout_id,
        'xss': '/xss/xss_d/%s' % workout_id,
        '2fa': '/tfh/%s' % workout_id,
        'inspect': '/inspect/%s' % workout_id,
        'sql_injection': '/sql_injection/%s' % workout_id,
        'arena_snake': '/arena_snake/%s' % workout_id
    }
    if workout:
        workout_type = workout['type']
        if workout_type in valid_types:
            # Any route specific logic is handled at the individual blueprint
            # level. Return redirect to specific blueprint
            return redirect(valid_types[workout_type])
    else:
        return abort(404)


# Create database if none exist
db.create_all()

if __name__ == "__main__":
    # app.run(debug=True, host='0.0.0.0', port=4000)
    app.run(debug=True)

