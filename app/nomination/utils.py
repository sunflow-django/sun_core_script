from datetime import datetime
from datetime import timedelta

from app.constants.time_zones import PARIS_TZ


def tomorrow_boundaries() -> tuple[datetime, datetime]:
    """
    Returns the [start, end) boundaries for tomorrow in Paris time.
    End is exclusive (00:00 of the day after tomorrow).
    """
    tomorrow_start = datetime.now(tz=PARIS_TZ).replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    tomorrow_end = tomorrow_start + timedelta(days=1)
    return tomorrow_start, tomorrow_end


def tomorrow_iso() -> str:
    """
    Returns tomorrow start of day as an ISO string, in Paris time

    Example: "2025-05-24T00:00:00+02:00"
    """
    tomorrow = datetime.now(tz=PARIS_TZ) + timedelta(days=1)
    tomorrow_start = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)
    return tomorrow_start.isoformat()


def tomorrow_str_dash() -> str:
    """
    Returns tomorrow's date as 'YYYY-MM-DD' string, in Paris time.

    Example: "2025-05-24"
    """
    tomorrow = datetime.now(tz=PARIS_TZ) + timedelta(days=1)
    return tomorrow.strftime("%Y-%m-%d")


def tomorrow_str_no_dash() -> str:
    """
    Returns tomorrow's date as 'YYYYMMDD' string, in Paris time.

    Example: "20250524"
    """
    tomorrow = datetime.now(tz=PARIS_TZ) + timedelta(days=1)
    return tomorrow.strftime("%Y%m%d")
