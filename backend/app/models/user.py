import json
from datetime import datetime

from werkzeug.security import check_password_hash, generate_password_hash

from ..extensions import db
from .common import TimestampMixin


class User(db.Model, TimestampMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    is_demo = db.Column(db.Boolean, default=False, nullable=False)

    accounts = db.relationship("Account", backref="user", lazy="dynamic", cascade="all, delete-orphan")
    preference = db.relationship("UserPreference", backref="user", uselist=False, cascade="all, delete-orphan")

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password, method="pbkdf2:sha256")

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "is_demo": self.is_demo,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class UserPreference(db.Model):
    __tablename__ = "user_preferences"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    currency = db.Column(db.String(8), default="NGN", nullable=False)
    locale = db.Column(db.String(16), default="en-NG", nullable=False)
    theme = db.Column(db.String(16), default="system", nullable=False)
    default_time_range = db.Column(db.String(8), default="30d", nullable=False)
    budget_alert_thresholds = db.Column(db.String(64), default="50,80,100", nullable=False)
    dashboard_widgets = db.Column(db.Text, default="")

    def widget_list(self):
        default = [
            "summary",
            "cashflow",
            "spending",
            "budgets",
            "recent",
            "upcoming",
            "health",
        ]
        if not self.dashboard_widgets:
            return default
        try:
            data = json.loads(self.dashboard_widgets)
            if isinstance(data, list) and data:
                return data
        except json.JSONDecodeError:
            pass
        return default

    def set_widgets(self, widgets):
        self.dashboard_widgets = json.dumps(widgets)

    def thresholds(self):
        try:
            return [int(x.strip()) for x in self.budget_alert_thresholds.split(",") if x.strip()]
        except ValueError:
            return [50, 80, 100]

    def to_dict(self):
        return {
            "currency": self.currency,
            "locale": self.locale,
            "theme": self.theme,
            "default_time_range": self.default_time_range,
            "budget_alert_thresholds": self.thresholds(),
            "dashboard_widgets": self.widget_list(),
        }
