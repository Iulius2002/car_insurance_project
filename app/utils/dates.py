from datetime import datetime, date

MIN_YEAR = 1900
MAX_YEAR = 2100

def ensure_date_in_range(d: date) -> None:
    if d.year < MIN_YEAR or d.year > MAX_YEAR:
        raise ValueError(f"Date out of allowed range {MIN_YEAR}-{MAX_YEAR}.")

def parse_date_str(value: str) -> date:
    try:
        d = datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as e:
        raise ValueError("Invalid date format, expected YYYY-MM-DD") from e
    ensure_date_in_range(d)
    return d