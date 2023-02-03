import json
from datetime import datetime


class HttpResponse:
    """Takes input http code and returns json formatted response"""
    def __init__(self, code, msg=None, data=None):
        self.http_codes = {
            200: "OK",
            205: "RESET CONTENT",
            400: "BAD REQUEST",
            403: "UNAUTHORIZED",
            404: "NOT FOUND",
            405: "NOT ALLOWED",
            409: "CONFLICT",
            500: "INTERNAL SERVER ERROR",
            501: "NOT IMPLEMENTED",
        }
        self.code = code
        self.msg = msg
        self.data = data

    def prepare_response(self):
        response = {
            'status': self.code,
            'message': self.http_codes[self.code],
            'data': []
        }
        if self.msg:
            response['message'] = self.msg
        if self.data:
            response['data'] = self.data
        return json.dumps(response, cls=self.DateTimeEncoder)

    class DateTimeEncoder(json.JSONEncoder):
        def default(self, o):
            if isinstance(o, datetime):
                return o.isoformat()
            return super().default(o)
