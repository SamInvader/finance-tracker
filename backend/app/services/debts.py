from datetime import date, timedelta
from math import ceil

from ..extensions import db
from ..models import Debt, DebtPayment
from ..utils.dates import parse_date
from ..utils.money import from_minor, to_minor


def record_payment(user_id, debt_id, data):
    debt = Debt.query.filter_by(id=debt_id, user_id=user_id).first()
    if not debt:
        return None, "Debt not found"
    amount = to_minor(data.get("amount"))
    if amount <= 0:
        return None, {"amount": "Amount must be greater than zero"}
    amount = min(amount, debt.remaining_minor)
    payment = DebtPayment(
        debt_id=debt.id,
        amount_minor=amount,
        date=parse_date(data.get("date") or date.today().isoformat()),
        note=data.get("note"),
    )
    debt.remaining_minor -= amount
    db.session.add(payment)
    db.session.commit()
    return {"debt": debt.to_dict(), "payment": payment.to_dict()}, None


def payoff_plan(user_id, method="snowball", extra_minor=0):
    debts = [d for d in Debt.query.filter_by(user_id=user_id).all() if d.remaining_minor > 0]
    if method == "avalanche":
        debts.sort(key=lambda d: (-(d.interest_rate_bps or 0), d.remaining_minor))
    else:
        debts.sort(key=lambda d: (d.remaining_minor, -(d.interest_rate_bps or 0)))
    monthly = extra_minor + sum(d.minimum_payment_minor or 0 for d in debts)
    if monthly <= 0 or not debts:
        return {
            "method": method,
            "order": [d.to_dict() for d in debts],
            "months": None,
            "total_interest_estimate": 0,
            "disclaimer": "Payoff projections are estimates and ignore fees, changing rates, and extra spending.",
        }
    # Simple month-by-month simulation using remaining balances and APR/12.
    clone = [
        {
            "id": d.id,
            "name": d.name,
            "remaining": d.remaining_minor,
            "rate": (d.interest_rate_bps or 0) / 10000 / 12,
            "min": max(d.minimum_payment_minor or 0, 1),
        }
        for d in debts
    ]
    months = 0
    interest = 0
    order_paid = []
    guard = 0
    while any(c["remaining"] > 0 for c in clone) and guard < 600:
        guard += 1
        months += 1
        extra = extra_minor
        for c in clone:
            if c["remaining"] <= 0:
                continue
            accrued = int(c["remaining"] * c["rate"])
            interest += accrued
            c["remaining"] += accrued
        # minimums first
        for c in clone:
            if c["remaining"] <= 0:
                continue
            pay = min(c["min"], c["remaining"])
            c["remaining"] -= pay
            extra_used = min(c["min"], pay)
            # leftover min unused is ignored; extra applied to first remaining in order
        # extra to first unpaid in strategy order
        for c in clone:
            if extra <= 0:
                break
            if c["remaining"] <= 0:
                continue
            pay = min(extra, c["remaining"])
            c["remaining"] -= pay
            extra -= pay
            if c["remaining"] == 0:
                order_paid.append(c["name"])
    return {
        "method": method,
        "order": [d.to_dict() for d in debts],
        "months": months if guard < 600 else None,
        "total_interest_estimate": from_minor(interest),
        "paid_off_order": order_paid,
        "disclaimer": "Payoff projections are estimates based on current balances, stated interest rates, and planned minimum payments. They are not a financial guarantee.",
    }
