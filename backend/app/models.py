from .extensions import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    accounts = db.relationship('Account', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    type = db.Column(db.String(50), default='cash')
    balance = db.Column(db.Numeric(14, 2), default=0.0)
    currency = db.Column(db.String(8), default='NGN')
    institution = db.Column(db.String(120))
    notes = db.Column(db.Text)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    transactions = db.relationship('Transaction', backref='account', lazy=True)


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    name = db.Column(db.String(120), nullable=False)
    type = db.Column(db.String(10), nullable=False)  # 'income' or 'expense'
    color = db.Column(db.String(20))
    icon = db.Column(db.String(120))


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
    amount = db.Column(db.Numeric(14, 2), nullable=False)
    type = db.Column(db.String(10), nullable=False)  # income, expense, transfer
    date = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.String(500))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    month = db.Column(db.String(7), nullable=False)  # YYYY-MM
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    amount = db.Column(db.Numeric(14,2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class SavingsGoal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    target_amount = db.Column(db.Numeric(14,2), nullable=False)
    current_amount = db.Column(db.Numeric(14,2), default=0.0)
    target_date = db.Column(db.Date)
    priority = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
