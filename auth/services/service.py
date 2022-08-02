from typing import Optional

from flask_jwt_extended import get_jwt_identity, create_access_token, create_refresh_token
from werkzeug.security import check_password_hash, generate_password_hash

from api import redis, db
# <<<<<<< HEAD:auth/services.py
# from datamodels import JWTTokens, JWTIdentity, Msg, LoginHistory
from models import User, UserLoginHistory, Role
from services.datamodels import JWTTokens, JWTIdentity, Msg, LoginHistory



def get_user_id_in_jwt_token() -> str:
    return get_jwt_identity()['user_id']


def add_user_in_white_list(user_id: str, user_agent: str) -> None:
    redis.sadd(user_id, user_agent)


def check_login_user(email: str, password: str) -> dict:
    user = User.query.filter_by(email=email).first()
    if not user:
        return {"msg": "email is not registered"}
    elif not check_password_hash(user.password, password):
        return {"msg": "please check you password"}
    else:
        return {"msg": "ok", "user_id": user.id}


def add_user_login_history(user_id: str) -> None:
    db.session.add(UserLoginHistory(user_id=user_id))
    db.session.commit()


def create_jwt_tokens(identity: JWTIdentity) -> JWTTokens:
    return JWTTokens(
        access_token=create_access_token(identity),
        refresh_token=create_refresh_token(identity)
    )


def create_new_user(email: str, name: str, password: str) -> Msg:
    if email and name and password:
        user = User.query.filter_by(email=email).first()
        if user:
            return Msg(msg="email already exists")
        new_user = User(
            email=email,
            name=name,
            password=generate_password_hash(password),
            roles=[]
        )
        db.session.add(new_user)
        db.session.commit()
        return Msg(msg="signup success")
    return Msg(msg="please enter email, name, password")


def logout_user(user_id: str, user_agent: str, logout_all: Optional[str]) -> Msg:
    if logout_all == "all":
        redis.delete(user_id)
        return Msg(msg="logout for all devices success")
    else:
        redis.srem(user_id, user_agent)
        return Msg(msg="logout success")


def get_user_login_history(user_id: str, page_num: int, page_size: int) -> LoginHistory:
    history_list = UserLoginHistory.query.filter_by(user_id=user_id).paginate(
        int(page_num),
        int(page_size),
        True
    ).items
    history_list = [h.datestamp for h in history_list]
    return LoginHistory(history=history_list)


def check_edit_user_data(user_id: str, email: str, name: str, password: str) -> Msg:
    user = User.query.filter_by(id=user_id).first()
    if password:
        if check_password_hash(user.password, password):
            return Msg(msg="password must be different from the current")
        else:
            user.password = generate_password_hash(password)
    if email:
        _user = User.query.filter_by(email=email).first()
        if _user:
            return Msg(msg="email already exists")
        if user.email == email:
            return Msg(msg="email must be different from the current")
        else:
            user.email = email
    if name:
        if user.name == name:
            return Msg(msg="name must be different from the current")
        else:
            user.name = name
    if not password and not email and not name:
        return Msg(msg="no data to change")
    db.session.commit()
    return Msg(msg="user data edit success")


"""
ROLES AND PERMISSIONS
"""


def create_new_role(name):
    if name:
        role = Role.query.filter_by(name=name).first()
        if role:
            return Msg(msg=f'The role has already existed')
        new_role = Role(name=name)

        db.session.add(new_role)
        db.session.commit()
        return Msg(msg=f'The role {name} has created')
    else:
        Msg(msg='please enter name')


def get_role_service(name):
    if name:
        role = Role.query.filter_by(name=name).first()
        if not role:
            return Msg(msg='Error in finding role')
        return Msg(msg=f'Role {name}')
    else:
        Msg(msg='please enter name')


def delete_role_service(name):
    if name:
        role = Role.query.filter_by(name=name).first()
        if not role:
            return Msg(msg='Error in finding role')
        db.session.delete(role)
        db.session.commit()
        return Msg(msg=f'The role {name} has deleted')
    else:
        Msg(msg='please enter name')


def create_user_role(name_user, name_role):
    if name_user and name_role:
        user = User.query.filter_by(name=name_user).first()
        role = Role.query.filter_by(name=name_role).first()
        user.roles.append(role)
        db.session.commit()
        return Msg(msg='The role has edited to user')
    else:
        return Msg(msg='Please, enter user name and role name')


def get_roles_service():
    roles = Role.query.all()
    if not roles:
        return Msg(msg='no created roles')
    return [iter.serialize() for iter in roles]


def delete_user_role_service(name_user, name_role):
    if name_user and name_role:
        user = User.query.filter_by(name=name_user).first()
        role = Role.query.filter_by(name=name_role).first()
        if role in user.roles:
            user.roles.remove(role)
        else:
            return Msg(msg=f'The user has not had {name_role} role')
        db.session.commit()
        return Msg(msg='The role has deleted to user')
    return Msg(msg='Please print name of user and name of role')


def get_user_role_service(name_user):
    if name_user:
        user = User.query.filter_by(name=name_user).first()
        return [iter.serialize() for iter in user.roles]
    return Msg(msg='Please enter name of user')
