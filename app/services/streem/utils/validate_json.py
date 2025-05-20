import logging

from jsonschema import FormatChecker
from jsonschema import ValidationError
from jsonschema import validate

from app.services.streem.utils.validation_context import ValidationContext


JsonResponse = list[dict[str, str | float]]  #  List of dictionaries with 'date' (str) and 'data' (float) keys.


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
