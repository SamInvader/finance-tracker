from datetime import date, timedelta

from sqlalchemy import func

from ..extensions import db
from ..models import Category, RecurringTransaction, Transaction
from ..utils.dates import add_months, month_key, month_range
from ..utils.money import from_minor
from .analytics import month_summary, spending_by_category
from .budgets import budget_overview


def generate_insights(user_id):
    insights = []
    current = month_summary(user_id)
    prev_start, _ = month_range(current["month"])
    prev_key = month_key(add_months(prev_start, -1))
    previous = month_summary(user_id, prev_key)

    if current["expense_minor"] and previous["expense_minor"]:
        delta = current["expense_minor"] - previous["expense_minor"]
        if abs(delta) > 0:
            direction = "more" if delta > 0 else "less"
            insights.append(
                {
                    "title": "Spending vs last month",
                    "body": f"You spent ₦{from_minor(abs(delta)):,.2f} {direction} this month than last month.",
                    "kind": "trend",
                }
            )

    start, end = month_range(current["month"])
    cats = spending_by_category(user_id, start, end)
    if cats:
        top = max(cats, key=lambda c: c["value"])
        total = sum(c["value"] for c in cats) or 1
        insights.append(
            {
                "title": "Largest spending category",
                "body": f"Your largest spending category this month is {top['name']} ({round(top['value'] * 100 / total)}% of expenses).",
                "kind": "composition",
            }
        )
        prev_start_d, prev_end_d = month_range(prev_key)
        prev_cats = {c["name"]: c["value"] for c in spending_by_category(user_id, prev_start_d, prev_end_d)}
        for cat in cats:
            prev_val = prev_cats.get(cat["name"], 0)
            if prev_val and cat["value"] > prev_val * 1.1:
                pct = round((cat["value"] - prev_val) * 100 / prev_val)
                insights.append(
                    {
                        "title": f"{cat['name']} is up",
                        "body": f"{cat['name']} spending is {pct}% higher than last month.",
                        "kind": "category",
                    }
                )

    if current["income_minor"]:
        insights.append(
            {
                "title": "Savings rate",
                "body": f"Your savings rate this month is {current['savings_rate']}% (income minus expenses, excluding transfers).",
                "kind": "savings",
            }
        )

    upcoming = RecurringTransaction.query.filter_by(user_id=user_id, is_active=True, type="expense").all()
    next_month_start = add_months(date.today().replace(day=1), 1)
    next_month_end = add_months(next_month_start, 1) - timedelta(days=1)
    recurring_next = 0
    for rec in upcoming:
        cursor = rec.next_occurrence
        if cursor and next_month_start <= cursor <= next_month_end:
            recurring_next += rec.amount_minor
    if recurring_next:
        insights.append(
            {
                "title": "Recurring next month",
                "body": f"You have ₦{from_minor(recurring_next):,.2f} in recurring expenses scheduled next month.",
                "kind": "recurring",
            }
        )

    # consecutive monthly increases for a category
    months = []
    cursor = date.today().replace(day=1)
    for _ in range(3):
        months.append(month_key(cursor))
        cursor = add_months(cursor, -1)
    months = list(reversed(months))
    names = {c.name for c in Category.query.filter_by(user_id=user_id, kind="expense").all()}
    for name in names:
        totals = []
        for m in months:
            s, e = month_range(m)
            val = (
                db.session.query(func.coalesce(func.sum(Transaction.amount_minor), 0))
                .join(Category, Category.id == Transaction.category_id)
                .filter(
                    Transaction.user_id == user_id,
                    Transaction.type == "expense",
                    Category.name == name,
                    Transaction.date >= s,
                    Transaction.date <= e,
                )
                .scalar()
            )
            totals.append(int(val or 0))
        if totals[0] and totals[1] > totals[0] and totals[2] > totals[1]:
            insights.append(
                {
                    "title": f"{name} rising",
                    "body": f"{name} spending has increased for three consecutive months.",
                    "kind": "streak",
                }
            )

    overview = budget_overview(user_id)
    for line in overview["categories"]:
        if line["percent_used"] >= 100:
            insights.append(
                {
                    "title": f"{line['category_name']} budget exceeded",
                    "body": f"You have spent {line['percent_used']}% of the {line['category_name']} budget this month.",
                    "kind": "budget",
                }
            )

    if not insights:
        insights.append(
            {
                "title": "Not enough history yet",
                "body": "Add more transactions across months to unlock trend insights. All insights are calculated from your data only.",
                "kind": "empty",
            }
        )
    return insights
