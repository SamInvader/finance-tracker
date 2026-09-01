from functools import wraps

from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

from .responses import error


def current_user_id() -> int:
    identity = get_jwt_identity()
    return int(identity)


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
        except Exception:
            return error("Authentication required", 401)
        return fn(*args, **kwargs)

    return wrapper
