from api import redis, db
from models import User, UserLoginHistory, Role
from services.datamodels import JWTTokens, JWTIdentity, Msg, LoginHistory
from services.exceptions import RoleError


def create_new_role(name):
    if name:
        role = Role.query.filter_by(name=name).first()
        if role:
            raise RoleError(f"The role has already existed")
        new_role = Role(name=name)

        db.session.add(new_role)
        db.session.commit()
        return Msg(msg=f"The role {name} has created")
    else:
        raise RoleError("please enter name")


def get_role_service(name):
    if name:
        role = Role.query.filter_by(name=name).first()
        if not role:
            raise RoleError("Error in finding role")
        return Msg(msg=f"Role {name}")
    else:
        raise RoleError("please enter name")


def delete_role_service(name):
    if name:
        role = Role.query.filter_by(name=name).first()
        if not role:
            raise RoleError("Error in finding role")
        db.session.delete(role)
        db.session.commit()
        return Msg(msg=f"The role {name} has deleted")
    else:
        raise RoleError("please enter name")


def create_user_role(name_user, name_role):
    if name_user and name_role:
        user = User.query.filter_by(name=name_user).first()
        role = Role.query.filter_by(name=name_role).first()
        user.roles.append(role)
        db.session.commit()
        return Msg(msg="The role has edited to user")
    else:
        raise RoleError("Please, enter user name and role name")


def get_roles_service():
    roles = Role.query.all()
    if not roles:
        return Msg(msg="no created roles")
    return [iter.serialize() for iter in roles]


def delete_user_role_service(name_user, name_role):
    if name_user and name_role:
        user = User.query.filter_by(name=name_user).first()
        role = Role.query.filter_by(name=name_role).first()
        if role in user.roles:
            user.roles.remove(role)
        else:
            raise RoleError(f"The user has not had {name_role} role")
        db.session.commit()
        return Msg(msg="The role has deleted to user")
    raise RoleError("Please print name of user and name of role")


def get_user_role_service(name_user):
    if name_user:
        user = User.query.filter_by(name=name_user).first()
        return [iter.serialize() for iter in user.roles]
    raise RoleError("Please enter name of user")


def get_user_roles(user_id: str) -> list[str]:
    user = User.query.filter_by(id=user_id).first()
    return [role.name for role in user.roles]

