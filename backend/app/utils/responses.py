from flask import jsonify


def success(data=None, message=None, status=200, **extra):
    payload = {"ok": True}
    if message:
        payload["message"] = message
    if data is not None:
        payload["data"] = data
    payload.update(extra)
    return jsonify(payload), status


def error(message, status=400, details=None):
    payload = {"ok": False, "error": message}
    if details is not None:
        payload["details"] = details
    return jsonify(payload), status
