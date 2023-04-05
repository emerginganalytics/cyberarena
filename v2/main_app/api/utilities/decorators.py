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
        if user_email := session.get('user_email', None):
            if auth.authorized(email=user_email, base=auth.UserGroups.STUDENT):
                return f(*args, **kwargs)
        abort(401)
    return decorator


def instructor_required(f):
    """Enforces instructor or greater authentication"""
    @wraps(f)
    def decorator(*args, **kwargs):
        auth = ArenaAuthorizer()
        if user_email := session.get('user_email', None):
            if auth.authorized(email=user_email, base=auth.UserGroups.INSTRUCTOR):
                return f(*args, **kwargs)
        abort(401)
    return decorator


def admin_required(f):
    """Enforces admin authentication"""
    @wraps(f)
    def decorator(*args, **kwargs):
        auth = ArenaAuthorizer()
        if user_email := session.get('user_email', None):
            if auth.authorized(email=user_email, base=auth.UserGroups.ADMIN):
                return f(*args, **kwargs)
        abort(401)
    return decorator
