from flask.views import View, MethodView
from api.utilities import auth_required, admin_required, instructor_required


__author__ = "Andrew Bomberger"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Andrew Bomberger"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class FixedArena(MethodView):
    decorators = [auth_required]

    def get(self, fixed_arena_id=None):
        """Get Classroom"""
        if fixed_arena_id:
            return f'{fixed_arena_id}'
        return 'FIXED ARENA'

    def post(self):
        """Create Classroom"""
        pass

    def delete(self, user_id):
        pass

    def put(self, user_id):
        """Update Existing Classroom"""
        pass
