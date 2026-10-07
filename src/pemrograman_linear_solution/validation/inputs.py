import math


def parse_count(raw: str, label: str, maximum: int) -> int:
    try:
        value = int(raw.strip())
    except ValueError as error:
        raise ValueError(f"ENTER A WHOLE NUMBER FOR {label}.") from error
    if not 1 <= value <= maximum:
        raise ValueError(f"{label} MUST BE BETWEEN 1 AND {maximum}.")
    return value


def parse_finite_number(raw: str) -> float:
    try:
        value = float(raw.strip())
    except ValueError as error:
        raise ValueError("ENTER A VALID NUMBER, FOR EXAMPLE 3 OR -1.5.") from error
    if not math.isfinite(value):
        raise ValueError("THE NUMBER MUST BE FINITE.")
    return value


def parse_unique_name(raw: str, existing: set[str]) -> str:
    name = raw.strip()
    if not name:
        raise ValueError("A NAME CANNOT BE EMPTY.")
    if any(name.casefold() == item.casefold() for item in existing):
        raise ValueError("EACH VARIABLE NAME MUST BE UNIQUE.")
    if any(character.isspace() for character in name):
        raise ValueError("USE A SINGLE TOKEN FOR EACH VARIABLE NAME.")
    return name
