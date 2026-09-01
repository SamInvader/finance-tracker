from decimal import ROUND_HALF_EVEN, Decimal, InvalidOperation

TWOPLACES = Decimal("0.01")


def to_minor(value) -> int:
    """Convert a currency amount (naira) to integer kobo/cents."""
    if value is None:
        raise ValueError("Amount is required")
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError("Amount must be a valid number") from exc
    if not amount.is_finite():
        raise ValueError("Amount must be a finite number")
    quantized = amount.quantize(TWOPLACES, rounding=ROUND_HALF_EVEN)
    return int(quantized * 100)


def from_minor(minor: int) -> float:
    """Return a JSON-safe decimal amount from integer minor units."""
    if minor is None:
        return 0.0
    value = (Decimal(int(minor)) / Decimal(100)).quantize(TWOPLACES, rounding=ROUND_HALF_EVEN)
    return float(value)


def parse_optional_amount(value):
    if value is None or value == "":
        return None
    return to_minor(value)
