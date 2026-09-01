from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from ..extensions import db
from ..models import Account
from ..utils.money import to_minor
from ..utils.responses import error, success

accounts_bp = Blueprint("accounts", __name__)


@accounts_bp.route("", methods=["GET"])
@jwt_required()
def list_accounts():
    user_id = int(get_jwt_identity())
    accounts = Account.query.filter_by(user_id=user_id).all()
    return success({"accounts": [a.to_dict() for a in accounts]})


@accounts_bp.route("/<int:account_id>", methods=["GET"])
@jwt_required()
def get_account(account_id):
    user_id = int(get_jwt_identity())
    account = Account.query.filter_by(id=account_id, user_id=user_id).first()
    if not account:
        return error("Account not found", 404)
    return success(account.to_dict())


@accounts_bp.route("", methods=["POST"])
@jwt_required()
def create_account():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    name = data.get("name")
    if not name:
        return error("name required", 400)
    try:
        balance_minor = to_minor(data.get("balance", 0) or 0)
    except ValueError as exc:
        return error(str(exc), 400)
    account = Account(
        user_id=user_id,
        name=name,
        type=data.get("type", "cash"),
        balance_minor=balance_minor,
        currency=(data.get("currency") or "NGN").upper(),
        institution=data.get("institution"),
        notes=data.get("notes"),
        is_active=bool(data.get("is_active", True)),
    )
    db.session.add(account)
    db.session.commit()
    return success(account.to_dict(), status=201)
