from datetime import date, timedelta

from ..models import Account, Bill, Debt, RecurringTransaction, Subscription
from ..utils.dates import add_months
from ..utils.money import from_minor
from .recurring import next_date


def forecast(user_id, days=30):
    days = int(days)
    start = date.today()
    end = start + timedelta(days=days)
    accounts = Account.query.filter_by(user_id=user_id, is_active=True).all()
    opening = sum(a.balance_minor for a in accounts if a.type != "credit")
    events = []

    for rec in RecurringTransaction.query.filter_by(user_id=user_id, is_active=True).all():
        cursor = rec.next_occurrence
        guard = 0
        while cursor and cursor <= end and guard < 400:
            guard += 1
            if cursor >= start:
                sign = 1 if rec.type == "income" else -1
                if rec.type == "transfer":
                    sign = 0
                events.append(
                    {
                        "date": cursor,
                        "amount_minor": sign * rec.amount_minor,
                        "label": rec.description or "Recurring",
                        "kind": rec.type,
                    }
                )
            nxt = next_date(cursor, rec.frequency, rec.interval)
            if nxt <= cursor:
                break
            cursor = nxt
            if rec.end_date and cursor > rec.end_date:
                break

    for bill in Bill.query.filter_by(user_id=user_id).all():
        if bill.due_date >= start and bill.due_date <= end and bill.computed_status() != "paid":
            events.append(
                {
                    "date": bill.due_date,
                    "amount_minor": -bill.amount_minor,
                    "label": bill.name,
                    "kind": "bill",
                }
            )

    for sub in Subscription.query.filter_by(user_id=user_id, status="active").all():
        cursor = sub.next_billing_date
        freq = "yearly" if sub.billing_cycle == "yearly" else "weekly" if sub.billing_cycle == "weekly" else "monthly"
        guard = 0
        while cursor <= end and guard < 40:
            guard += 1
            if cursor >= start:
                events.append(
                    {
                        "date": cursor,
                        "amount_minor": -sub.amount_minor,
                        "label": sub.name,
                        "kind": "subscription",
                    }
                )
            cursor = next_date(cursor, freq, 1)

    for debt in Debt.query.filter_by(user_id=user_id).all():
        if debt.due_date and start <= debt.due_date <= end and debt.remaining_minor > 0:
            events.append(
                {
                    "date": debt.due_date,
                    "amount_minor": -(debt.minimum_payment_minor or 0),
                    "label": f"{debt.name} payment",
                    "kind": "debt",
                }
            )

    events.sort(key=lambda e: e["date"])
    running = opening
    series = []
    by_day = {}
    for ev in events:
        running += ev["amount_minor"]
        key = ev["date"].isoformat()
        by_day.setdefault(key, {"inflow": 0, "outflow": 0, "balance": running, "events": []})
        if ev["amount_minor"] >= 0:
            by_day[key]["inflow"] += ev["amount_minor"]
        else:
            by_day[key]["outflow"] += -ev["amount_minor"]
        by_day[key]["balance"] = running
        by_day[key]["events"].append(
            {
                "label": ev["label"],
                "kind": ev["kind"],
                "amount": from_minor(abs(ev["amount_minor"])),
                "direction": "in" if ev["amount_minor"] >= 0 else "out",
            }
        )
    cursor = start
    last_balance = opening
    while cursor <= end:
        key = cursor.isoformat()
        if key in by_day:
            last_balance = by_day[key]["balance"]
            series.append(
                {
                    "date": key,
                    "balance": from_minor(last_balance),
                    "inflow": from_minor(by_day[key]["inflow"]),
                    "outflow": from_minor(by_day[key]["outflow"]),
                    "events": by_day[key]["events"],
                }
            )
        else:
            series.append({"date": key, "balance": from_minor(last_balance), "inflow": 0, "outflow": 0, "events": []})
        cursor += timedelta(days=1)

    min_balance = min((p["balance"] for p in series), default=from_minor(opening))
    return {
        "days": days,
        "opening_balance": from_minor(opening),
        "projected_end_balance": series[-1]["balance"] if series else from_minor(opening),
        "lowest_projected_balance": min_balance,
        "series": series,
        "disclaimer": "This is a projection from current balances and known recurring items. It does not predict unexpected spending.",
    }
