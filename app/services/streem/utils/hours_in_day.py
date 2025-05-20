import re

import pendulum
from pendulum import DateTime

from app.constants.time_zones import PARIS_TZ


def hours_in_day(day: str) -> int:
    """
    Calculate the number of hours in a given day in Paris timezone, accounting for DST transitions.

    Args:
        day: Date string in YYYY-MM-DD format (e.g., "2025-05-20").

    Returns:
        int: Number of hours in the day (24 for normal days, 23 or 25 during DST transitions).

    Raises:
        ValueError: If the date string is invalid or not in YYYY-MM-DD format.
    """
    # Validate format
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", day):
        msg = f"Invalid date format: '{day}'. Expected YYYY-MM-DD"
        raise ValueError(msg)

    try:
        delivery_date = pendulum.parse(day, tz=PARIS_TZ, strict=True)
        if not isinstance(delivery_date, DateTime):
            msg = f"Not able to parse: '{day}' as date"
            raise TypeError(msg)
        start = delivery_date.start_of("day")
        end = start.add(days=1)
        hours = int((end - start).total_hours())
    except ValueError as e:
        msg = f"Invalid date: '{day}'"
        raise ValueError(msg) from e
    else:
        return hours


