import csv
import io
import json
from datetime import date, datetime

from ..extensions import db
from ..models import (
    Account,
    Asset,
    Bill,
    Budget,
    BudgetCategory,
    Category,
    Debt,
    Liability,
    RecurringTransaction,
    SavingsGoal,
    Subscription,
    Transaction,
    UserPreference,
)
from ..utils.dates import parse_date
from ..utils.money import from_minor, to_minor
from .transactions import create_transaction


def export_csv(user_id, kind):
    output = io.StringIO()
    writer = csv.writer(output)
    if kind == "transactions":
        writer.writerow(["date", "type", "amount", "account", "category", "description", "notes", "tags"])
        for tx in Transaction.query.filter_by(user_id=user_id).order_by(Transaction.date).all():
            writer.writerow(
                [
                    tx.date.isoformat(),
                    tx.type,
                    from_minor(tx.amount_minor),
                    tx.account.name if tx.account else "",
                    tx.category.name if tx.category else "",
                    tx.description or "",
                    tx.notes or "",
                    tx.tags_text or "",
                ]
            )
    elif kind == "accounts":
        writer.writerow(["name", "type", "institution", "balance", "currency", "active"])
        for a in Account.query.filter_by(user_id=user_id).all():
            writer.writerow([a.name, a.type, a.institution or "", from_minor(a.balance_minor), a.currency, a.is_active])
    elif kind == "budgets":
        writer.writerow(["month", "category", "amount"])
        for b in Budget.query.filter_by(user_id=user_id).all():
            for line in b.categories:
                writer.writerow([b.month, line.category.name if line.category else "", from_minor(line.amount_minor)])
    elif kind == "goals":
        writer.writerow(["name", "target", "current", "deadline", "priority"])
        for g in SavingsGoal.query.filter_by(user_id=user_id).all():
            writer.writerow([g.name, from_minor(g.target_minor), from_minor(g.current_minor), g.deadline, g.priority])
    elif kind == "debts":
        writer.writerow(["name", "lender", "original", "remaining", "interest_rate", "minimum_payment"])
        for d in Debt.query.filter_by(user_id=user_id).all():
            writer.writerow(
                [
                    d.name,
                    d.lender or "",
                    from_minor(d.original_minor),
                    from_minor(d.remaining_minor),
                    (d.interest_rate_bps or 0) / 100,
                    from_minor(d.minimum_payment_minor or 0),
                ]
            )
    else:
        raise ValueError("Unsupported export type")
    return output.getvalue()


def preview_csv(user_id, text, mapping):
    reader = csv.DictReader(io.StringIO(text))
    valid = []
    invalid = []
    for i, row in enumerate(reader, start=2):
        try:
            parsed = {
                "date": parse_date(row[mapping["date"]], "date").isoformat(),
                "amount": float(str(row[mapping["amount"]]).replace(",", "").replace("₦", "")),
                "description": row.get(mapping.get("description") or "", "") if mapping.get("description") else "",
                "type": (row.get(mapping.get("type") or "") or "expense").lower()
                if mapping.get("type")
                else "expense",
            }
            if parsed["type"] not in {"income", "expense", "transfer"}:
                if parsed["amount"] < 0:
                    parsed["type"] = "expense"
                    parsed["amount"] = abs(parsed["amount"])
                else:
                    parsed["type"] = "expense"
            if mapping.get("category"):
                parsed["category_name"] = row.get(mapping["category"])
            if mapping.get("account"):
                parsed["account_name"] = row.get(mapping["account"])
            if parsed["amount"] <= 0:
                raise ValueError("Amount must be greater than zero")
            valid.append(parsed)
        except Exception as exc:
            invalid.append({"row": i, "error": str(exc), "data": row})
    return {"valid": valid[:200], "valid_count": len(valid), "invalid": invalid[:50], "invalid_count": len(invalid), "columns": reader.fieldnames}


def commit_import(user_id, rows, default_account_id):
    created = 0
    errors = []
    accounts = {a.name.lower(): a for a in Account.query.filter_by(user_id=user_id).all()}
    categories = {c.name.lower(): c for c in Category.query.filter_by(user_id=user_id).all()}
    for i, row in enumerate(rows):
        account = accounts.get((row.get("account_name") or "").lower())
        account_id = account.id if account else default_account_id
        category = categories.get((row.get("category_name") or "").lower())
        payload = {
            "type": row.get("type") or "expense",
            "amount": row.get("amount"),
            "date": row.get("date"),
            "description": row.get("description"),
            "account_id": account_id,
            "category_id": category.id if category else None,
        }
        _, err = create_transaction(user_id, payload)
        if err:
            errors.append({"row": i + 1, "error": err})
        else:
            created += 1
    return {"created": created, "errors": errors}


def full_backup(user_id):
    pref = UserPreference.query.filter_by(user_id=user_id).first()
    return {
        "version": 1,
        "exported_at": datetime.utcnow().isoformat(),
        "preferences": pref.to_dict() if pref else {},
        "accounts": [a.to_dict() for a in Account.query.filter_by(user_id=user_id).all()],
        "categories": [c.to_dict() for c in Category.query.filter_by(user_id=user_id).all()],
        "transactions": [t.to_dict() for t in Transaction.query.filter_by(user_id=user_id).all()],
        "budgets": [b.to_dict() for b in Budget.query.filter_by(user_id=user_id).all()],
        "goals": [g.to_dict() for g in SavingsGoal.query.filter_by(user_id=user_id).all()],
        "bills": [b.to_dict() for b in Bill.query.filter_by(user_id=user_id).all()],
        "subscriptions": [s.to_dict() for s in Subscription.query.filter_by(user_id=user_id).all()],
        "debts": [d.to_dict() for d in Debt.query.filter_by(user_id=user_id).all()],
        "assets": [a.to_dict() for a in Asset.query.filter_by(user_id=user_id).all()],
        "liabilities": [l.to_dict() for l in Liability.query.filter_by(user_id=user_id).all()],
        "recurring": [r.to_dict() for r in RecurringTransaction.query.filter_by(user_id=user_id).all()],
    }


def restore_backup(user_id, payload, replace=False):
    if not isinstance(payload, dict) or payload.get("version") != 1:
        return None, "Backup file is invalid or unsupported"
    required = ["accounts", "transactions", "categories"]
    for key in required:
        if key not in payload or not isinstance(payload[key], list):
            return None, f"Backup is missing '{key}'"
    if replace:
        # delete user-owned financial data
        Transaction.query.filter_by(user_id=user_id).delete()
        Budget.query.filter_by(user_id=user_id).delete()
        SavingsGoal.query.filter_by(user_id=user_id).delete()
        Bill.query.filter_by(user_id=user_id).delete()
        Subscription.query.filter_by(user_id=user_id).delete()
        Debt.query.filter_by(user_id=user_id).delete()
        RecurringTransaction.query.filter_by(user_id=user_id).delete()
        Asset.query.filter_by(user_id=user_id).delete()
        Liability.query.filter_by(user_id=user_id).delete()
        Account.query.filter_by(user_id=user_id).delete()
        Category.query.filter_by(user_id=user_id).delete()
        db.session.flush()
    cat_map = {}
    for c in payload.get("categories", []):
        obj = Category(
            user_id=user_id,
            name=c["name"],
            kind=c.get("kind") or "expense",
            icon=c.get("icon") or "circle",
            color=c.get("color") or "#64748b",
        )
        db.session.add(obj)
        db.session.flush()
        cat_map[c.get("id")] = obj.id
    acc_map = {}
    for a in payload.get("accounts", []):
        obj = Account(
            user_id=user_id,
            name=a["name"],
            type=a.get("type") or "cash",
            institution=a.get("institution"),
            balance_minor=0,
            currency=a.get("currency") or "NGN",
            notes=a.get("notes"),
            is_active=a.get("is_active", True),
        )
        db.session.add(obj)
        db.session.flush()
        acc_map[a.get("id")] = obj.id
    from .transactions import create_transaction as make_tx

    errors = []
    for t in payload.get("transactions", []):
        _, err = make_tx(
            user_id,
            {
                "type": t.get("type"),
                "amount": t.get("amount"),
                "date": t.get("date"),
                "description": t.get("description"),
                "notes": t.get("notes"),
                "tags": t.get("tags"),
                "account_id": acc_map.get(t.get("account_id")),
                "destination_account_id": acc_map.get(t.get("destination_account_id")),
                "category_id": cat_map.get(t.get("category_id")),
            },
        )
        if err:
            errors.append(err)
    db.session.commit()
    return {"restored_transactions_errors": errors[:20], "ok": True}, None
