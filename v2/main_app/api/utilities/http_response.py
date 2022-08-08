import json


class HttpResponse:
    """Takes input http code and returns json formatted response"""
    def __init__(self, code, msg=None):
        self.http_codes = {
            200: "OK",
            400: "BAD REQUEST",
            403: "UNAUTHORIZED",
            404: "NOT FOUND",
            405: "NOT ALLOWED",
            409: "CONFLICT",
            500: "INTERNAL SERVER ERROR"
        }
        self.code = code
        self.msg = msg
        # Return HTTP Response based on input code
        self.prepare_response()

    def prepare_response(self):
        if not self.msg:
            return json.dumps({'status': self.code, 'message': self.http_codes[self.code]})
        else:
            return json.dumps({'status': self.code, 'message': self.msg})
