from ..extensions import db
from ..models import Account
from ..schemas.validators import ALLOWED_ACCOUNT_TYPES, require_fields
from ..utils.money import parse_optional_amount, to_minor


def list_accounts(user_id, include_inactive=False):
    q = Account.query.filter_by(user_id=user_id)
    if not include_inactive:
        q = q.filter_by(is_active=True)
    accounts = q.order_by(Account.name).all()
    total = sum(a.balance_minor for a in accounts if a.type != "credit")
    credit = sum(a.balance_minor for a in accounts if a.type == "credit")
    from ..utils.money import from_minor

    return {
        "accounts": [a.to_dict() for a in accounts],
        "combined_balance": from_minor(total),
        "credit_balances": from_minor(credit),
    }


def create_account(user_id, data):
    errors = require_fields(data, ["name", "type"])
    acc_type = (data.get("type") or "").lower()
    if acc_type not in ALLOWED_ACCOUNT_TYPES:
        errors["type"] = "Invalid account type"
    if errors:
        return None, errors
    try:
        opening = to_minor(data.get("balance", 0) or 0)
    except ValueError as exc:
        return None, {"balance": str(exc)}
    account = Account(
        user_id=user_id,
        name=data["name"].strip(),
        type=acc_type,
        institution=(data.get("institution") or "").strip(),
        balance_minor=opening,
        currency=(data.get("currency") or "NGN").upper(),
        notes=data.get("notes"),
        is_active=bool(data.get("is_active", True)),
    )
    db.session.add(account)
    db.session.commit()
    return account.to_dict(), None


def update_account(user_id, account_id, data):
    account = Account.query.filter_by(id=account_id, user_id=user_id).first()
    if not account:
        return None, "Account not found"
    if "name" in data and data["name"]:
        account.name = data["name"].strip()
    if "type" in data:
        if data["type"] not in ALLOWED_ACCOUNT_TYPES:
            return None, "Invalid account type"
        account.type = data["type"]
    if "institution" in data:
        account.institution = data.get("institution") or ""
    if "notes" in data:
        account.notes = data.get("notes")
    if "currency" in data and data["currency"]:
        account.currency = data["currency"].upper()
    if "is_active" in data:
        account.is_active = bool(data["is_active"])
    if "balance" in data and data["balance"] is not None:
        try:
            account.balance_minor = to_minor(data["balance"])
        except ValueError as exc:
            return None, str(exc)
    db.session.commit()
    return account.to_dict(), None


def get_owned_account(user_id, account_id):
    return Account.query.filter_by(id=account_id, user_id=user_id).first()
