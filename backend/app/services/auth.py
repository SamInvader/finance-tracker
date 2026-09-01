from flask_jwt_extended import create_access_token

from ..extensions import db
from ..models import User
from ..schemas.validators import validate_email, validate_password
from .defaults import seed_user_defaults


def register_user(data):
    errors = {}
    email = (data.get("email") or "").strip().lower()
    name = (data.get("name") or "").strip()
    password = data.get("password") or ""
    confirm = data.get("confirm_password")
    email_err = validate_email(email)
    if email_err:
        errors["email"] = email_err
    if not name:
        errors["name"] = "Name is required"
    pwd_err = validate_password(password, confirm)
    if pwd_err:
        errors["password"] = pwd_err
    if User.query.filter_by(email=email).first():
        errors["email"] = "An account with this email already exists"
    if errors:
        return None, errors
    user = User(email=email, name=name)
    user.set_password(password)
    db.session.add(user)
    db.session.flush()
    seed_user_defaults(user)
    db.session.commit()
    db.session.refresh(user)
    token = create_access_token(identity=str(user.id))
    prefs = user.preference.to_dict() if user.preference else {}
    return {"user": user.to_dict(), "token": token, "preferences": prefs}, None


def login_user(data):
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return None, "Invalid email or password"
    token = create_access_token(identity=str(user.id))
    return {"user": user.to_dict(), "token": token, "preferences": user.preference.to_dict() if user.preference else {}}, None
