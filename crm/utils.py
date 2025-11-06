import re
from decimal import Decimal, InvalidOperation


PHONE_RE = re.compile(r'^(\+?\d{7,15}|(\d{3}-\d{3}-\d{4}))$')


def validate_phone(phone):
    """Raise ValueError if phone provided and invalid."""
    if phone and not PHONE_RE.match(phone):
        raise ValueError("Invalid phone format. Use +1234567890 or 123-456-7890.")


def to_decimal(value):
    """Safely convert a float/str/int to Decimal or raise ValueError."""
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError(f"Invalid decimal value: {value}")