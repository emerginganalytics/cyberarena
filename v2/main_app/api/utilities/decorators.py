from flask import abort, session
from functools import wraps
from main_app_utilities.gcp.arena_authorizer import ArenaAuthorizer


__author__ = "Andrew Bomberger"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Andrew Bomberger"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


def auth_required(f):
    """General user authentication. Includes: students, instructors, admins"""
    @wraps(f)
    def decorator(*args, **kwargs):
        auth = ArenaAuthorizer()
        user_email = session.get('user_email', None)
        if user_email:
            auth_list = auth.get_user_groups(user=user_email)
            if auth.UserGroups.PENDING not in auth_list:
                return f(*args, **kwargs)
        else:
            abort(401)
    return decorator


def instructor_required(f):
    """Enforces instructor or greater authentication"""
    @wraps(f)
    def decorator(*args, **kwargs):
        auth = ArenaAuthorizer()
        user_email = session.get('user_email', None)
        if user_email:
            auth_list = auth.get_user_groups(user=user_email)
            if auth.UserGroups.AUTHORIZED in auth_list:
                return f(*args, **kwargs)
            else:
                abort(401)
        else:
            abort(401)
    return decorator


def admin_required(f):
    """Enforces admin authentication"""
    @wraps(f)
    def decorator(*args, **kwargs):
        auth = ArenaAuthorizer()
        user_email = session.get('user_email', None)
        if user_email:
            auth_list = auth.get_user_groups(user=user_email)
            if auth.UserGroups.ADMINS in auth_list:
                return f(*args, **kwargs)
            abort(401)
        abort(401)
    return decorator
