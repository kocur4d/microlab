"""Shared validation for integer experiment parameters."""


def validate_integer(
    value: int, name: str, minimum: int, maximum: int | None = None
) -> None:
    """Reject non-integers (including booleans) and values outside the bounds."""
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an integer")
    if value < minimum or (maximum is not None and value > maximum):
        bounds = f"at least {minimum}" if maximum is None else f"{minimum}–{maximum}"
        raise ValueError(f"{name} must be {bounds}; got {value}")
