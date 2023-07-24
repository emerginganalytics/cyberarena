from flask import jsonify
from datetime import datetime
import json


class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        return super().default(o)


class HttpResponse:
    """
    Takes input http code and returns json formatted response
    """
    http_codes = {
        200: "OK",
        205: "RESET CONTENT",
        302: "FOUND",
        307: "TEMPORARY REDIRECT",
        400: "BAD REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT FOUND",
        405: "NOT ALLOWED",
        409: "CONFLICT",
        500: "INTERNAL SERVER ERROR",
        501: "NOT IMPLEMENTED",
    }

    def __init__(self, code, msg=None, data=None):
        self.code = code
        self.msg = msg
        self.data = data

    def prepare_response(self):
        resp_data = {
            'status': self.code,
            'message': self.http_codes.get(self.code, "UNKNOWN"),
            'data': self.data or []
        }
        if self.msg:
            resp_data['message'] = self.msg

        return jsonify(resp_data), self.code
