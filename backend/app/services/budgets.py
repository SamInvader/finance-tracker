from datetime import date

from sqlalchemy import func

from ..extensions import db
from ..models import Budget, BudgetCategory, Category, Transaction
from ..utils.dates import add_months, month_key, month_range
from ..utils.money import from_minor, to_minor


def _spent_by_category(user_id, start, end):
    rows = (
        db.session.query(Transaction.category_id, func.sum(Transaction.amount_minor))
        .filter(
            Transaction.user_id == user_id,
            Transaction.type == "expense",
            Transaction.date >= start,
            Transaction.date <= end,
        )
        .group_by(Transaction.category_id)
        .all()
    )
    return {cid: int(total or 0) for cid, total in rows}


def budget_overview(user_id, month=None):
    month = month or month_key(date.today())
    start, end = month_range(month)
    budget = Budget.query.filter_by(user_id=user_id, month=month).first()
    spent_map = _spent_by_category(user_id, start, end)
    total_spent = sum(spent_map.values())
    items = []
    overall_limit = budget.overall_limit_minor if budget else 0
    allocated = 0
    if budget:
        for line in budget.categories:
            spent = spent_map.get(line.category_id, 0)
            remaining = line.amount_minor - spent
            pct = round(spent * 10000 / line.amount_minor) / 100 if line.amount_minor else 0
            allocated += line.amount_minor
            items.append(
                {
                    **line.to_dict(),
                    "spent": from_minor(spent),
                    "remaining": from_minor(remaining),
                    "percent_used": pct,
                    "status": "over" if pct >= 100 else "warning" if pct >= 80 else "ok",
                }
            )
    remaining_budget = (overall_limit or allocated) - total_spent
    return {
        "month": month,
        "overall_limit": from_minor(overall_limit),
        "allocated": from_minor(allocated),
        "spent": from_minor(total_spent),
        "remaining": from_minor(remaining_budget),
        "percent_used": round(total_spent * 10000 / allocated) / 100 if allocated else 0,
        "carry_forward": budget.carry_forward if budget else False,
        "categories": items,
        "id": budget.id if budget else None,
    }


def upsert_budget(user_id, data):
    month = data.get("month") or month_key(date.today())
    budget = Budget.query.filter_by(user_id=user_id, month=month).first()
    if not budget:
        budget = Budget(user_id=user_id, month=month)
        db.session.add(budget)
        db.session.flush()
    if "overall_limit" in data:
        budget.overall_limit_minor = to_minor(data.get("overall_limit") or 0)
    if "carry_forward" in data:
        budget.carry_forward = bool(data.get("carry_forward"))
    lines = data.get("categories") or []
    if lines:
        BudgetCategory.query.filter_by(budget_id=budget.id).delete()
        for line in lines:
            cat = Category.query.filter_by(id=line.get("category_id"), user_id=user_id).first()
            if not cat:
                continue
            db.session.add(
                BudgetCategory(
                    budget_id=budget.id,
                    category_id=cat.id,
                    amount_minor=to_minor(line.get("amount") or 0),
                )
            )
    db.session.commit()
    return budget_overview(user_id, month), None


def copy_previous_budget(user_id, month):
    start, _ = month_range(month)
    prev_month = month_key(add_months(start, -1))
    previous = Budget.query.filter_by(user_id=user_id, month=prev_month).first()
    if not previous:
        return None, "No budget exists for the previous month"
    payload = {
        "month": month,
        "overall_limit": from_minor(previous.overall_limit_minor),
        "carry_forward": previous.carry_forward,
        "categories": [
            {"category_id": c.category_id, "amount": from_minor(c.amount_minor)}
            for c in previous.categories
        ],
    }
    if previous.carry_forward:
        prev_overview = budget_overview(user_id, prev_month)
        leftover = {}
        for item in prev_overview["categories"]:
            leftover[item["category_id"]] = max(to_minor(item["remaining"]), 0)
        for line in payload["categories"]:
            line["amount"] = from_minor(to_minor(line["amount"]) + leftover.get(line["category_id"], 0))
    return upsert_budget(user_id, payload)


def budget_history(user_id):
    months = (
        Budget.query.filter_by(user_id=user_id).order_by(Budget.month.desc()).limit(24).all()
    )
    return [budget_overview(user_id, b.month) for b in months]
