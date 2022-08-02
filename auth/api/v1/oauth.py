import os

from flask import Blueprint, request, jsonify
from services.datamodels import JWTIdentity, Msg
from utils.mail import send_mail
from services.oauth_google import get_user_scope, authorization_url
from services.service import (
    add_user_in_white_list,
    check_login_user,
    create_jwt_tokens,
    create_new_user,
)
from utils.util import generate_random_password

oauth = Blueprint('oauth', __name__)


@oauth.route('/oauth/callback', methods=['GET'])
def auth_users():
    """login user by Oauth info
        login user by Oauth info
        If all ok create and return access and refresh jwt tokens
        ---
        responses:
          200:
            description: create access and refresh tokens after Oauth
            schema:
              id: jwt_tokens
    """
    user_scope = get_user_scope(request.url)

    email = user_scope["email"]
    name = user_scope["name"]
    password = generate_random_password()
    user_agent = request.headers.get("User-Agent")

    create_user = create_new_user(email, name, password)
    if create_user["msg"] != "signup success":
        return jsonify(create_user)

    if os.getenv("FLASK_ENV") == "development":
        print(password)  # send password to user email (delete in prod)
    send_mail("You password in Movies website", email, password)

    login = check_login_user(email, password)
    if login["msg"] != "ok":
        return jsonify(login)
    add_user_in_white_list(str(login["user_id"]), user_agent)
    # add_user_login_history(login["user_id"])

    identity = JWTIdentity(
        user_id=login["user_id"]
    )

    return jsonify(create_jwt_tokens(identity))


@oauth.route('/oauth', methods=['GET'])
def get_oauth_link():
    """get link to oauth users
        get link to oauth users
        ---
        responses:
          200:
            description: get link to oauth users
    """
    msg = Msg(msg=f"Please go here and authorize: {authorization_url}")
    return jsonify(msg)
