import pendulum
import pytest
from _pytest.monkeypatch import MonkeyPatch

from app.services.streem.utils.hours_in_day import hours_in_day


@pytest.mark.parametrize(
    ("date", "expected_hours"),
    [
        ("2025-05-20", 24),
        ("2024-01-01", 24),
        ("2025-12-25", 24),
        ("2024-02-29", 24),
    ],
    ids=["normal_day", "new_year", "christmas", "leap_year"],
)
def test_normal_days(date: str, expected_hours: str) -> None:
    """Test normal days with 24 hours."""
    assert hours_in_day(date) == expected_hours


@pytest.mark.parametrize(
    ("date", "expected_hours"),
    [
        ("2025-03-30", 23),  # DST start 2025: March 30, 2 AM to 3 AM
        ("2024-03-31", 23),  # DST start 2024: March 31
        ("2025-10-26", 25),  # DST end 2025: October 26, 3 AM to 2 AM
        ("2024-10-27", 25),  # DST end 2024: October 27
    ],
    ids=["dst_start_2025", "dst_start_2024", "dst_end_2025", "dst_end_2024"],
)
def test_dst_transitions(date: str, expected_hours: str) -> None:
    """Test DST transition days (23 or 25 hours)."""
    assert hours_in_day(date) == expected_hours


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
    with pytest.raises(ValueError, match=r"Invalid date format: '.*'\. Expected YYYY-MM-DD"):
        hours_in_day(date)


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
    with pytest.raises(ValueError, match=r"Invalid date: '.*'"):
        hours_in_day(date)


@pytest.mark.parametrize(
    ("date", "expected_hours"),
    [
        ("9999-12-30", 24),  # Far future. Overfolw with 9999-12-30
        ("1900-01-01", 24),  # Early date
        ("2024-12-31", 24),  # Year boundary (end)
        ("2025-01-01", 24),  # Year boundary (start)
    ],
    ids=["far_future", "early_date", "year_end", "year_start"],
)
def test_edge_cases(date: str, expected_hours: str) -> None:
    """Test extreme but valid dates and year boundaries."""
    assert hours_in_day(date) == expected_hours


def test_non_datetime_parse(monkeypatch:MonkeyPatch) -> None: 
    """Test case where pendulum.parse returns a non-DateTime object."""

    def mock_parse(*args, **kwargs) -> None:  # noqa: ANN002, ANN003
        return "not a datetime"

    monkeypatch.setattr(pendulum, "parse", mock_parse)
    with pytest.raises(TypeError, match=r"Not able to parse: '2025-05-20' as date"):
        hours_in_day("2025-05-20")
