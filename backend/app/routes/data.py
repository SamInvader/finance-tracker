from flask import Blueprint, Response, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from ..services.imex import commit_import, export_csv, full_backup, preview_csv, restore_backup
from ..services.notifications import list_notifications, mark_read
from ..utils.responses import error, success

bp = Blueprint("data", __name__)


def uid():
    return int(get_jwt_identity())


@bp.get("/notifications")
@jwt_required()
def notifs():
    return success(list_notifications(uid()))


@bp.post("/notifications/<int:notif_id>/read")
@jwt_required()
def notif_read(notif_id):
    ok, err = mark_read(uid(), notif_id)
    if err:
        return error(err, 404)
    return success({"read": True})


@bp.post("/notifications/read-all")
@jwt_required()
def notif_read_all():
    mark_read(uid(), all_items=True)
    return success({"read": True})


@bp.get("/export/<kind>")
@jwt_required()
def export_kind(kind):
    try:
        content = export_csv(uid(), kind)
    except ValueError as exc:
        return error(str(exc), 400)
    return Response(
        content,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={kind}.csv"},
    )


@bp.post("/import/preview")
@jwt_required()
def import_preview():
    data = request.get_json() or {}
    text = data.get("csv") or ""
    mapping = data.get("mapping") or {}
    if not text or not mapping.get("date") or not mapping.get("amount"):
        return error("CSV text and date/amount column mapping are required", 400)
    return success(preview_csv(uid(), text, mapping))


@bp.post("/import/commit")
@jwt_required()
def import_commit():
    data = request.get_json() or {}
    result = commit_import(uid(), data.get("rows") or [], data.get("account_id"))
    return success(result)


@bp.get("/backup")
@jwt_required()
def backup():
    return success(full_backup(uid()))


@bp.post("/restore")
@jwt_required()
def restore():
    data = request.get_json() or {}
    payload = data.get("backup")
    result, err = restore_backup(uid(), payload, replace=bool(data.get("replace")))
    if err:
        return error(err, 400)
    return success(result)
