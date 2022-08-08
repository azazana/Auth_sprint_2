import os

from flask import Blueprint, request, jsonify
from services.datamodels import JWTIdentity, Msg
from services.oauth_providers import match_oauth_provider
from utils.mail import send_mail
from services.service import (
    add_user_in_white_list,
    add_user_login_history,
    create_jwt_tokens,
    create_new_user,
    login_user_get_token,
)
from utils.util import generate_random_password
from models import User

oauth = Blueprint("oauth", __name__)


@oauth.route("/oauth/callback/<provider>", methods=["GET"])
def auth_users(provider):
    """login user by Oauth info
    login user by Oauth info
    If all ok create and return access and refresh jwt tokens
    ---
    parameters:
      - in: path
        name: provider
        required: true
        type: string
    responses:
      200:
        description: create access and refresh tokens after Oauth
        schema:
          id: jwt_tokens
    """
    provider = match_oauth_provider(provider)
    user_scope = provider.get_user_scope(request.url)

    email = user_scope["email"]
    name = user_scope["name"]
    password = generate_random_password()
    user_agent = request.headers.get("User-Agent")

    create_user = create_new_user(email, name, password)
    if create_user["msg"] == "email already exists":
        user = User.query.filter_by(email=email).first()
        identity = JWTIdentity(user_id=user.id)
        add_user_in_white_list(str(user.id), user_agent)
        add_user_login_history(user.id)
        return jsonify(create_jwt_tokens(identity))

    if os.getenv("FLASK_ENV") == "development":
        print(password)  # send password to user email (delete in prod)
    send_mail("You password in Movies website", email, password)

    return login_user_get_token(email, password, user_agent)


@oauth.route("/oauth/<provider>", methods=["GET"])
def get_oauth_link(provider):
    """get link to oauth users
    get link to oauth users
    ---
    parameters:
      - in: path
        name: provider
        required: true
        type: string
    responses:
      200:
        description: get link to oauth users
    """
    provider = match_oauth_provider(provider)
    auth_url = provider.get_authorization_url()
    msg = Msg(msg=f"Please go here and authorize: {auth_url}")
    return jsonify(msg)
