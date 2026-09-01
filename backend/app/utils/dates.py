from datetime import date, datetime, timedelta


def parse_date(value, field="date"):
    if value is None or value == "":
        raise ValueError(f"{field} is required")
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = str(value)[:10]
    try:
        return datetime.strptime(text, "%Y-%m-%d").date()
    except ValueError as exc:
        raise ValueError(f"{field} must be YYYY-MM-DD") from exc


def month_key(d: date) -> str:
    return d.strftime("%Y-%m")


def month_range(key: str):
    start = datetime.strptime(key + "-01", "%Y-%m-%d").date()
    if start.month == 12:
        end = date(start.year + 1, 1, 1) - timedelta(days=1)
    else:
        end = date(start.year, start.month + 1, 1) - timedelta(days=1)
    return start, end


def add_months(d: date, months: int) -> date:
    month = d.month - 1 + months
    year = d.year + month // 12
    month = month % 12 + 1
    day = min(d.day, _days_in_month(year, month))
    return date(year, month, day)


def _days_in_month(year, month):
    if month == 12:
        nxt = date(year + 1, 1, 1)
    else:
        nxt = date(year, month + 1, 1)
    return (nxt - timedelta(days=1)).day


def period_days(period: str) -> int:
    mapping = {
        "7d": 7,
        "30d": 30,
        "3m": 90,
        "6m": 180,
        "1y": 365,
        "90d": 90,
    }
    return mapping.get(period, 30)
