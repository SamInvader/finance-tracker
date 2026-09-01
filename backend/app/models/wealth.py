from datetime import date

from ..extensions import db
from ..utils.money import from_minor
from .common import TimestampMixin, UserOwnedMixin


class Debt(db.Model, TimestampMixin, UserOwnedMixin):
    __tablename__ = "debts"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    lender = db.Column(db.String(120))
    original_minor = db.Column(db.Integer, nullable=False)
    remaining_minor = db.Column(db.Integer, nullable=False)
    interest_rate_bps = db.Column(db.Integer, default=0)  # 1250 = 12.50%
    minimum_payment_minor = db.Column(db.Integer, default=0)
    payment_frequency = db.Column(db.String(16), default="monthly")
    due_date = db.Column(db.Date, nullable=True)
    notes = db.Column(db.Text)

    payments = db.relationship("DebtPayment", backref="debt", cascade="all, delete-orphan")

    def to_dict(self):
        paid = self.original_minor - self.remaining_minor
        pct = 0
        if self.original_minor > 0:
            pct = round(max(paid, 0) * 10000 / self.original_minor) / 100
        return {
            "id": self.id,
            "name": self.name,
            "lender": self.lender,
            "original": from_minor(self.original_minor),
            "remaining": from_minor(self.remaining_minor),
            "paid": from_minor(max(paid, 0)),
            "percent": min(max(pct, 0), 100),
            "interest_rate": (self.interest_rate_bps or 0) / 100,
            "minimum_payment": from_minor(self.minimum_payment_minor or 0),
            "payment_frequency": self.payment_frequency,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "notes": self.notes,
        }


class DebtPayment(db.Model, TimestampMixin):
    __tablename__ = "debt_payments"

    id = db.Column(db.Integer, primary_key=True)
    debt_id = db.Column(db.Integer, db.ForeignKey("debts.id"), nullable=False)
    amount_minor = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Date, nullable=False)
    note = db.Column(db.String(255))

    def to_dict(self):
        return {
            "id": self.id,
            "amount": from_minor(self.amount_minor),
            "date": self.date.isoformat(),
            "note": self.note,
        }


class Asset(db.Model, TimestampMixin, UserOwnedMixin):
    __tablename__ = "assets"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    kind = db.Column(db.String(32), default="other")  # cash bank savings investment other
    value_minor = db.Column(db.Integer, default=0, nullable=False)
    notes = db.Column(db.Text)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "kind": self.kind,
            "value": from_minor(self.value_minor),
            "notes": self.notes,
        }


class Liability(db.Model, TimestampMixin, UserOwnedMixin):
    __tablename__ = "liabilities"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    kind = db.Column(db.String(32), default="other")
    value_minor = db.Column(db.Integer, default=0, nullable=False)
    notes = db.Column(db.Text)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "kind": self.kind,
            "value": from_minor(self.value_minor),
            "notes": self.notes,
        }


class NetWorthSnapshot(db.Model, UserOwnedMixin):
    __tablename__ = "net_worth_snapshots"

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, index=True)
    assets_minor = db.Column(db.Integer, nullable=False)
    liabilities_minor = db.Column(db.Integer, nullable=False)
    net_worth_minor = db.Column(db.Integer, nullable=False)

    __table_args__ = (db.UniqueConstraint("user_id", "date", name="uq_nw_user_date"),)

    def to_dict(self):
        return {
            "date": self.date.isoformat(),
            "assets": from_minor(self.assets_minor),
            "liabilities": from_minor(self.liabilities_minor),
            "net_worth": from_minor(self.net_worth_minor),
        }


class Notification(db.Model, TimestampMixin, UserOwnedMixin):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=False)
    kind = db.Column(db.String(32), default="info")
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    fingerprint = db.Column(db.String(80), index=True)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "body": self.body,
            "kind": self.kind,
            "is_read": self.is_read,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
