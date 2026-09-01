from datetime import date

from ..models import Account, RecurringTransaction, Transaction
from ..utils.dates import month_range, month_key
from ..utils.money import from_minor
from .analytics import month_summary
from .budgets import budget_overview
from .goals import list_goals
from .networth import compute_net_worth


def financial_health(user_id):
    """Heuristic 0-100 score from stored data. Not a credit score."""
    current = month_summary(user_id)
    income = current["income_minor"]
    expense = current["expense_minor"]
    savings_rate = ((income - expense) / income) if income else 0
    savings_score = max(min(savings_rate / 0.2, 1), 0) * 25

    overview = budget_overview(user_id)
    if overview["categories"]:
        over = sum(1 for c in overview["categories"] if c["percent_used"] >= 100)
        adherence = 1 - (over / len(overview["categories"]))
    else:
        adherence = 0.5
    budget_score = adherence * 20

    goals = list_goals(user_id)
    emergency = next((g for g in goals if "emergency" in g["name"].lower()), None)
    if emergency and emergency["target"]:
        emergency_score = min(emergency["current"] / emergency["target"], 1) * 20
    elif goals:
        emergency_score = min(sum(g["percent"] for g in goals) / (100 * len(goals)), 1) * 15
    else:
        emergency_score = 8

    nw = compute_net_worth(user_id, persist=False)
    assets = nw["assets"]
    debts = nw["liabilities"]
    if assets + debts == 0:
        debt_score = 12
    else:
        burden = debts / (assets + debts) if (assets + debts) else 1
        debt_score = max(1 - burden, 0) * 20

    rec_exp = (
        RecurringTransaction.query.filter_by(user_id=user_id, is_active=True, type="expense").count()
    )
    rec_score = 8 if rec_exp <= 8 else 5 if rec_exp <= 15 else 2

    # cash-flow consistency: last 3 months net variance
    from ..utils.dates import add_months

    nets = []
    cursor = date.today().replace(day=1)
    for _ in range(3):
        s = month_summary(user_id, month_key(cursor))
        nets.append(s["income_minor"] - s["expense_minor"])
        cursor = add_months(cursor, -1)
    if max(abs(n) for n in nets) == 0:
        consistency = 7
    else:
        avg = sum(nets) / 3
        var = sum((n - avg) ** 2 for n in nets) / 3
        consistency = 10 if var < (abs(avg) + 1) ** 2 else 6 if var < (abs(avg) * 3) ** 2 else 3

    total = round(savings_score + budget_score + emergency_score + debt_score + rec_score + consistency)
    total = int(max(min(total, 100), 0))
    return {
        "score": total,
        "label": "Strong" if total >= 75 else "Fair" if total >= 50 else "Needs attention",
        "components": {
            "savings_rate": round(savings_score, 1),
            "budget_adherence": round(budget_score, 1),
            "emergency_fund": round(emergency_score, 1),
            "debt_burden": round(debt_score, 1),
            "recurring_load": rec_score,
            "cashflow_consistency": consistency,
        },
        "explanation": (
            "This is a simple in-app health score (0–100), not a credit score or professional diagnosis. "
            "It weights savings rate (target ~20%), staying within category budgets, emergency-fund progress, "
            "debt relative to assets, the number of recurring expenses, and how consistent monthly cash flow has been."
        ),
    }
