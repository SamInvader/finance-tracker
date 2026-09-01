from datetime import date

from ..extensions import db
from ..models import Account, SavingsContribution, SavingsGoal
from ..utils.dates import parse_date
from ..utils.money import to_minor


def list_goals(user_id):
    goals = SavingsGoal.query.filter_by(user_id=user_id).order_by(SavingsGoal.priority, SavingsGoal.name).all()
    return [g.to_dict() for g in goals]


def create_goal(user_id, data):
    if not data.get("name"):
        return None, {"name": "Name is required"}
    try:
        target = to_minor(data.get("target"))
    except ValueError as exc:
        return None, {"target": str(exc)}
    if target <= 0:
        return None, {"target": "Target must be greater than zero"}
    account_id = data.get("account_id")
    if account_id and not Account.query.filter_by(id=account_id, user_id=user_id).first():
        return None, {"account_id": "Invalid account"}
    deadline = None
    if data.get("deadline"):
        deadline = parse_date(data["deadline"], "deadline")
    goal = SavingsGoal(
        user_id=user_id,
        account_id=account_id,
        name=data["name"].strip(),
        target_minor=target,
        current_minor=to_minor(data.get("current") or 0),
        deadline=deadline,
        description=data.get("description"),
        icon=data.get("icon") or "piggy-bank",
        priority=int(data.get("priority") or 3),
    )
    db.session.add(goal)
    db.session.commit()
    return goal.to_dict(), None


def contribute(user_id, goal_id, data, withdraw=False):
    goal = SavingsGoal.query.filter_by(id=goal_id, user_id=user_id).first()
    if not goal:
        return None, "Goal not found"
    amount = to_minor(data.get("amount"))
    if amount <= 0:
        return None, {"amount": "Amount must be greater than zero"}
    signed = -amount if withdraw else amount
    if withdraw and amount > goal.current_minor:
        return None, {"amount": "Cannot withdraw more than the current saved amount"}
    contrib = SavingsContribution(
        goal_id=goal.id,
        amount_minor=signed,
        date=parse_date(data.get("date") or date.today().isoformat()),
        note=data.get("note"),
    )
    goal.current_minor += signed
    db.session.add(contrib)
    db.session.commit()
    return {"goal": goal.to_dict(), "contribution": contrib.to_dict()}, None


def update_goal(user_id, goal_id, data):
    goal = SavingsGoal.query.filter_by(id=goal_id, user_id=user_id).first()
    if not goal:
        return None, "Goal not found"
    if "name" in data and data["name"]:
        goal.name = data["name"].strip()
    if "target" in data:
        goal.target_minor = to_minor(data["target"])
    if "deadline" in data:
        goal.deadline = parse_date(data["deadline"], "deadline") if data["deadline"] else None
    if "description" in data:
        goal.description = data["description"]
    if "icon" in data:
        goal.icon = data["icon"]
    if "priority" in data:
        goal.priority = int(data["priority"])
    if "account_id" in data:
        goal.account_id = data["account_id"]
    db.session.commit()
    return goal.to_dict(), None


def delete_goal(user_id, goal_id):
    goal = SavingsGoal.query.filter_by(id=goal_id, user_id=user_id).first()
    if not goal:
        return None, "Goal not found"
    db.session.delete(goal)
    db.session.commit()
    return True, None
