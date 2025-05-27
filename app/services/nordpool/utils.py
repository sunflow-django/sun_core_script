import re
from datetime import datetime
from datetime import timedelta
from uuid import UUID

from app.constants.time_zones import PARIS_TZ


def extract_uuid(text: str) -> UUID | None:
    """
    Extract a UUID from a string.

    Returns:
        The UUID if found as an isolated token, otherwise None.
    """
    uuid_pattern = r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b"
    match = re.search(uuid_pattern, text, re.IGNORECASE)
    if match:
        return UUID(match.group(0))
    return None


def does_order_exist(text: str) -> bool:
    """
    Check if the string contains both 'Order with id' and 'already exists'.

    Return
        True if both phrases are present, False otherwise.
    """
    return "already exists" in text and "Order with id" in text



def tomorrow_str() -> str:
    """Returns tomorrow (Paris time) as a str (YYYYMMDD)."""
    tomorrow = datetime.now(tz=PARIS_TZ) + timedelta(days=1)
    return tomorrow.strftime("%Y%m%d")


def tomorrow_date() -> datetime:
    """Returns tomorrow (Paris time) as a datetime."""
    tomorrow = datetime.now(tz=PARIS_TZ) + timedelta(days=1)
    return tomorrow.date()
