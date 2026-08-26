from flask import Blueprint, request, jsonify
from backend.app.extensions import db
from backend.app.models import Account
from flask_jwt_extended import jwt_required, get_jwt_identity

accounts_bp = Blueprint("accounts", __name__)


@accounts_bp.route("/", methods=["GET"])
@jwt_required()
def list_accounts():
    user_id = int(get_jwt_identity())
    accounts = Account.query.filter_by(user_id=user_id).all()
    return jsonify(
        [
            {
                "id": a.id,
                "name": a.name,
                "type": a.type,
                "balance": float(a.balance),
                "currency": a.currency,
                "institution": a.institution,
                "notes": a.notes,
                "active": a.active,
            }
            for a in accounts
        ]
    )


@accounts_bp.route("/", methods=["POST"])
@jwt_required()
def create_account():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    name = data.get("name")
    if not name:
        return jsonify({"msg": "name required"}), 400
    account = Account(
        user_id=user_id,
        name=name,
        type=data.get("type", "cash"),
        balance=data.get("balance", 0.0),
        currency=data.get("currency", "NGN"),
        institution=data.get("institution"),
    )
    db.session.add(account)
    db.session.commit()
    return jsonify({"id": account.id}), 201
