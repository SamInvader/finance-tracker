from datetime import date, timedelta

from ..models import Account, Bill, Debt, RecurringTransaction, Subscription, Transaction
from ..utils.dates import month_key
from ..utils.money import from_minor
from .analytics import cashflow_series, month_summary, spending_by_category
from .budgets import budget_overview
from .health import financial_health
from .networth import compute_net_worth


def dashboard(user_id, period="30d"):
    accounts = Account.query.filter_by(user_id=user_id, is_active=True).all()
    total_balance = sum(a.balance_minor for a in accounts if a.type != "credit")
    month = month_summary(user_id)
    overview = budget_overview(user_id)
    recent = (
        Transaction.query.filter_by(user_id=user_id)
        .order_by(Transaction.date.desc(), Transaction.id.desc())
        .limit(8)
        .all()
    )
    upcoming = []
    today = date.today()
    horizon = today + timedelta(days=14)
    for bill in Bill.query.filter_by(user_id=user_id).all():
        if today <= bill.due_date <= horizon:
            upcoming.append({"kind": "bill", "title": bill.name, "date": bill.due_date.isoformat(), "amount": from_minor(bill.amount_minor)})
    for rec in RecurringTransaction.query.filter_by(user_id=user_id, is_active=True).all():
        if rec.next_occurrence and today <= rec.next_occurrence <= horizon:
            upcoming.append({"kind": rec.type, "title": rec.description or "Recurring", "date": rec.next_occurrence.isoformat(), "amount": from_minor(rec.amount_minor)})
    for sub in Subscription.query.filter_by(user_id=user_id, status="active").all():
        if today <= sub.next_billing_date <= horizon:
            upcoming.append({"kind": "subscription", "title": sub.name, "date": sub.next_billing_date.isoformat(), "amount": from_minor(sub.amount_minor)})
    for debt in Debt.query.filter_by(user_id=user_id).all():
        if debt.due_date and today <= debt.due_date <= horizon:
            upcoming.append({"kind": "debt", "title": f"{debt.name} payment", "date": debt.due_date.isoformat(), "amount": from_minor(debt.minimum_payment_minor or 0)})
    upcoming.sort(key=lambda x: x["date"])
    savings = sum(a.balance_minor for a in accounts if a.type == "savings")
    start = date.today().replace(day=1)
    from datetime import date as d

    from .analytics import spending_by_category as sbc
    from ..utils.dates import month_range

    s, e = month_range(month_key(date.today()))
    return {
        "summary": {
            "total_balance": from_minor(total_balance),
            "income_this_month": month["income"],
            "expenses_this_month": month["expense"],
            "net_cashflow": month["net"],
            "total_savings": from_minor(savings),
            "remaining_budget": overview["remaining"],
        },
        "accounts": [a.to_dict() for a in accounts],
        "cashflow": cashflow_series(user_id, period),
        "spending": sbc(user_id, s, e),
        "budgets": overview,
        "recent": [t.to_dict() for t in recent],
        "upcoming": upcoming[:12],
        "health": financial_health(user_id),
        "net_worth": compute_net_worth(user_id, persist=False)["current"],
        "period": period,
    }
