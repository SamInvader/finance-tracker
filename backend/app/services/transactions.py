from datetime import date

from sqlalchemy import and_, or_

from ..extensions import db
from ..models import Account, Category, Transaction
from ..schemas.validators import ALLOWED_TX_TYPES, validate_positive_minor
from ..utils.dates import parse_date
from ..utils.money import from_minor, to_minor


def _apply_balance(tx, reverse=False):
    sign = -1 if reverse else 1
    source = Account.query.get(tx.account_id)
    if tx.type == "income":
        source.balance_minor += sign * tx.amount_minor
    elif tx.type == "expense":
        source.balance_minor -= sign * tx.amount_minor
    elif tx.type == "transfer":
        dest = Account.query.get(tx.destination_account_id)
        source.balance_minor -= sign * tx.amount_minor
        if dest:
            dest.balance_minor += sign * tx.amount_minor


def _build_transaction(user_id, data):
    errors = {}
    tx_type = (data.get("type") or "").lower()
    if tx_type not in ALLOWED_TX_TYPES:
        errors["type"] = "Type must be income, expense, or transfer"
    try:
        amount_minor = to_minor(data.get("amount"))
        errors.update(validate_positive_minor(amount_minor))
    except ValueError as exc:
        errors["amount"] = str(exc)
        amount_minor = 0
    try:
        tx_date = parse_date(data.get("date") or date.today().isoformat())
    except ValueError as exc:
        errors["date"] = str(exc)
        tx_date = date.today()
    account_id = data.get("account_id")
    account = Account.query.filter_by(id=account_id, user_id=user_id).first() if account_id else None
    if not account:
        errors["account_id"] = "Select a valid account"
    dest = None
    dest_id = data.get("destination_account_id")
    if tx_type == "transfer":
        dest = Account.query.filter_by(id=dest_id, user_id=user_id).first() if dest_id else None
        if not dest:
            errors["destination_account_id"] = "Select a destination account"
        elif dest.id == account.id if account else False:
            errors["destination_account_id"] = "Source and destination must differ"
    category_id = data.get("category_id")
    category = None
    if category_id:
        category = Category.query.filter_by(id=category_id, user_id=user_id).first()
        if not category:
            errors["category_id"] = "Invalid category"
        elif tx_type != "transfer" and category.kind != tx_type:
            errors["category_id"] = "Category does not match transaction type"
    if errors:
        return None, errors
    tags = data.get("tags") or []
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(",") if t.strip()]
    tx = Transaction(
        user_id=user_id,
        account_id=account.id,
        destination_account_id=dest.id if dest else None,
        category_id=category.id if category else None,
        type=tx_type,
        amount_minor=amount_minor,
        date=tx_date,
        description=(data.get("description") or "").strip(),
        notes=data.get("notes"),
        tags_text=",".join(tags),
        recurring_id=data.get("recurring_id"),
    )
    return tx, None


def create_transaction(user_id, data):
    tx, errors = _build_transaction(user_id, data)
    if errors:
        return None, errors
    db.session.add(tx)
    db.session.flush()
    _apply_balance(tx)
    db.session.commit()
    return tx.to_dict(include_attachments=True), None


def update_transaction(user_id, tx_id, data):
    tx = Transaction.query.filter_by(id=tx_id, user_id=user_id).first()
    if not tx:
        return None, "Transaction not found"
    _apply_balance(tx, reverse=True)
    rebuilt, errors = _build_transaction(user_id, {**tx.to_dict(), **data, "amount": data.get("amount", from_minor(tx.amount_minor))})
    if errors:
        db.session.rollback()
        return None, errors
    tx.account_id = rebuilt.account_id
    tx.destination_account_id = rebuilt.destination_account_id
    tx.category_id = rebuilt.category_id
    tx.type = rebuilt.type
    tx.amount_minor = rebuilt.amount_minor
    tx.date = rebuilt.date
    tx.description = rebuilt.description
    tx.notes = rebuilt.notes
    tx.tags_text = rebuilt.tags_text
    _apply_balance(tx)
    db.session.commit()
    return tx.to_dict(include_attachments=True), None


def delete_transaction(user_id, tx_id):
    tx = Transaction.query.filter_by(id=tx_id, user_id=user_id).first()
    if not tx:
        return None, "Transaction not found"
    _apply_balance(tx, reverse=True)
    db.session.delete(tx)
    db.session.commit()
    return True, None


def duplicate_transaction(user_id, tx_id):
    tx = Transaction.query.filter_by(id=tx_id, user_id=user_id).first()
    if not tx:
        return None, "Transaction not found"
    payload = {
        "type": tx.type,
        "amount": from_minor(tx.amount_minor),
        "account_id": tx.account_id,
        "destination_account_id": tx.destination_account_id,
        "category_id": tx.category_id,
        "date": date.today().isoformat(),
        "description": tx.description,
        "notes": tx.notes,
        "tags": tx.tag_list(),
    }
    return create_transaction(user_id, payload)


def list_transactions(user_id, args):
    q = Transaction.query.filter_by(user_id=user_id)
    if args.get("account_id"):
        q = q.filter_by(account_id=args.get("account_id"))
    if args.get("category_id"):
        q = q.filter_by(category_id=args.get("category_id"))
    if args.get("type"):
        q = q.filter_by(type=args.get("type"))
    if args.get("q"):
        like = f"%{args.get('q')}%"
        q = q.filter(
            or_(
                Transaction.description.ilike(like),
                Transaction.notes.ilike(like),
                Transaction.tags_text.ilike(like),
            )
        )
    if args.get("start"):
        q = q.filter(Transaction.date >= parse_date(args["start"], "start"))
    if args.get("end"):
        q = q.filter(Transaction.date <= parse_date(args["end"], "end"))
    if args.get("month"):
        from ..utils.dates import month_range

        start, end = month_range(args["month"])
        q = q.filter(and_(Transaction.date >= start, Transaction.date <= end))
    if args.get("min_amount"):
        q = q.filter(Transaction.amount_minor >= to_minor(args["min_amount"]))
    if args.get("max_amount"):
        q = q.filter(Transaction.amount_minor <= to_minor(args["max_amount"]))
    if args.get("tags"):
        q = q.filter(Transaction.tags_text.ilike(f"%{args['tags']}%"))
    sort = args.get("sort", "date_desc")
    if sort == "date_asc":
        q = q.order_by(Transaction.date.asc(), Transaction.id.asc())
    elif sort == "amount_desc":
        q = q.order_by(Transaction.amount_minor.desc())
    elif sort == "amount_asc":
        q = q.order_by(Transaction.amount_minor.asc())
    else:
        q = q.order_by(Transaction.date.desc(), Transaction.id.desc())
    page = max(int(args.get("page", 1)), 1)
    per_page = min(max(int(args.get("per_page", 50)), 1), 200)
    total = q.count()
    items = q.offset((page - 1) * per_page).limit(per_page).all()
    return {
        "items": [t.to_dict() for t in items],
        "total": total,
        "page": page,
        "per_page": per_page,
    }


def parse_quick_entry(text: str):
    """Deterministic parser: 'Food 3500', 'Food ₦3,500', 'Salary 150000 income'."""
    import re

    raw = (text or "").strip()
    if not raw:
        return None
    amount = None
    amount_match = re.search(r"(?:₦|NGN)?\s*([0-9]{1,3}(?:,[0-9]{3})*|[0-9]+)(?:\.[0-9]{1,2})?", raw, re.I)
    if amount_match:
        amount = amount_match.group(0)
        amount = amount.replace("₦", "").replace("NGN", "").replace(",", "").strip()
        desc = (raw[: amount_match.start()] + raw[amount_match.end() :]).strip(" -–")
    else:
        desc = raw
    tx_type = "expense"
    lowered = raw.lower()
    if any(w in lowered for w in ["salary", "allowance", "freelance", "income", "gift"]):
        tx_type = "income"
    if "transfer" in lowered or "->" in raw or "→" in raw:
        tx_type = "transfer"
    return {
        "description": desc or "Transaction",
        "amount": float(amount) if amount else None,
        "type": tx_type,
        "raw": raw,
    }
