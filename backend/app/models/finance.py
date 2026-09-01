from ..extensions import db
from ..utils.money import from_minor
from .common import TimestampMixin, UserOwnedMixin


class Account(db.Model, TimestampMixin, UserOwnedMixin):
    __tablename__ = "accounts"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    type = db.Column(db.String(32), default="cash", nullable=False)
    institution = db.Column(db.String(120))
    balance_minor = db.Column(db.Integer, default=0, nullable=False)
    currency = db.Column(db.String(8), default="NGN", nullable=False)
    notes = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "institution": self.institution,
            "balance": from_minor(self.balance_minor),
            "balance_minor": self.balance_minor,
            "currency": self.currency,
            "notes": self.notes,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Category(db.Model, TimestampMixin):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    kind = db.Column(db.String(16), nullable=False)  # income | expense
    icon = db.Column(db.String(64), default="circle")
    color = db.Column(db.String(16), default="#0f766e")
    parent_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=True)

    parent = db.relationship("Category", remote_side="Category.id", backref="children")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "kind": self.kind,
            "icon": self.icon,
            "color": self.color,
            "parent_id": self.parent_id,
        }


class Tag(db.Model, UserOwnedMixin):
    __tablename__ = "tags"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)

    __table_args__ = (db.UniqueConstraint("user_id", "name", name="uq_tag_user_name"),)

    def to_dict(self):
        return {"id": self.id, "name": self.name}


class Transaction(db.Model, TimestampMixin, UserOwnedMixin):
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey("accounts.id"), nullable=False, index=True)
    destination_account_id = db.Column(db.Integer, db.ForeignKey("accounts.id"), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=True)
    type = db.Column(db.String(16), nullable=False)  # income | expense | transfer
    amount_minor = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Date, nullable=False, index=True)
    description = db.Column(db.String(500))
    notes = db.Column(db.Text)
    recurring_id = db.Column(db.Integer, db.ForeignKey("recurring_transactions.id"), nullable=True)
    tags_text = db.Column(db.String(500), default="")

    account = db.relationship("Account", foreign_keys=[account_id])
    destination_account = db.relationship("Account", foreign_keys=[destination_account_id])
    category = db.relationship("Category")
    attachments = db.relationship("Attachment", backref="transaction", cascade="all, delete-orphan")

    __table_args__ = (
        db.Index("ix_tx_user_date", "user_id", "date"),
        db.Index("ix_tx_user_type", "user_id", "type"),
    )

    def tag_list(self):
        if not self.tags_text:
            return []
        return [t.strip() for t in self.tags_text.split(",") if t.strip()]

    def to_dict(self, include_attachments=False):
        payload = {
            "id": self.id,
            "account_id": self.account_id,
            "destination_account_id": self.destination_account_id,
            "account_name": self.account.name if self.account else None,
            "destination_account_name": self.destination_account.name
            if self.destination_account
            else None,
            "category_id": self.category_id,
            "category_name": self.category.name if self.category else None,
            "category_color": self.category.color if self.category else None,
            "type": self.type,
            "amount": from_minor(self.amount_minor),
            "amount_minor": self.amount_minor,
            "date": self.date.isoformat() if self.date else None,
            "description": self.description,
            "notes": self.notes,
            "tags": self.tag_list(),
            "recurring_id": self.recurring_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_attachments:
            payload["attachments"] = [a.to_dict() for a in self.attachments]
        else:
            payload["attachment_count"] = len(self.attachments) if self.attachments else 0
        return payload


class Attachment(db.Model, TimestampMixin):
    __tablename__ = "attachments"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey("transactions.id"), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    stored_name = db.Column(db.String(255), nullable=False)
    mime_type = db.Column(db.String(120), nullable=False)
    size_bytes = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "mime_type": self.mime_type,
            "size_bytes": self.size_bytes,
            "url": f"/api/attachments/{self.id}",
        }
