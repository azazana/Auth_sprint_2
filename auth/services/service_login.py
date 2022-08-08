from typing import Optional

from api import redis, db
from flask import jsonify
from flask_jwt_extended import (
    get_jwt_identity,
    create_access_token,
    create_refresh_token,
)
from models import User, UserLoginHistory, Role
from services.datamodels import JWTTokens, JWTIdentity, Msg, LoginHistory
from services.exceptions import LoginError
from werkzeug.security import check_password_hash, generate_password_hash


def get_user_id_in_jwt_token() -> str:
    return get_jwt_identity()["user_id"]


def add_user_in_white_list(user_id: str, user_agent: str) -> None:
    redis.sadd(user_id, user_agent)


def check_login_user(email: str, password: str) -> str:
    user = User.query.filter_by(email=email).first()
    if not user:
        raise LoginError("email is not registered")
    elif not check_password_hash(user.password, password):
        raise LoginError("please check you password")
    else:
        return str(user.id)


def add_user_login_history(user_id: str) -> None:
    db.session.add(UserLoginHistory(user_id=user_id))
    db.session.commit()


def login_user_get_token(email, password, user_agent):
    user_id = check_login_user(email, password)

    add_user_in_white_list(user_id, user_agent)
    add_user_login_history(user_id)

    identity = JWTIdentity(user_id=user_id)

    return jsonify(create_jwt_tokens(identity))


def create_jwt_tokens(identity: JWTIdentity) -> JWTTokens:
    return JWTTokens(
        access_token=create_access_token(identity),
        refresh_token=create_refresh_token(identity),
    )


def create_new_user(email: str, name: str, password: str) -> Msg:
    if email and name and password:
        user = User.query.filter_by(email=email).first()
        if user:
            raise LoginError("email already exists")
        new_user = User(
            email=email, name=name, password=generate_password_hash(password), roles=[]
        )
        db.session.add(new_user)
        db.session.commit()
        return Msg(msg="signup success")
    raise LoginError("please enter email, name, password")


def logout_user(user_id: str, user_agent: str, logout_all: Optional[str]) -> Msg:
    if logout_all == "all":
        redis.delete(user_id)
        return Msg(msg="logout for all devices success")
    else:
        redis.srem(user_id, user_agent)
        return Msg(msg="logout success")


def get_user_login_history(user_id: str, page_num: int, page_size: int) -> LoginHistory:
    history_list = (
        UserLoginHistory.query.filter_by(user_id=user_id)
            .paginate(int(page_num), int(page_size), True)
            .items
    )
    history_list = [h.datestamp for h in history_list]
    return LoginHistory(history=history_list)


def check_edit_user_data(user_id: str, email: str, name: str, password: str) -> Msg:
    user = User.query.filter_by(id=user_id).first()
    if password:
        if check_password_hash(user.password, password):
            raise LoginError("password must be different from the current")
        else:
            user.password = generate_password_hash(password)
    if email:
        _user = User.query.filter_by(email=email).first()
        if _user:
            raise LoginError("email already exists")
        if user.email == email:
            raise LoginError("email must be different from the current")
        else:
            user.email = email
    if name:
        if user.name == name:
            raise LoginError("name must be different from the current")
        else:
            user.name = name
    if not password and not email and not name:
        return Msg(msg="no data to change")
    db.session.commit()
    return Msg(msg="user data edit success")

