from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from ..services.goals import create_goal as service_create, contribute, list_goals as service_list, update_goal
from ..utils.responses import error, success

goals_bp = Blueprint("goals", __name__)


@goals_bp.route("", methods=["GET"])
@jwt_required()
def list_goals():
    user_id = int(get_jwt_identity())
    return success(service_list(user_id))


@goals_bp.route("", methods=["POST"])
@jwt_required()
def create_goal():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    goal, validation_errors = service_create(user_id, data)
    if validation_errors:
        return error("Could not create goal", 400, validation_errors)
    return success(goal, status=201)


@goals_bp.route("/<int:gid>", methods=["GET"])
@jwt_required()
def get_goal(gid):
    user_id = int(get_jwt_identity())
    goals = service_list(user_id)
    goal = next((g for g in goals if g["id"] == gid), None)
    if not goal:
        return error("Goal not found", 404)
    return success(goal)


@goals_bp.route("/<int:gid>", methods=["PUT"])
@jwt_required()
def update_goal_route(gid):
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    goal, validation_errors = update_goal(user_id, gid, data)
    if validation_errors:
        return error("Could not update goal", 400, validation_errors)
    return success(goal)


@goals_bp.route("/<int:gid>", methods=["DELETE"])
@jwt_required()
def delete_goal(gid):
    user_id = int(get_jwt_identity())
    from ..models import SavingsGoal

    savings_goal = SavingsGoal.query.filter_by(id=gid, user_id=user_id).first()
    if not savings_goal:
        return error("Goal not found", 404)
    from ..extensions import db

    db.session.delete(savings_goal)
    db.session.commit()
    return success({"deleted": True})


@goals_bp.route("/<int:gid>/deposit", methods=["POST"])
@jwt_required()
def deposit_goal(gid):
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    result, validation_errors = contribute(user_id, gid, data)
    if validation_errors:
        return error("Could not deposit to goal", 400, validation_errors)
    return success(result["goal"], status=201)
