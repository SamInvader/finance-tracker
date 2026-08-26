from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.app.extensions import db
from backend.app.models import Budget

budgets_bp = Blueprint('budgets', __name__)


@budgets_bp.route('/', methods=['GET'])
@jwt_required()
def list_budgets():
    user_id = int(get_jwt_identity())
    month = request.args.get('month')
    q = Budget.query.filter_by(user_id=user_id)
    if month:
        q = q.filter_by(month=month)
    items = q.all()
    return jsonify([{'id': b.id, 'month': b.month, 'category_id': b.category_id, 'amount': float(b.amount)} for b in items])


@budgets_bp.route('/', methods=['POST'])
@jwt_required()
def create_budget():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    month = data.get('month')
    category_id = data.get('category_id')
    amount = data.get('amount')
    if not month or not category_id or amount is None:
        return jsonify({'msg': 'month, category_id and amount required'}), 400
    b = Budget(user_id=user_id, month=month, category_id=category_id, amount=amount)
    db.session.add(b)
    db.session.commit()
    return jsonify({'id': b.id}), 201


@budgets_bp.route('/<int:bid>', methods=['GET'])
@jwt_required()
def get_budget(bid):
    user_id = int(get_jwt_identity())
    b = Budget.query.filter_by(id=bid, user_id=user_id).first_or_404()
    return jsonify({'id': b.id, 'month': b.month, 'category_id': b.category_id, 'amount': float(b.amount)})


@budgets_bp.route('/<int:bid>', methods=['PUT'])
@jwt_required()
def update_budget(bid):
    user_id = int(get_jwt_identity())
    b = Budget.query.filter_by(id=bid, user_id=user_id).first_or_404()
    data = request.get_json() or {}
    if 'amount' in data:
        b.amount = data.get('amount')
    if 'month' in data:
        b.month = data.get('month')
    db.session.commit()
    return jsonify({'msg': 'updated'})


@budgets_bp.route('/<int:bid>', methods=['DELETE'])
@jwt_required()
def delete_budget(bid):
    user_id = int(get_jwt_identity())
    b = Budget.query.filter_by(id=bid, user_id=user_id).first_or_404()
    db.session.delete(b)
    db.session.commit()
    return jsonify({'msg': 'deleted'})
