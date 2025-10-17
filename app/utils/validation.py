import re


_VIN_RE = re.compile(r"^[A-HJ-NPR-Z0-9]{11,17}$", re.IGNORECASE)  # excludes I, O, Q


def validate_vin(vin: str) -> str:
    vin = (vin or "").strip().upper()
    if not _VIN_RE.match(vin):
        raise ValueError("vin must be 11–17 chars, alphanumeric (no I/O/Q)")
    return vin
