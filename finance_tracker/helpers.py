from datetime import datetime


def format_money(value):
    return f"${value:,.2f}"


def month_label(date_value):
    if isinstance(date_value, str):
        return datetime.strptime(date_value, "%Y-%m").strftime("%b %Y")
    return date_value.strftime("%b %Y")
