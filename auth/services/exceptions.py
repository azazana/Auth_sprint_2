from api import app
from flask import jsonify


class AuthError(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['msg'] = self.message
        return rv


class OauthProviderError(AuthError):
    pass


class LoginError(AuthError):
    pass


class RoleError(AuthError):
    pass


@app.errorhandler(OauthProviderError)
def oauth_provider_error(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.errorhandler(LoginError)
def oauth_provider_error(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response
