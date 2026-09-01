from collections import defaultdict
from datetime import date, timedelta

from sqlalchemy import func

from ..extensions import db
from ..models import Account, Category, Transaction
from ..utils.dates import month_key, month_range, period_days
from ..utils.money import from_minor


def _sum(user_id, tx_type, start, end):
    value = (
        db.session.query(func.coalesce(func.sum(Transaction.amount_minor), 0))
        .filter(
            Transaction.user_id == user_id,
            Transaction.type == tx_type,
            Transaction.date >= start,
            Transaction.date <= end,
        )
        .scalar()
    )
    return int(value or 0)


def cashflow_series(user_id, period="30d"):
    days = period_days(period)
    end = date.today()
    start = end - timedelta(days=days - 1)
    rows = (
        db.session.query(Transaction.date, Transaction.type, func.sum(Transaction.amount_minor))
        .filter(
            Transaction.user_id == user_id,
            Transaction.type.in_(["income", "expense"]),
            Transaction.date >= start,
            Transaction.date <= end,
        )
        .group_by(Transaction.date, Transaction.type)
        .all()
    )
    by_day = defaultdict(lambda: {"income": 0, "expense": 0})
    for d, t, total in rows:
        by_day[d][t] = int(total or 0)
    series = []
    cursor = start
    while cursor <= end:
        income = by_day[cursor]["income"]
        expense = by_day[cursor]["expense"]
        series.append(
            {
                "date": cursor.isoformat(),
                "income": from_minor(income),
                "expense": from_minor(expense),
                "net": from_minor(income - expense),
            }
        )
        cursor += timedelta(days=1)
    return series


def spending_by_category(user_id, start, end):
    rows = (
        db.session.query(Category.name, Category.color, func.sum(Transaction.amount_minor))
        .join(Category, Category.id == Transaction.category_id, isouter=True)
        .filter(
            Transaction.user_id == user_id,
            Transaction.type == "expense",
            Transaction.date >= start,
            Transaction.date <= end,
        )
        .group_by(Category.name, Category.color)
        .all()
    )
    return [
        {"name": name or "Uncategorized", "color": color or "#64748b", "value": from_minor(int(total or 0))}
        for name, color, total in rows
        if total
    ]


def spending_by_account(user_id, start, end):
    rows = (
        db.session.query(Account.name, func.sum(Transaction.amount_minor))
        .join(Account, Account.id == Transaction.account_id)
        .filter(
            Transaction.user_id == user_id,
            Transaction.type == "expense",
            Transaction.date >= start,
            Transaction.date <= end,
        )
        .group_by(Account.name)
        .all()
    )
    return [{"name": name, "value": from_minor(int(total or 0))} for name, total in rows]


def income_by_source(user_id, start, end):
    rows = (
        db.session.query(Category.name, func.sum(Transaction.amount_minor))
        .join(Category, Category.id == Transaction.category_id, isouter=True)
        .filter(
            Transaction.user_id == user_id,
            Transaction.type == "income",
            Transaction.date >= start,
            Transaction.date <= end,
        )
        .group_by(Category.name)
        .all()
    )
    return [{"name": name or "Uncategorized", "value": from_minor(int(total or 0))} for name, total in rows]


def month_summary(user_id, month=None):
    month = month or month_key(date.today())
    start, end = month_range(month)
    income = _sum(user_id, "income", start, end)
    expense = _sum(user_id, "expense", start, end)
    days = max((min(date.today(), end) - start).days + 1, 1)
    savings_rate = round((income - expense) * 10000 / income) / 100 if income else 0
    return {
        "month": month,
        "income": from_minor(income),
        "expense": from_minor(expense),
        "net": from_minor(income - expense),
        "savings_rate": savings_rate,
        "avg_daily_spend": from_minor(int(expense / days)),
        "start": start.isoformat(),
        "end": end.isoformat(),
        "income_minor": income,
        "expense_minor": expense,
    }


def compare_months(user_id):
    this_key = month_key(date.today())
    last_start, _ = month_range(this_key)
    from ..utils.dates import add_months

    last_key = month_key(add_months(last_start, -1))
    current = month_summary(user_id, this_key)
    previous = month_summary(user_id, last_key)
    return {"current": current, "previous": previous}


def analytics_bundle(user_id, period="30d"):
    days = period_days(period)
    end = date.today()
    start = end - timedelta(days=days - 1)
    this_month = month_summary(user_id)
    return {
        "period": period,
        "cashflow": cashflow_series(user_id, period),
        "spending_by_category": spending_by_category(user_id, start, end),
        "spending_by_account": spending_by_account(user_id, start, end),
        "income_by_source": income_by_source(user_id, start, end),
        "this_month": this_month,
        "comparison": compare_months(user_id),
        "avg_monthly_spend": this_month["expense"],
    }
