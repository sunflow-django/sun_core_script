from typing import Any

import pendulum
import pytest
from _pytest.monkeypatch import MonkeyPatch
from pendulum import DateTime

from app.constants.time_zones import PARIS_TZ
from app.services.streem.utils.day_boundaries import day_boundaries


@pytest.mark.parametrize(
    ("date", "expected_start", "expected_end", "expected_hours"),
    [
        (
            "2025-05-20",
            pendulum.datetime(2025, 5, 20, 0, 0, 0, tz=PARIS_TZ),
            pendulum.datetime(2025, 5, 21, 0, 0, 0, tz=PARIS_TZ),
            24,
        ),
        (
            "2024-01-01",
            pendulum.datetime(2024, 1, 1, 0, 0, 0, tz=PARIS_TZ),
            pendulum.datetime(2024, 1, 2, 0, 0, 0, tz=PARIS_TZ),
            24,
        ),
        (
            "2024-02-29",
            pendulum.datetime(2024, 2, 29, 0, 0, 0, tz=PARIS_TZ),
            pendulum.datetime(2024, 3, 1, 0, 0, 0, tz=PARIS_TZ),
            24,
        ),
    ],
    ids=["normal_day", "new_year", "leap_year"],
)
def test_normal_days(date: str, expected_start: DateTime, expected_end: DateTime, expected_hours: int) -> None:
    """Test normal days with 24-hour duration."""

    start, end = day_boundaries(date)

    assert isinstance(start, DateTime)
    assert isinstance(end, DateTime)
    assert start == expected_start
    assert end == expected_end
    assert (end - start).total_hours() == expected_hours
    assert start.timezone_name == "Europe/Paris"
    assert end.timezone_name == "Europe/Paris"


@pytest.mark.parametrize(
    ("date", "expected_start", "expected_end", "expected_hours"),
    [
        (
            "2025-03-30",  # DST start: March 30, 2 AM to 3 AM
            pendulum.datetime(2025, 3, 30, 0, 0, 0, tz=PARIS_TZ),
            pendulum.datetime(2025, 3, 31, 0, 0, 0, tz=PARIS_TZ),
            23,
        ),
        (
            "2025-10-26",  # DST end: October 26, 3 AM to 2 AM
            pendulum.datetime(2025, 10, 26, 0, 0, 0, tz=PARIS_TZ),
            pendulum.datetime(2025, 10, 27, 0, 0, 0, tz=PARIS_TZ),
            25,
        ),
    ],
    ids=["dst_start_2025", "dst_end_2025"],
)
def test_dst_transitions(date: str, expected_start: DateTime, expected_end: DateTime, expected_hours: int) -> None:
    """Test DST transition days with 23 or 25 hours."""
    start, end = day_boundaries(date)
    assert isinstance(start, DateTime)
    assert isinstance(end, DateTime)
    assert start == expected_start
    assert end == expected_end
    assert (end - start).total_hours() == expected_hours
    assert start.timezone_name == "Europe/Paris"
    assert end.timezone_name == "Europe/Paris"


@pytest.mark.parametrize(
    "date",
    [
        "2025-5-20",  # Missing leading zeros
        "2025/05/20",  # Wrong separator
        "2025-05-20T00:00",  # Includes time
        "25-05-20",  # Wrong year format
        "invalid",  # Non-date string
        "",  # Empty string
        "2025-05",  # Incomplete date
        "2025-05-20-01",  # Extra component
    ],
    ids=[
        "missing_zeros",
        "wrong_separator",
        "with_time",
        "short_year",
        "non_date",
        "empty",
        "incomplete",
        "extra_component",
    ],
)
def test_invalid_date_format(date: str) -> None:
    """Test invalid date formats."""
    with pytest.raises(ValueError, match=f"Invalid date format: '{date}'. Expected YYYY-MM-DD") as exc_info:
        day_boundaries(date)
    assert str(exc_info.value) == f"Invalid date format: '{date}'. Expected YYYY-MM-DD"


@pytest.mark.parametrize(
    "date",
    [
        "2025-04-31",  # April has 30 days
        "2025-02-29",  # 2025 is not a leap year
        "2025-00-01",  # Invalid month
        "2025-01-00",  # Invalid day
        "2025-13-01",  # Invalid month
        "0000-01-01",  # Year out of valid range
    ],
    ids=["invalid_day", "non_leap_feb29", "zero_month", "zero_day", "invalid_month", "zero_year"],
)
def test_invalid_date(date: str) -> None:
    """Test invalid or non-existent dates."""
    with pytest.raises(ValueError, match=f"Invalid date: '{date}'") as exc_info:
        day_boundaries(date)
    assert str(exc_info.value) == f"Invalid date: '{date}'"


@pytest.mark.parametrize(
    ("date", "expected_start", "expected_end", "expected_hours"),
    [
        (
            "9999-12-30",
            pendulum.datetime(9999, 12, 30, 0, 0, 0, tz=PARIS_TZ),
            pendulum.datetime(9999, 12, 31, 0, 0, 0, tz=PARIS_TZ),
            24,
        ),
        (
            "1900-01-01",
            pendulum.datetime(1900, 1, 1, 0, 0, 0, tz=PARIS_TZ),
            pendulum.datetime(1900, 1, 2, 0, 0, 0, tz=PARIS_TZ),
            24,
        ),
    ],
    ids=["far_future", "early_date"],
)
def test_edge_cases(date: str, expected_start: DateTime, expected_end: DateTime, expected_hours: int) -> None:
    """Test extreme but valid dates."""
    start, end = day_boundaries(date)
    assert isinstance(start, DateTime)
    assert isinstance(end, DateTime)
    assert start == expected_start
    assert end == expected_end
    assert (end - start).total_hours() == expected_hours
    assert start.timezone_name == "Europe/Paris"
    assert end.timezone_name == "Europe/Paris"


def test_non_datetime_parse(monkeypatch: MonkeyPatch) -> None:
    """Test case where pendulum.parse returns a non-DateTime object."""

    def mock_parse(*args: Any, **kwargs: Any) -> pendulum.Date:  # noqa: ANN401
        return pendulum.Date(2025, 5, 20)

    monkeypatch.setattr(pendulum, "parse", mock_parse)
    with pytest.raises(TypeError, match="Not able to parse: '2025-05-20' as date") as exc_info:
        day_boundaries("2025-05-20")
    assert str(exc_info.value) == "Not able to parse: '2025-05-20' as date"
