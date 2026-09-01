from datetime import date, timedelta

from ..models import (
    Account,
    Bill,
    Category,
    Debt,
    RecurringTransaction,
    SavingsGoal,
    Subscription,
    Transaction,
)
from .recurring import next_date


def global_search(user_id, q):
    q = (q or "").strip()
    if len(q) < 2:
        return {"transactions": [], "categories": [], "accounts": [], "bills": [], "subscriptions": [], "goals": [], "debts": []}
    like = f"%{q}%"
    txs = (
        Transaction.query.filter_by(user_id=user_id)
        .filter(Transaction.description.ilike(like))
        .order_by(Transaction.date.desc())
        .limit(10)
        .all()
    )
    return {
        "transactions": [t.to_dict() for t in txs],
        "categories": [c.to_dict() for c in Category.query.filter_by(user_id=user_id).filter(Category.name.ilike(like)).limit(10)],
        "accounts": [a.to_dict() for a in Account.query.filter_by(user_id=user_id).filter(Account.name.ilike(like)).limit(10)],
        "bills": [b.to_dict() for b in Bill.query.filter_by(user_id=user_id).filter(Bill.name.ilike(like)).limit(10)],
        "subscriptions": [s.to_dict() for s in Subscription.query.filter_by(user_id=user_id).filter(Subscription.name.ilike(like)).limit(10)],
        "goals": [g.to_dict() for g in SavingsGoal.query.filter_by(user_id=user_id).filter(SavingsGoal.name.ilike(like)).limit(10)],
        "debts": [d.to_dict() for d in Debt.query.filter_by(user_id=user_id).filter(Debt.name.ilike(like)).limit(10)],
    }


def calendar_events(user_id, year, month):
    start = date(int(year), int(month), 1)
    end = (date(int(year) + (1 if month == 12 else 0), 1 if month == 12 else int(month) + 1, 1)) - timedelta(days=1)
    events = []
    for bill in Bill.query.filter_by(user_id=user_id).all():
        if start <= bill.due_date <= end:
            events.append({"date": bill.due_date.isoformat(), "title": bill.name, "kind": "bill", "id": bill.id, "amount": bill.to_dict()["amount"]})
    for sub in Subscription.query.filter_by(user_id=user_id, status="active").all():
        if start <= sub.next_billing_date <= end:
            events.append({"date": sub.next_billing_date.isoformat(), "title": sub.name, "kind": "subscription", "id": sub.id, "amount": sub.to_dict()["amount"]})
    for rec in RecurringTransaction.query.filter_by(user_id=user_id, is_active=True).all():
        cursor = rec.next_occurrence
        guard = 0
        # walk back to month start
        probe = rec.start_date
        while probe < start and guard < 400:
            guard += 1
            nxt = next_date(probe, rec.frequency, rec.interval)
            if nxt <= probe:
                break
            probe = nxt
        cursor = probe
        guard = 0
        while cursor and cursor <= end and guard < 80:
            if cursor >= start:
                events.append(
                    {
                        "date": cursor.isoformat(),
                        "title": rec.description or "Recurring",
                        "kind": rec.type,
                        "id": rec.id,
                        "amount": rec.to_dict()["amount"],
                    }
                )
            nxt = next_date(cursor, rec.frequency, rec.interval)
            if nxt <= cursor:
                break
            cursor = nxt
            guard += 1
    for debt in Debt.query.filter_by(user_id=user_id).all():
        if debt.due_date and start <= debt.due_date <= end:
            events.append({"date": debt.due_date.isoformat(), "title": f"{debt.name} payment", "kind": "debt", "id": debt.id, "amount": debt.to_dict()["minimum_payment"]})
    events.sort(key=lambda e: e["date"])
    return events
