from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.app.extensions import db
from backend.app.models import SavingsGoal

goals_bp = Blueprint('goals', __name__)


@goals_bp.route('/', methods=['GET'])
@jwt_required()
def list_goals():
    user_id = int(get_jwt_identity())
    items = SavingsGoal.query.filter_by(user_id=user_id).all()
    return jsonify([{'id': g.id, 'name': g.name, 'target_amount': float(g.target_amount), 'current_amount': float(g.current_amount), 'target_date': g.target_date.isoformat() if g.target_date else None} for g in items])


@goals_bp.route('/', methods=['POST'])
@jwt_required()
def create_goal():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    name = data.get('name')
    target = data.get('target_amount')
    if not name or target is None:
        return jsonify({'msg': 'name and target_amount required'}), 400
    g = SavingsGoal(user_id=user_id, name=name, target_amount=target, current_amount=data.get('current_amount', 0.0), target_date=data.get('target_date'), priority=data.get('priority', 0))
    db.session.add(g)
    db.session.commit()
    return jsonify({'id': g.id}), 201


@goals_bp.route('/<int:gid>', methods=['GET'])
@jwt_required()
def get_goal(gid):
    user_id = int(get_jwt_identity())
    g = SavingsGoal.query.filter_by(id=gid, user_id=user_id).first_or_404()
    return jsonify({'id': g.id, 'name': g.name, 'target_amount': float(g.target_amount), 'current_amount': float(g.current_amount), 'target_date': g.target_date.isoformat() if g.target_date else None, 'priority': g.priority})


@goals_bp.route('/<int:gid>', methods=['PUT'])
@jwt_required()
def update_goal(gid):
    user_id = int(get_jwt_identity())
    g = SavingsGoal.query.filter_by(id=gid, user_id=user_id).first_or_404()
    data = request.get_json() or {}
    if 'current_amount' in data:
        g.current_amount = data.get('current_amount')
    if 'priority' in data:
        g.priority = data.get('priority')
    db.session.commit()
    return jsonify({'msg': 'updated'})


@goals_bp.route('/<int:gid>', methods=['DELETE'])
@jwt_required()
def delete_goal(gid):
    user_id = int(get_jwt_identity())
    g = SavingsGoal.query.filter_by(id=gid, user_id=user_id).first_or_404()
    db.session.delete(g)
    db.session.commit()
    return jsonify({'msg': 'deleted'})
