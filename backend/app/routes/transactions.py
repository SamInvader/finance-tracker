from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.app.extensions import db
from backend.app.models import Transaction, Account

tx_bp = Blueprint('transactions', __name__)


@tx_bp.route('/', methods=['GET'])
@jwt_required()
def list_transactions():
    user_id = int(get_jwt_identity())
    txs = Transaction.query.filter_by(user_id=user_id).order_by(Transaction.date.desc()).all()
    result = []
    for t in txs:
        result.append({
            'id': t.id,
            'amount': float(t.amount),
            'type': t.type,
            'date': t.date.isoformat(),
            'description': t.description,
            'account_id': t.account_id,
            'category_id': t.category_id,
        })
    return jsonify(result)


@tx_bp.route('/', methods=['POST'])
@jwt_required()
def create_transaction():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    account_id = data.get('account_id')
    try:
        account = Account.query.filter_by(id=account_id, user_id=user_id).first()
    except Exception:
        account = None
    if not account:
        return jsonify({'msg': 'account not found or not owned by user'}), 404
    t = Transaction(
        user_id=user_id,
        account_id=account_id,
        category_id=data.get('category_id'),
        amount=data.get('amount', 0),
        type=data.get('type', 'expense'),
        description=data.get('description'),
    )
    db.session.add(t)
    db.session.commit()
    return jsonify({'id': t.id}), 201


@tx_bp.route('/<int:tx_id>', methods=['GET'])
@jwt_required()
def get_transaction(tx_id):
    user_id = int(get_jwt_identity())
    t = Transaction.query.filter_by(id=tx_id, user_id=user_id).first_or_404()
    return jsonify({'id': t.id, 'amount': float(t.amount), 'type': t.type, 'date': t.date.isoformat(), 'description': t.description})


@tx_bp.route('/<int:tx_id>', methods=['PUT'])
@jwt_required()
def update_transaction(tx_id):
    user_id = int(get_jwt_identity())
    t = Transaction.query.filter_by(id=tx_id, user_id=user_id).first_or_404()
    data = request.get_json() or {}
    if 'amount' in data:
        t.amount = data.get('amount')
    if 'description' in data:
        t.description = data.get('description')
    db.session.commit()
    return jsonify({'msg': 'updated'})


@tx_bp.route('/<int:tx_id>', methods=['DELETE'])
@jwt_required()
def delete_transaction(tx_id):
    user_id = int(get_jwt_identity())
    t = Transaction.query.filter_by(id=tx_id, user_id=user_id).first_or_404()
    db.session.delete(t)
    db.session.commit()
    return jsonify({'msg': 'deleted'})
