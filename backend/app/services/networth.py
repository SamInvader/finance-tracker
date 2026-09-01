from datetime import date

from sqlalchemy import func

from ..extensions import db
from ..models import Account, Asset, Debt, Liability, NetWorthSnapshot, Transaction
from ..utils.money import from_minor


ACCOUNT_ASSET_TYPES = {"cash", "bank", "wallet", "savings", "investment", "other"}


def compute_net_worth(user_id, persist=True):
    accounts = Account.query.filter_by(user_id=user_id, is_active=True).all()
    account_assets = sum(a.balance_minor for a in accounts if a.type in ACCOUNT_ASSET_TYPES)
    extra_assets = (
        db.session.query(func.coalesce(func.sum(Asset.value_minor), 0))
        .filter_by(user_id=user_id)
        .scalar()
    )
    extra_liabilities = (
        db.session.query(func.coalesce(func.sum(Liability.value_minor), 0))
        .filter_by(user_id=user_id)
        .scalar()
    )
    debts = (
        db.session.query(func.coalesce(func.sum(Debt.remaining_minor), 0))
        .filter_by(user_id=user_id)
        .scalar()
    )
    credit = sum(a.balance_minor for a in accounts if a.type == "credit")
    assets_minor = int(account_assets) + int(extra_assets or 0)
    liabilities_minor = int(extra_liabilities or 0) + int(debts or 0) + int(credit)
    net = assets_minor - liabilities_minor
    today = date.today()
    if persist:
        snap = NetWorthSnapshot.query.filter_by(user_id=user_id, date=today).first()
        if not snap:
            snap = NetWorthSnapshot(user_id=user_id, date=today)
            db.session.add(snap)
        snap.assets_minor = assets_minor
        snap.liabilities_minor = liabilities_minor
        snap.net_worth_minor = net
        db.session.commit()
    history = (
        NetWorthSnapshot.query.filter_by(user_id=user_id)
        .order_by(NetWorthSnapshot.date.asc())
        .all()
    )
    previous = history[-2] if len(history) >= 2 else None
    change = net - previous.net_worth_minor if previous else 0
    pct = None
    if previous and previous.net_worth_minor:
        pct = round(change * 10000 / abs(previous.net_worth_minor)) / 100
    return {
        "current": from_minor(net),
        "assets": from_minor(assets_minor),
        "liabilities": from_minor(liabilities_minor),
        "previous": from_minor(previous.net_worth_minor) if previous else None,
        "change": from_minor(change),
        "percent_change": pct,
        "breakdown": {
            "accounts": from_minor(account_assets),
            "other_assets": from_minor(int(extra_assets or 0)),
            "debts": from_minor(int(debts or 0)),
            "other_liabilities": from_minor(int(extra_liabilities or 0) + credit),
        },
        "history": [h.to_dict() for h in history],
        "assets_list": [a.to_dict() for a in Asset.query.filter_by(user_id=user_id).all()],
        "liabilities_list": [l.to_dict() for l in Liability.query.filter_by(user_id=user_id).all()],
        "debts": [d.to_dict() for d in Debt.query.filter_by(user_id=user_id).all()],
        "accounts": [a.to_dict() for a in accounts],
    }
