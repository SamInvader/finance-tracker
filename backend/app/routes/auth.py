from flask import Blueprint, request, jsonify
from backend.app.extensions import db
from backend.app.models import User
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
    get_jwt,
)
from backend.app.extensions import token_blocklist

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")
    name = data.get("name")
    if not email or not password:
        return jsonify({"msg": "email and password required"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"msg": "email already registered"}), 400
    user = User(email=email, name=name)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
        access = create_access_token(
            identity=str(user.id)
        )
    return (
        jsonify(
            {
                "access_token": access,
                "user": {"id": user.id, "email": user.email, "name": user.name},
            }
        ),
        201,
    )


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"msg": "Invalid credentials"}), 401
        access = create_access_token(
            identity=str(user.id)
        )
    return jsonify(
        {
            "access_token": access,
            "user": {"id": user.id, "email": user.email, "name": user.name},
        }
    )


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    return jsonify({"id": user.id, "email": user.email, "name": user.name})


@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    jti = get_jwt().get("jti")
    token_blocklist.add(jti)
    return jsonify({"msg": "successfully logged out"})


@auth_bp.route("/change-password", methods=["POST"])
@jwt_required()
def change_password():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    data = request.get_json() or {}
    old = data.get("old_password")
    new = data.get("new_password")
    if not old or not new:
        return jsonify({"msg": "old_password and new_password required"}), 400
    if not user.check_password(old):
        return jsonify({"msg": "old password incorrect"}), 401
    user.set_password(new)
    db.session.commit()
    # revoke current token
    jti = get_jwt().get("jti")
    token_blocklist.add(jti)
    return jsonify({"msg": "password changed"})
