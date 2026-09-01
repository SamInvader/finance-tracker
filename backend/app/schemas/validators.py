import re

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
ALLOWED_TX_TYPES = {"income", "expense", "transfer"}
ALLOWED_ACCOUNT_TYPES = {
    "cash",
    "bank",
    "wallet",
    "savings",
    "investment",
    "credit",
    "other",
}
ALLOWED_FREQUENCIES = {"daily", "weekly", "monthly", "yearly", "custom"}
ALLOWED_THEMES = {"light", "dark", "system"}


def require_fields(data, fields):
    errors = {}
    data = data or {}
    for field in fields:
        if data.get(field) in (None, ""):
            errors[field] = "This field is required"
    return errors


def validate_email(email):
    if not email or not EMAIL_RE.match(email.strip().lower()):
        return "Enter a valid email address"
    return None


def validate_password(password, confirm=None):
    if not password or len(password) < 8:
        return "Password must be at least 8 characters"
    if confirm is not None and password != confirm:
        return "Passwords do not match"
    return None


def validate_positive_minor(amount_minor, field="amount"):
    if amount_minor is None:
        return {field: "Amount is required"}
    if amount_minor <= 0:
        return {field: "Amount must be greater than zero"}
    return {}
