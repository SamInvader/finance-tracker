from datetime import date, timedelta
from hashlib import sha1

from sqlalchemy import func

from ..extensions import db
from ..models import Bill, Notification, Subscription, Transaction
from ..utils.dates import month_range, month_key
from ..utils.money import from_minor
from .budgets import budget_overview
from .forecast import forecast
from .goals import list_goals


def _ensure(user_id, fingerprint, title, body, kind):
    existing = Notification.query.filter_by(user_id=user_id, fingerprint=fingerprint).first()
    if existing:
        return
    db.session.add(
        Notification(user_id=user_id, fingerprint=fingerprint, title=title, body=body, kind=kind)
    )


def refresh_notifications(user_id):
    today = date.today()
    overview = budget_overview(user_id)
    for line in overview["categories"]:
        pct = line["percent_used"]
        for threshold in (50, 80, 100):
            if pct >= threshold:
                fp = f"budget-{overview['month']}-{line['category_id']}-{threshold}"
                verb = "exceeded" if threshold >= 100 else f"reached {threshold}%"
                _ensure(
                    user_id,
                    fp,
                    f"{line['category_name']} budget {verb}",
                    f"{line['category_name']} is at {pct}% of this month's budget.",
                    "budget",
                )

    for bill in Bill.query.filter_by(user_id=user_id).all():
        status = bill.computed_status(today)
        if status in {"due_soon", "overdue"}:
            fp = f"bill-{bill.id}-{bill.due_date.isoformat()}-{status}"
            _ensure(
                user_id,
                fp,
                f"Bill {status.replace('_', ' ')}: {bill.name}",
                f"{bill.name} of ₦{from_minor(bill.amount_minor):,.2f} is {status.replace('_', ' ')} ({bill.due_date.isoformat()}).",
                "bill",
            )

    soon = today + timedelta(days=3)
    for sub in Subscription.query.filter_by(user_id=user_id, status="active").all():
        if today <= sub.next_billing_date <= soon:
            fp = f"sub-{sub.id}-{sub.next_billing_date.isoformat()}"
            _ensure(
                user_id,
                fp,
                f"{sub.name} renews soon",
                f"{sub.name} renews on {sub.next_billing_date.isoformat()} for ₦{from_minor(sub.amount_minor):,.2f}.",
                "subscription",
            )

    for goal in list_goals(user_id):
        pct = goal["percent"]
        for mark in (25, 50, 75, 100):
            if pct >= mark:
                fp = f"goal-{goal['id']}-{mark}"
                _ensure(
                    user_id,
                    fp,
                    f"{goal['name']} milestone",
                    f"{goal['name']} is {pct}% of the way to ₦{goal['target']:,.2f}.",
                    "savings",
                )

    from ..models import Debt

    for debt in Debt.query.filter_by(user_id=user_id).all():
        if debt.due_date and today <= debt.due_date <= soon and debt.remaining_minor > 0:
            fp = f"debt-{debt.id}-{debt.due_date.isoformat()}"
            _ensure(
                user_id,
                fp,
                f"{debt.name} payment approaching",
                f"Minimum payment of ₦{from_minor(debt.minimum_payment_minor):,.2f} is due {debt.due_date.isoformat()}.",
                "debt",
            )

    # unusual spending: today's expenses > 2x 30-day daily average
    start = today - timedelta(days=30)
    total = (
        db.session.query(func.coalesce(func.sum(Transaction.amount_minor), 0))
        .filter(
            Transaction.user_id == user_id,
            Transaction.type == "expense",
            Transaction.date >= start,
            Transaction.date < today,
        )
        .scalar()
    )
    avg = int(total or 0) / 30
    today_spend = (
        db.session.query(func.coalesce(func.sum(Transaction.amount_minor), 0))
        .filter(
            Transaction.user_id == user_id,
            Transaction.type == "expense",
            Transaction.date == today,
        )
        .scalar()
    )
    if avg and int(today_spend or 0) > avg * 2 and int(today_spend or 0) > 500000:
        fp = f"unusual-{today.isoformat()}"
        _ensure(
            user_id,
            fp,
            "Unusual spending detected",
            f"Today's expenses (₦{from_minor(int(today_spend)):,.2f}) are more than twice your recent daily average.",
            "alert",
        )

    proj = forecast(user_id, 30)
    if proj["lowest_projected_balance"] < 0:
        fp = f"lowbal-{today.isoformat()}"
        _ensure(
            user_id,
            fp,
            "Forecasted low balance",
            "Your 30-day cash-flow projection dips below zero based on known recurring items.",
            "forecast",
        )

    db.session.commit()


def list_notifications(user_id):
    refresh_notifications(user_id)
    items = (
        Notification.query.filter_by(user_id=user_id)
        .order_by(Notification.created_at.desc())
        .limit(100)
        .all()
    )
    unread = sum(1 for n in items if not n.is_read)
    return {"items": [n.to_dict() for n in items], "unread": unread}


def mark_read(user_id, notif_id=None, all_items=False):
    q = Notification.query.filter_by(user_id=user_id)
    if all_items:
        q.update({"is_read": True})
    elif notif_id:
        item = q.filter_by(id=notif_id).first()
        if not item:
            return None, "Notification not found"
        item.is_read = True
    db.session.commit()
    return True, None
