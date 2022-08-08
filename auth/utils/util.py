from functools import wraps
import string
import random

from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity

from api import redis
from models import User


def check_logout_user(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()["user_id"]
        user_agent = request.headers.get("User-Agent")
        if not redis.sismember(name=user_id, value=user_agent):
            return jsonify({"msg": "sorry you are logout go to login"})
        return fn(*args, **kwargs)

    return wrapper


# deprecated
def is_superuser():
    def decorator(f):
        @wraps(f)
        def decorated_func(*args, **kwargs):
            # todo how to find current user?
            user_id = get_jwt_identity()["id"]
            # todo get user id
            current_user = User.query.filter_by(id=user_id).first()
            if current_user.superuser:
                return f(*args, **kwargs)
            return jsonify({"msg": "User does not have permission"})

        return decorated_func

    return decorator


def my_current_user():
    try:
        user_id = get_jwt_identity()["user_id"]
        user = User.query.filter_by(id=user_id).first()
        return user
    except:
        return None


def generate_random_password(length: int = 8) -> str:
    characters = list(string.ascii_letters + string.digits + "!@#$%^&*()")
    random.shuffle(characters)
    password = []
    for i in range(length):
        password.append(random.choice(characters))
    random.shuffle(password)
    return "".join(password)
