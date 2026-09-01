from datetime import date, timedelta

from ..extensions import db
from ..models import RecurringTransaction, Transaction
from ..utils.dates import add_months, parse_date
from ..utils.money import to_minor
from .transactions import create_transaction


def next_date(current: date, frequency: str, interval: int = 1) -> date:
    interval = max(int(interval or 1), 1)
    if frequency == "daily":
        return current + timedelta(days=interval)
    if frequency == "weekly":
        return current + timedelta(weeks=interval)
    if frequency == "yearly":
        try:
            return date(current.year + interval, current.month, current.day)
        except ValueError:
            return date(current.year + interval, current.month, 28)
    # monthly and custom default to months
    return add_months(current, interval)


def process_due(user_id, today=None):
    today = today or date.today()
    created = []
    items = RecurringTransaction.query.filter(
        RecurringTransaction.user_id == user_id,
        RecurringTransaction.is_active.is_(True),
        RecurringTransaction.next_occurrence <= today,
    ).all()
    for item in items:
        cursor = item.next_occurrence
        while cursor and cursor <= today:
            if item.end_date and cursor > item.end_date:
                item.is_active = False
                break
            exists = Transaction.query.filter_by(
                user_id=user_id, recurring_id=item.id, date=cursor
            ).first()
            if not exists:
                from ..utils.money import from_minor

                payload = {
                    "type": item.type,
                    "amount": from_minor(item.amount_minor),
                    "account_id": item.account_id,
                    "category_id": item.category_id,
                    "date": cursor.isoformat(),
                    "description": item.description,
                    "recurring_id": item.id,
                }
                tx, err = create_transaction(user_id, payload)
                if not err:
                    created.append(tx)
            item.last_generated = cursor
            nxt = next_date(cursor, item.frequency, item.interval)
            if nxt <= cursor:
                break
            cursor = nxt
            if item.end_date and cursor > item.end_date:
                item.is_active = False
                item.next_occurrence = cursor
                break
            item.next_occurrence = cursor
    db.session.commit()
    return created


def create_recurring(user_id, data):
    from ..models import Account

    if not data.get("account_id") or not Account.query.filter_by(id=data["account_id"], user_id=user_id).first():
        return None, {"account_id": "Select a valid account"}
    start = parse_date(data.get("start_date") or date.today().isoformat(), "start_date")
    rec = RecurringTransaction(
        user_id=user_id,
        account_id=data["account_id"],
        category_id=data.get("category_id"),
        type=data.get("type") or "expense",
        amount_minor=to_minor(data.get("amount")),
        description=data.get("description"),
        frequency=data.get("frequency") or "monthly",
        interval=int(data.get("interval") or 1),
        start_date=start,
        end_date=parse_date(data["end_date"], "end_date") if data.get("end_date") else None,
        next_occurrence=start,
        is_active=True,
    )
    db.session.add(rec)
    db.session.commit()
    process_due(user_id)
    return rec.to_dict(), None
