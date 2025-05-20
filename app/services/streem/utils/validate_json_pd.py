import logging

import pandas as pd
from pendulum import interval

from app.constants.time_zones import PARIS_TZ
from app.services.streem.utils.day_boundaries import day_boundaries
from app.services.streem.utils.validation_context import ValidationContext


JsonResponse = list[dict[str, str | float]]  # List of dictionaries with 'date' (str) and 'data' (float) keys.


def validate_json_pd(volume_data: JsonResponse, context: ValidationContext) -> bool:  # noqa: PLR0911
    """Validate volume_data for structure, data range, and timestamp frequency.

    Args:
        volume_data: List of dictionaries with 'date' and 'data' keys.
        context: ValidationContext with delivery_date, freq, mini, and maxi.

    Returns:
        bool: True if data is valid, False if validation fails with logged error.

    """
    # Validate data can be converted to DataFrame
    try:
        volume_df = pd.DataFrame(volume_data)
    except (ValueError, AttributeError):
        msg = "Cannot convert volume_data to DataFrame"
        logging.exception(msg)
        return False

    # Validate exactly 2 columns: 'date' and 'data'
    if set(volume_df.columns) != {"date", "data"}:
        msg = "Each item must have exactly 'date' and 'data' keys"
        logging.exception(msg)
        return False

    # Validate data type
    if not pd.api.types.is_numeric_dtype(volume_df["data"]):
        msg = "All 'data' values must be numeric"
        logging.exception(msg)
        return False

    # Validate data values
    if (volume_df["data"] < context.mini).any() or (volume_df["data"] > context.maxi).any():
        msg = f"All 'data' values must be between {context.mini} and {context.maxi}"
        logging.exception(msg)
        return False

    # Validate dates can be parsed
    try:
        volume_df["date"] = pd.to_datetime(
            volume_df["date"], format="%Y-%m-%dT%H:%M:%S%z", utc=True, errors="raise"
        ).dt.tz_convert(PARIS_TZ)
    except (ValueError, TypeError):
        msg = "All 'date' values must be valid ISO 8601 timestamps with timezone"
        logging.exception(msg)
        return False

    start, end = day_boundaries(context.delivery_date)

    # Validate length of provided data
    hours = (end - start).in_hours()
    expected_len = hours * context.multiplier
    actual_len = len(volume_df)
    if actual_len != expected_len:
        msg = f"Invalid item count: {actual_len}. Expected {expected_len} for {context.freq} on {context.delivery_date}"
        logging.exception(msg)
        return False

    # Validate dates
    if context.freq == "1h":
        expected_dates = list(interval(start, end).range("hours", 1))[:-1]
    else:
        expected_dates = list(interval(start, end).range("minutes", 15))[:-1]

    if not (volume_df["date"] == expected_dates).all():
        msg = f"Timestamps must be exactly {context.freq} apart starting from {context.delivery_date}"
        logging.exception(msg)
        return False

    return True
