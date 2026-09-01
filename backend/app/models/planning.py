from datetime import date

from ..extensions import db
from ..utils.money import from_minor
from .common import TimestampMixin, UserOwnedMixin


class Budget(db.Model, TimestampMixin, UserOwnedMixin):
    __tablename__ = "budgets"

    id = db.Column(db.Integer, primary_key=True)
    month = db.Column(db.String(7), nullable=False, index=True)  # YYYY-MM
    overall_limit_minor = db.Column(db.Integer, default=0, nullable=False)
    carry_forward = db.Column(db.Boolean, default=False, nullable=False)

    categories = db.relationship("BudgetCategory", backref="budget", cascade="all, delete-orphan")

    __table_args__ = (db.UniqueConstraint("user_id", "month", name="uq_budget_user_month"),)

    def to_dict(self):
        return {
            "id": self.id,
            "month": self.month,
            "overall_limit": from_minor(self.overall_limit_minor),
            "carry_forward": self.carry_forward,
            "categories": [c.to_dict() for c in self.categories],
        }


class BudgetCategory(db.Model):
    __tablename__ = "budget_categories"

    id = db.Column(db.Integer, primary_key=True)
    budget_id = db.Column(db.Integer, db.ForeignKey("budgets.id"), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)
    amount_minor = db.Column(db.Integer, nullable=False)
    alert_50 = db.Column(db.Boolean, default=True)
    alert_80 = db.Column(db.Boolean, default=True)
    alert_100 = db.Column(db.Boolean, default=True)

    category = db.relationship("Category")

    def to_dict(self):
        return {
            "id": self.id,
            "category_id": self.category_id,
            "category_name": self.category.name if self.category else None,
            "category_color": self.category.color if self.category else None,
            "amount": from_minor(self.amount_minor),
            "amount_minor": self.amount_minor,
        }


class SavingsGoal(db.Model, TimestampMixin, UserOwnedMixin):
    __tablename__ = "savings_goals"

    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey("accounts.id"), nullable=True)
    name = db.Column(db.String(120), nullable=False)
    target_minor = db.Column(db.Integer, nullable=False)
    current_minor = db.Column(db.Integer, default=0, nullable=False)
    deadline = db.Column(db.Date, nullable=True)
    description = db.Column(db.Text)
    icon = db.Column(db.String(64), default="piggy-bank")
    priority = db.Column(db.Integer, default=3)

    account = db.relationship("Account")
    contributions = db.relationship(
        "SavingsContribution", backref="goal", cascade="all, delete-orphan", order_by="SavingsContribution.date.desc()"
    )

    def to_dict(self):
        remaining = max(self.target_minor - self.current_minor, 0)
        pct = 0
        if self.target_minor > 0:
            pct = round(self.current_minor * 10000 / self.target_minor) / 100
        required_monthly = None
        required_weekly = None
        eta = None
        today = date.today()
        if self.deadline and remaining > 0:
            days = max((self.deadline - today).days, 1)
            required_weekly = remaining / max(days / 7, 1)
            required_monthly = remaining / max(days / 30, 1)
        return {
            "id": self.id,
            "account_id": self.account_id,
            "account_name": self.account.name if self.account else None,
            "name": self.name,
            "target": from_minor(self.target_minor),
            "current": from_minor(self.current_minor),
            "remaining": from_minor(remaining),
            "percent": min(pct, 100),
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "description": self.description,
            "icon": self.icon,
            "priority": self.priority,
            "required_monthly": from_minor(int(required_monthly)) if required_monthly else None,
            "required_weekly": from_minor(int(required_weekly)) if required_weekly else None,
            "estimated_completion": eta,
        }


class SavingsContribution(db.Model, TimestampMixin):
    __tablename__ = "savings_contributions"

    id = db.Column(db.Integer, primary_key=True)
    goal_id = db.Column(db.Integer, db.ForeignKey("savings_goals.id"), nullable=False)
    amount_minor = db.Column(db.Integer, nullable=False)  # positive deposit, negative withdrawal
    date = db.Column(db.Date, nullable=False)
    note = db.Column(db.String(255))

    def to_dict(self):
        return {
            "id": self.id,
            "amount": from_minor(self.amount_minor),
            "date": self.date.isoformat(),
            "note": self.note,
            "kind": "deposit" if self.amount_minor >= 0 else "withdrawal",
        }


class RecurringTransaction(db.Model, TimestampMixin, UserOwnedMixin):
    __tablename__ = "recurring_transactions"

    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey("accounts.id"), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=True)
    type = db.Column(db.String(16), nullable=False)
    amount_minor = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(255))
    frequency = db.Column(db.String(16), nullable=False)  # daily weekly monthly yearly custom
    interval = db.Column(db.Integer, default=1, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=True)
    next_occurrence = db.Column(db.Date, nullable=False, index=True)
    last_generated = db.Column(db.Date, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    account = db.relationship("Account")
    category = db.relationship("Category")

    def to_dict(self):
        return {
            "id": self.id,
            "account_id": self.account_id,
            "account_name": self.account.name if self.account else None,
            "category_id": self.category_id,
            "category_name": self.category.name if self.category else None,
            "type": self.type,
            "amount": from_minor(self.amount_minor),
            "description": self.description,
            "frequency": self.frequency,
            "interval": self.interval,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "next_occurrence": self.next_occurrence.isoformat() if self.next_occurrence else None,
            "last_generated": self.last_generated.isoformat() if self.last_generated else None,
            "is_active": self.is_active,
        }


class Bill(db.Model, TimestampMixin, UserOwnedMixin):
    __tablename__ = "bills"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    amount_minor = db.Column(db.Integer, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    frequency = db.Column(db.String(16), default="monthly")
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=True)
    account_id = db.Column(db.Integer, db.ForeignKey("accounts.id"), nullable=True)
    status = db.Column(db.String(16), default="upcoming")
    last_paid = db.Column(db.Date, nullable=True)

    category = db.relationship("Category")
    account = db.relationship("Account")

    def computed_status(self, today=None):
        today = today or date.today()
        if self.status == "paid" and self.last_paid and self.last_paid >= self.due_date:
            return "paid"
        days = (self.due_date - today).days
        if days < 0:
            return "overdue"
        if days <= 3:
            return "due_soon"
        return "upcoming"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "amount": from_minor(self.amount_minor),
            "due_date": self.due_date.isoformat(),
            "frequency": self.frequency,
            "category_id": self.category_id,
            "account_id": self.account_id,
            "status": self.computed_status(),
            "stored_status": self.status,
            "last_paid": self.last_paid.isoformat() if self.last_paid else None,
        }


class Subscription(db.Model, TimestampMixin, UserOwnedMixin):
    __tablename__ = "subscriptions"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    amount_minor = db.Column(db.Integer, nullable=False)
    billing_cycle = db.Column(db.String(16), default="monthly")  # weekly monthly yearly
    next_billing_date = db.Column(db.Date, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=True)
    account_id = db.Column(db.Integer, db.ForeignKey("accounts.id"), nullable=True)
    status = db.Column(db.String(16), default="active")  # active cancelled paused

    category = db.relationship("Category")
    account = db.relationship("Account")

    def monthly_minor(self):
        if self.billing_cycle == "weekly":
            return int(self.amount_minor * 52 / 12)
        if self.billing_cycle == "yearly":
            return int(self.amount_minor / 12)
        return self.amount_minor

    def annual_minor(self):
        return self.monthly_minor() * 12

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "amount": from_minor(self.amount_minor),
            "billing_cycle": self.billing_cycle,
            "next_billing_date": self.next_billing_date.isoformat(),
            "category_id": self.category_id,
            "account_id": self.account_id,
            "status": self.status,
            "monthly_cost": from_minor(self.monthly_minor()),
            "annual_cost": from_minor(self.annual_minor()),
        }
