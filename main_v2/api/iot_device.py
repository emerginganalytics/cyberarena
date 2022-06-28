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


class IoTDevice(MethodView):
    decorators = [auth_required]

    def get(self, device_id=None):
        """Get device status"""
        if device_id:
            return f'{device_id}'
        return 'IOT DEVICE'

    @auth_required
    def post(self):
        """Create New Device"""
        pass

    @admin_required
    def delete(self, user_id):
        pass

    @instructor_required
    def put(self, user_id):
        """Update Existing Device State"""
        pass
