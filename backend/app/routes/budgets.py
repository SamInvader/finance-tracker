from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from ..services.budgets import budget_overview, upsert_budget
from ..utils.responses import error, success

budgets_bp = Blueprint("budgets", __name__)


@budgets_bp.route("", methods=["GET"])
@jwt_required()
def list_budgets():
    user_id = int(get_jwt_identity())
    month = request.args.get("month")
    return success(budget_overview(user_id, month))


@budgets_bp.route("", methods=["POST"])
@jwt_required()
def create_budget():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    try:
        overview, validation_errors = upsert_budget(user_id, data)
        if validation_errors:
            return error("Could not create budget", 400, validation_errors)
        return success(overview, status=201)
    except Exception as exc:  # pragma: no cover
        return error(str(exc), 400)


@budgets_bp.route("", methods=["PUT"])
@jwt_required()
def update_budget():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    overview, validation_errors = upsert_budget(user_id, data)
    if validation_errors:
        return error("Could not update budget", 400, validation_errors)
    return success(overview)
