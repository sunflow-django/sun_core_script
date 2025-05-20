import logging

from jsonschema import FormatChecker
from jsonschema import ValidationError
from jsonschema import validate
from pendulum import DateTime
from pendulum import interval
from pendulum import parse

from app.constants.time_zones import PARIS_TZ
from app.services.streem.utils.day_boundaries import day_boundaries
from app.services.streem.utils.validation_context import ValidationContext


JsonResponse = list[dict[str, str | float]]  # List of dictionaries with 'date' (str) and 'data' (float) keys.


def _validate_schema(json_data: JsonResponse, context: ValidationContext) -> bool:
    """
    Validate the structure of JSON-like data (list).

    Checks:
    - The list has the expected number of items based on freq and day length.
    - Each item has exactly two keys: 'date' and 'data'.
    - 'date' is a valid ISO 8601 date-time.
    - 'data' is a float between mini and maxi (inclusive).

    Args:
        json_data: List of dictionaries with 'date' and 'data' keys.
        context: The validation context that provies mini, maxi, freq etc.

    Returns:
        bool: True if validation succeeds, False if it fails.
    """

    schema = {
        "type": "array",
        "minItems": context.min_length,
        "maxItems": context.max_length,
        "items": {
            "type": "object",
            "properties": {
                "date": {"type": "string", "format": "date-time"},
                "data": {"type": "number", "minimum": context.mini, "maximum": context.maxi},
            },
            "required": ["date", "data"],
            "additionalProperties": False,
        },
    }

    try:
        validate(instance=json_data, schema=schema, format_checker=FormatChecker())
    except ValidationError as e:
        msg = f"Schema validation failed: {e.message}"
        logging.exception(msg)
        return False
    return True


def _validate_dates(json_data: JsonResponse, context: ValidationContext) -> bool:
    """
    Validate the time series aspects of JSON data.

    Checks:
    - Number of items matches expected count based on freq and day length.
    - Dates form the exact time series for the given day.

    Args:
        json_data: List of dictionaries with 'date' (ISO 8601 string) and 'data' keys.
        context: The validation context that provies mini, maxi, freq etc.

    Returns:
        bool: True if the dates and item count are valid, False otherwise.
    """
    start, end = day_boundaries(context.delivery_date)

    # Validate length
    hours = (end - start).in_hours()
    expected_len = hours * context.multiplier
    actual_len = len(json_data)
    if actual_len != expected_len:
        msg = f"Invalid item count: {actual_len}. Expected {expected_len} for {context.freq} on {context.delivery_date}"
        logging.exception(msg)
        return False

    # Validate dates
    if context.freq == "1h":
        expected_dates = [dt.isoformat() for dt in interval(start, end).range("hours", 1)][:-1]
    else:
        expected_dates = [dt.isoformat() for dt in interval(start, end).range("minutes", 15)][:-1]

    actual_dates = []
    for i, item in enumerate(json_data):
        try:
            dt = parse(item["date"], tz=PARIS_TZ, strict=True)
            if not isinstance(dt, DateTime):
                msg = f"Invalid date at item {i}: {item['date']}"
                logging.exception(msg)
                return False
            actual_dates.append(item["date"])
        except (ValueError, KeyError):
            msg = f"Invalid date at item {i}: {item.get('date', 'missing')}"
            logging.exception(msg)
            return False

    return actual_dates == expected_dates


def validate_json(json_data: JsonResponse, context: ValidationContext) -> bool:
    """
    Validate JSON data against a ValidationContext by combining structure and date checks.

    Args:
        json_data: List of dictionaries with 'date' and 'data' keys.
        context: ValidationContext instance with delivery_date, freq, mini, and maxi.

    Returns:
        bool: True if json_data is validated, False otherwise.
    """
    schema_test = _validate_schema(json_data, context)
    dates_test = _validate_dates(json_data, context)
    return schema_test and dates_test
