from flask.views import View, MethodView
from api.decorators import auth_required, admin_required, instructor_required


__author__ = "Andrew Bomberger"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Andrew Bomberger"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class Injector(MethodView):
    decorators = [auth_required]

    def get(self, inject_id=None):
        """Get Inject Status"""
        if inject_id:
            return f'{inject_id}'
        return 'INJECTOR'

    def post(self):
        """Create Inject"""
        pass

    def delete(self, user_id):
        pass

    def put(self, user_id):
        """Update Existing Inject"""
        pass
