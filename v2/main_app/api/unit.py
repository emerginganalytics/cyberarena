from flask import request
from flask.views import MethodView
from api.utilities.decorators import instructor_required
from api.utilities.http_response import HttpResponse

__author__ = "Andrew Bomberger"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Andrew Bomberger"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class Unit(MethodView):
    """Method View to handle API requests for Cyber Arena Units"""
    decorators = [instructor_required]

    def __init__(self):
        self.http_resp = HttpResponse

    def get(self, build_id=None):
        # TODO: Add GET logic
        args = request.args
        if build_id:
            pass
        # Invalid request; No build_id given
        return self.http_resp(code=400)

    def post(self):
        # TODO: Add POST logic
        return self.http_resp(code=400)

    def delete(self):
        # TODO: Add DELETE logic
        return self.http_resp(code=400)

    def put(self):
        # TODO: Add PUT logic
        return self.http_resp(code=400)
