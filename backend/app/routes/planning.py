from datetime import date

from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from ..extensions import db
from ..models import Account, Bill, RecurringTransaction, Subscription
from ..services.recurring import create_recurring, process_due
from ..utils.dates import parse_date
from ..utils.money import to_minor
from ..utils.responses import error, success

bp = Blueprint("planning", __name__)


def uid():
    return int(get_jwt_identity())


@bp.get("/recurring")
@jwt_required()
def rec_index():
    process_due(uid())
    items = RecurringTransaction.query.filter_by(user_id=uid()).order_by(RecurringTransaction.next_occurrence).all()
    return success([i.to_dict() for i in items])


@bp.post("/recurring")
@jwt_required()
def rec_create():
    data, errors = create_recurring(uid(), request.get_json() or {})
    if errors:
        return error("Could not create recurring item", 400, errors)
    return success(data, status=201)


@bp.patch("/recurring/<int:item_id>")
@jwt_required()
def rec_update(item_id):
    item = RecurringTransaction.query.filter_by(id=item_id, user_id=uid()).first()
    if not item:
        return error("Not found", 404)
    data = request.get_json() or {}
    for field in ["description", "frequency", "type"]:
        if field in data:
            setattr(item, field, data[field])
    if "interval" in data:
        item.interval = int(data["interval"])
    if "amount" in data:
        item.amount_minor = to_minor(data["amount"])
    if "is_active" in data:
        item.is_active = bool(data["is_active"])
    if "account_id" in data:
        item.account_id = data["account_id"]
    if "category_id" in data:
        item.category_id = data["category_id"]
    db.session.commit()
    return success(item.to_dict())


@bp.delete("/recurring/<int:item_id>")
@jwt_required()
def rec_delete(item_id):
    item = RecurringTransaction.query.filter_by(id=item_id, user_id=uid()).first()
    if not item:
        return error("Not found", 404)
    db.session.delete(item)
    db.session.commit()
    return success({"deleted": True})


@bp.get("/bills")
@jwt_required()
def bills_index():
    return success([b.to_dict() for b in Bill.query.filter_by(user_id=uid()).order_by(Bill.due_date).all()])


@bp.post("/bills")
@jwt_required()
def bills_create():
    data = request.get_json() or {}
    if not data.get("name") or data.get("amount") is None:
        return error("Name and amount are required", 400)
    bill = Bill(
        user_id=uid(),
        name=data["name"].strip(),
        amount_minor=to_minor(data["amount"]),
        due_date=parse_date(data.get("due_date") or date.today().isoformat(), "due_date"),
        frequency=data.get("frequency") or "monthly",
        category_id=data.get("category_id"),
        account_id=data.get("account_id"),
        status="upcoming",
    )
    db.session.add(bill)
    db.session.commit()
    return success(bill.to_dict(), status=201)


@bp.patch("/bills/<int:bill_id>")
@jwt_required()
def bills_update(bill_id):
    bill = Bill.query.filter_by(id=bill_id, user_id=uid()).first()
    if not bill:
        return error("Not found", 404)
    data = request.get_json() or {}
    if "name" in data:
        bill.name = data["name"]
    if "amount" in data:
        bill.amount_minor = to_minor(data["amount"])
    if "due_date" in data:
        bill.due_date = parse_date(data["due_date"], "due_date")
    if "status" in data:
        bill.status = data["status"]
        if data["status"] == "paid":
            bill.last_paid = date.today()
    db.session.commit()
    return success(bill.to_dict())


@bp.delete("/bills/<int:bill_id>")
@jwt_required()
def bills_delete(bill_id):
    bill = Bill.query.filter_by(id=bill_id, user_id=uid()).first()
    if not bill:
        return error("Not found", 404)
    db.session.delete(bill)
    db.session.commit()
    return success({"deleted": True})


@bp.get("/subscriptions")
@jwt_required()
def subs_index():
    items = Subscription.query.filter_by(user_id=uid()).order_by(Subscription.name).all()
    monthly = sum(s.monthly_minor() for s in items if s.status == "active")
    from ..utils.money import from_minor

    return success({"items": [s.to_dict() for s in items], "monthly_total": from_minor(monthly), "annual_total": from_minor(monthly * 12)})


@bp.post("/subscriptions")
@jwt_required()
def subs_create():
    data = request.get_json() or {}
    if not data.get("name"):
        return error("Name is required", 400)
    sub = Subscription(
        user_id=uid(),
        name=data["name"].strip(),
        amount_minor=to_minor(data.get("amount")),
        billing_cycle=data.get("billing_cycle") or "monthly",
        next_billing_date=parse_date(data.get("next_billing_date") or date.today().isoformat(), "next_billing_date"),
        category_id=data.get("category_id"),
        account_id=data.get("account_id"),
        status=data.get("status") or "active",
    )
    db.session.add(sub)
    db.session.commit()
    return success(sub.to_dict(), status=201)


@bp.patch("/subscriptions/<int:sub_id>")
@jwt_required()
def subs_update(sub_id):
    sub = Subscription.query.filter_by(id=sub_id, user_id=uid()).first()
    if not sub:
        return error("Not found", 404)
    data = request.get_json() or {}
    if "name" in data:
        sub.name = data["name"]
    if "amount" in data:
        sub.amount_minor = to_minor(data["amount"])
    if "billing_cycle" in data:
        sub.billing_cycle = data["billing_cycle"]
    if "next_billing_date" in data:
        sub.next_billing_date = parse_date(data["next_billing_date"], "next_billing_date")
    if "status" in data:
        sub.status = data["status"]
    db.session.commit()
    return success(sub.to_dict())


@bp.delete("/subscriptions/<int:sub_id>")
@jwt_required()
def subs_delete(sub_id):
    sub = Subscription.query.filter_by(id=sub_id, user_id=uid()).first()
    if not sub:
        return error("Not found", 404)
    db.session.delete(sub)
    db.session.commit()
    return success({"deleted": True})
