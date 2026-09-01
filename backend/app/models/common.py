from datetime import datetime

from sqlalchemy.ext.declarative import declared_attr

from ..extensions import db


class TimestampMixin:
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


class UserOwnedMixin:
    @declared_attr
    def user_id(cls):
        return db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
