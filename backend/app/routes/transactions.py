from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from ..extensions import db
from ..models import Transaction
from ..services.transactions import create_transaction as service_create, delete_transaction as service_delete, list_transactions as service_list, update_transaction as service_update
from ..utils.responses import error, success

tx_bp = Blueprint("transactions", __name__)


@tx_bp.route("", methods=["GET"])
@jwt_required()
def list_transactions():
    user_id = int(get_jwt_identity())
    payload = service_list(user_id, request.args.to_dict())
    return success(payload)


@tx_bp.route("", methods=["POST"])
@jwt_required()
def create_transaction():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    tx, validation_errors = service_create(user_id, data)
    if validation_errors:
        return error("Could not create transaction", 400, validation_errors)
    return success(tx, status=201)


@tx_bp.route("/<int:tx_id>", methods=["GET"])
@jwt_required()
def get_transaction(tx_id):
    user_id = int(get_jwt_identity())
    tx = Transaction.query.filter_by(id=tx_id, user_id=user_id).first_or_404()
    return success(tx.to_dict())


@tx_bp.route("/<int:tx_id>", methods=["PATCH"])
@jwt_required()
def update_transaction(tx_id):
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    tx, validation_errors = service_update(user_id, tx_id, data)
    if validation_errors:
        return error("Could not update transaction", 400, validation_errors if isinstance(validation_errors, dict) else {"error": validation_errors})
    return success(tx)


@tx_bp.route("/<int:tx_id>", methods=["DELETE"])
@jwt_required()
def delete_transaction(tx_id):
    user_id = int(get_jwt_identity())
    ok, validation_errors = service_delete(user_id, tx_id)
    if validation_errors:
        return error("Could not delete transaction", 400, validation_errors)
    return success({"deleted": True})
