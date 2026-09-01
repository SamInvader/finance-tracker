from datetime import date

from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from ..extensions import db
from ..models import Account, Transaction

from ..services.analytics import analytics_bundle
from ..services.dashboard import dashboard
from ..services.forecast import forecast
from ..services.health import financial_health
from ..services.insights import generate_insights
from ..services.search import calendar_events, global_search
from ..utils.responses import success

bp = Blueprint("analytics", __name__)


def uid():
    return int(get_jwt_identity())


@bp.get("/dashboard")
@jwt_required()
def dash():
    return success(dashboard(uid(), request.args.get("period") or "30d"))


@bp.get("/analytics")
@jwt_required()
def analytics():
    return success(analytics_bundle(uid(), request.args.get("period") or "30d"))


@bp.get("/forecast")
@jwt_required()
def forecast_view():
    days = int(request.args.get("days") or 30)
    return success(forecast(uid(), days))


@bp.get("/insights")
@jwt_required()
def insights():
    return success(generate_insights(uid()))


@bp.get("/health")
@jwt_required()
def health():
    return success(financial_health(uid()))


@bp.get("/search")
@jwt_required()
def search():
    return success(global_search(uid(), request.args.get("q") or ""))


@bp.get("/calendar")
@jwt_required()
def calendar():
    today = date.today()
    year = int(request.args.get("year") or today.year)
    month = int(request.args.get("month") or today.month)
    return success(calendar_events(uid(), year, month))
