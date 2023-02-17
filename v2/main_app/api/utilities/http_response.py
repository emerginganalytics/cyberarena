from flask import Response, json
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
        resp_data = {
            'status': self.code,
            'message': self.http_codes[self.code],
            'data': []
        }
        if self.msg:
            resp_data['message'] = self.msg
        if self.data:
            resp_data['data'] = self.data
        json_obj = json.dumps(resp_data, cls=self.DateTimeEncoder)
        response = Response(json_obj, mimetype='application/json')
        response.status_code = self.code
        return response

    class DateTimeEncoder(json.JSONEncoder):
        def default(self, o):
            if isinstance(o, datetime):
                return o.isoformat()
            return super().default(o)
