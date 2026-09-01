from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_

from ..extensions import db
from ..models import Category
from ..utils.responses import error, success

categories_bp = Blueprint("categories", __name__)


@categories_bp.route("", methods=["GET"])
@jwt_required()
def list_categories():
    user_id = int(get_jwt_identity())
    cats = Category.query.filter(
        or_(Category.user_id.is_(None), Category.user_id == user_id)
    ).all()
    return success([
        {
            "id": c.id,
            "name": c.name,
            "kind": c.kind,
            "color": c.color,
            "icon": c.icon,
            "user_id": c.user_id,
        }
        for c in cats
    ])


@categories_bp.route("", methods=["POST"])
@jwt_required()
def create_category():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    name = data.get("name")
    kind = data.get("kind") or data.get("type")
    if not name or not kind:
        return error("name and kind required", 400)
    cat = Category(
        user_id=user_id,
        name=name,
        kind=kind,
        color=data.get("color"),
        icon=data.get("icon"),
    )
    db.session.add(cat)
    db.session.commit()
    return success(cat.to_dict(), status=201)


@categories_bp.route("/<int:cat_id>", methods=["GET"])
@jwt_required()
def get_category(cat_id):
    user_id = int(get_jwt_identity())
    c = Category.query.filter(
        (Category.id == cat_id)
        & ((Category.user_id.is_(None)) | (Category.user_id == user_id))
    ).first_or_404()
    return success({"id": c.id, "name": c.name, "kind": c.kind, "color": c.color, "icon": c.icon})


@categories_bp.route("/<int:cat_id>", methods=["PUT"])
@jwt_required()
def update_category(cat_id):
    user_id = int(get_jwt_identity())
    c = Category.query.filter_by(id=cat_id, user_id=user_id).first_or_404()
    data = request.get_json() or {}
    if "name" in data:
        c.name = data.get("name")
    if "color" in data:
        c.color = data.get("color")
    if "icon" in data:
        c.icon = data.get("icon")
    db.session.commit()
    return success({"msg": "updated"})


@categories_bp.route("/<int:cat_id>", methods=["DELETE"])
@jwt_required()
def delete_category(cat_id):
    user_id = int(get_jwt_identity())
    c = Category.query.filter_by(id=cat_id, user_id=user_id).first_or_404()
    db.session.delete(c)
    db.session.commit()
    return success({"msg": "deleted"})
