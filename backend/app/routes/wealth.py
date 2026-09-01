from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from ..extensions import db
from ..models import Asset, Debt, Liability
from ..services.debts import payoff_plan, record_payment
from ..services.networth import compute_net_worth
from ..utils.dates import parse_date
from ..utils.money import to_minor
from ..utils.responses import error, success

bp = Blueprint("wealth", __name__)


def uid():
    return int(get_jwt_identity())


@bp.get("/debts")
@jwt_required()
def debts_index():
    items = Debt.query.filter_by(user_id=uid()).all()
    from ..utils.money import from_minor

    remaining = sum(d.remaining_minor for d in items)
    paid = sum(max(d.original_minor - d.remaining_minor, 0) for d in items)
    return success({"items": [d.to_dict() for d in items], "total_remaining": from_minor(remaining), "total_paid": from_minor(paid)})


@bp.post("/debts")
@jwt_required()
def debts_create():
    data = request.get_json() or {}
    if not data.get("name"):
        return error("Name is required", 400)
    original = to_minor(data.get("original") or data.get("remaining"))
    remaining = to_minor(data.get("remaining") or data.get("original"))
    rate = data.get("interest_rate") or 0
    debt = Debt(
        user_id=uid(),
        name=data["name"].strip(),
        lender=data.get("lender"),
        original_minor=original,
        remaining_minor=remaining,
        interest_rate_bps=int(round(float(rate) * 100)),
        minimum_payment_minor=to_minor(data.get("minimum_payment") or 0),
        payment_frequency=data.get("payment_frequency") or "monthly",
        due_date=parse_date(data["due_date"], "due_date") if data.get("due_date") else None,
        notes=data.get("notes"),
    )
    db.session.add(debt)
    db.session.commit()
    return success(debt.to_dict(), status=201)


@bp.patch("/debts/<int:debt_id>")
@jwt_required()
def debts_update(debt_id):
    debt = Debt.query.filter_by(id=debt_id, user_id=uid()).first()
    if not debt:
        return error("Not found", 404)
    data = request.get_json() or {}
    if "name" in data:
        debt.name = data["name"]
    if "notes" in data:
        debt.notes = data["notes"]
    if "interest_rate" in data:
        debt.interest_rate_bps = int(round(float(data["interest_rate"]) * 100))
    if "minimum_payment" in data:
        debt.minimum_payment_minor = to_minor(data["minimum_payment"])
    db.session.commit()
    return success(debt.to_dict())


@bp.delete("/debts/<int:debt_id>")
@jwt_required()
def debts_delete(debt_id):
    debt = Debt.query.filter_by(id=debt_id, user_id=uid()).first()
    if not debt:
        return error("Not found", 404)
    db.session.delete(debt)
    db.session.commit()
    return success({"deleted": True})


@bp.post("/debts/<int:debt_id>/payments")
@jwt_required()
def debts_pay(debt_id):
    data, err = record_payment(uid(), debt_id, request.get_json() or {})
    if err:
        return error(err if isinstance(err, str) else "Invalid payment", 400, err if isinstance(err, dict) else None)
    return success(data)


@bp.get("/debts/payoff")
@jwt_required()
def debts_payoff():
    method = request.args.get("method") or "snowball"
    extra = to_minor(request.args.get("extra") or 0)
    return success(payoff_plan(uid(), method, extra))


@bp.get("/net-worth")
@jwt_required()
def net_worth():
    return success(compute_net_worth(uid()))


@bp.post("/assets")
@jwt_required()
def add_asset():
    data = request.get_json() or {}
    asset = Asset(user_id=uid(), name=data.get("name") or "Asset", kind=data.get("kind") or "other", value_minor=to_minor(data.get("value") or 0), notes=data.get("notes"))
    db.session.add(asset)
    db.session.commit()
    return success(asset.to_dict(), status=201)


@bp.delete("/assets/<int:asset_id>")
@jwt_required()
def del_asset(asset_id):
    asset = Asset.query.filter_by(id=asset_id, user_id=uid()).first()
    if not asset:
        return error("Not found", 404)
    db.session.delete(asset)
    db.session.commit()
    return success({"deleted": True})


@bp.post("/liabilities")
@jwt_required()
def add_liability():
    data = request.get_json() or {}
    item = Liability(user_id=uid(), name=data.get("name") or "Liability", kind=data.get("kind") or "other", value_minor=to_minor(data.get("value") or 0), notes=data.get("notes"))
    db.session.add(item)
    db.session.commit()
    return success(item.to_dict(), status=201)


@bp.delete("/liabilities/<int:item_id>")
@jwt_required()
def del_liability(item_id):
    item = Liability.query.filter_by(id=item_id, user_id=uid()).first()
    if not item:
        return error("Not found", 404)
    db.session.delete(item)
    db.session.commit()
    return success({"deleted": True})
