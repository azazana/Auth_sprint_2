from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from services.service import (
    get_user_id_in_jwt_token,
    add_user_in_white_list,
    check_login_user,
    add_user_login_history,
    create_jwt_tokens,
    create_new_user,
    logout_user,
    get_user_login_history,
    check_edit_user_data,
    login_user_get_token,
)
from utils.util import check_logout_user
from utils.ratelimiter import rate_limit

auth = Blueprint("auth", __name__)


@auth.route("/login", methods=["POST"])
@rate_limit([(1, 10), (60, 100), (3600, 250)])
def login_users():
    """login user by email and password
    login user by email and password.
    If all ok create and return access and refresh jwt tokens
    ---
    parameters:
      - in: query
        name: email
        required: true
        type: string
      - in: query
        name: password
        required: true
        type: string
    responses:
      200:
        description: create access and refresh tokens
        schema:
          id: jwt_tokens
          properties:
            access_token:
              type: string
              description: JWT access token
            refresh_token:
              type: string
              description: JWT refresh token
    """
    email = request.args["email"]
    password = request.args["password"]
    user_agent = request.headers.get("User-Agent")
    return login_user_get_token(email, password, user_agent)



@auth.route("/signup", methods=["POST"])
@rate_limit([(1, 10), (60, 100), (3600, 250)])
def signup_users():
    """signup user by email and password and name
    signup user by email and password and name.
    If all ok create user in Postgres and success msg
    ---
    parameters:
      - in: query
        name: email
        required: true
        type: string
      - in: query
        name: password
        required: true
        type: string
      - in: query
        name: name
        required: true
        type: string
    responses:
      200:
        description: create user in Postgres
        schema:
          id: json_msg
          properties:
            msg:
              type: string
              description: message
    """
    email = request.args.get("email")
    name = request.args.get("name")
    password = request.args.get("password")

    return jsonify(create_new_user(email, name, password))


@auth.route("/logout", methods=["POST"])
@jwt_required()
@check_logout_user
@rate_limit([(1, 10), (60, 100), (3600, 250)])
def logout_users():
    """logout user in system
    logout user with correctly jwt token,
    If arg "all" = "all" logout from all devices
    ---
    parameters:
      - in: header
        name: Authorization
        required: true
        type: string
        description: Authorization token
      - in: query
        name: all
        type: string
        enum: ['all', ]
    responses:
      200:
        description: logout user
        schema:
          id: json_msg
          properties:
            msg:
              type: string
              description: message
    """
    user_agent = request.headers.get("User-Agent")
    logout_all = request.args.get("all")
    user_id = get_user_id_in_jwt_token()

    return jsonify(logout_user(user_id, user_agent, logout_all))


@auth.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
@check_logout_user
@rate_limit([(1, 10), (60, 100), (3600, 250)])
def refresh_tokens():
    """refresh jwt tokens user by fresh refresh token
    refresh jwt tokens user by fresh refresh token
    Return new refresh and access tokens
    ---
    parameters:
    - in: header
      name: Authorization
      required: true
      type: string
      description: Authorization token
    responses:
      200:
        description: refresh access and refresh tokens
        schema:
          id: jwt_tokens
    """
    identity = get_jwt_identity()
    return jsonify(create_jwt_tokens(identity))


@auth.route("/profile/login_history", methods=["GET"])
@jwt_required()
@check_logout_user
@rate_limit([(1, 10), (60, 100), (3600, 250)])
def profile_user_login_history():
    """get user login history
    get user login history by fresh access token
    ---
    parameters:
      - in: header
        name: Authorization
        required: true
        type: string
      - in: query
        name: page_size
        type: int
        default: 10
      - in: query
        name: page_num
        type: int
        default: 1
    responses:
      200:
        description: user login history, list datestamp login
        schema:
          id: user_login_history
          type: object
          properties:
            history:
              type: array
              items:
                schema:
                  id: datestamp
                  type: string
    """
    user_id = get_user_id_in_jwt_token()
    page_num = request.args.get("page_num") or 1
    page_size = request.args.get("page_size") or 10

    return jsonify(get_user_login_history(user_id, page_num, page_size))


@auth.route("/profile", methods=["PUT"])
@jwt_required()
@check_logout_user
@rate_limit([(1, 10), (60, 100), (3600, 250)])
def profile_user_edit():
    """edit data user: email or/and password or/and name
    edit data user: email or/and password or/and name
    If all ok edit data in Postgres and success msg
    ---
    parameters:
      - in: query
        name: email
        type: string
      - in: query
        name: password
        type: string
      - in: query
        name: name
        type: string
    responses:
      200:
        description: edit user data in Postgres
        schema:
          id: json_msg
    """
    email = request.args.get("email")
    name = request.args.get("name")
    password = request.args.get("password")
    user_id = get_user_id_in_jwt_token()

    return jsonify(check_edit_user_data(user_id, email, name, password))
