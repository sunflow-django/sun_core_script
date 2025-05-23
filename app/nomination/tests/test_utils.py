from datetime import datetime
from datetime import timedelta

import pytest
from freezegun import freeze_time

from app.constants.time_zones import PARIS_TZ
from app.nomination.utils import tomorrow_boundaries
from app.nomination.utils import tomorrow_iso
from app.nomination.utils import tomorrow_str_dash
from app.nomination.utils import tomorrow_str_no_dash


@pytest.fixture
def fixed_time() -> datetime:
    """Fixture to set a fixed time for all tests."""
    return datetime(2025, 5, 20, 14, 30, tzinfo=PARIS_TZ)


def test_tomorrow_boundaries(fixed_time: datetime) -> None:
    with freeze_time(fixed_time):
        tomorrow_start, tomorrow_end = tomorrow_boundaries()

        expected_start = datetime(2025, 5, 21, 0, 0, 0, 0, tzinfo=PARIS_TZ)
        expected_end = datetime(2025, 5, 22, 0, 0, 0, 0, tzinfo=PARIS_TZ)

        assert tomorrow_start == expected_start
        assert tomorrow_end == expected_end
        assert tomorrow_start.tzinfo == PARIS_TZ
        assert tomorrow_end.tzinfo == PARIS_TZ

        # Verify half-open interval [start, end)
        assert expected_start <= tomorrow_start < tomorrow_end
        assert tomorrow_end == expected_start + timedelta(days=1)


def test_tomorrow_iso(fixed_time: datetime) -> None:
    with freeze_time(fixed_time):
        result = tomorrow_iso()

        expected_start = datetime(2025, 5, 21, 0, 0, 0, 0, tzinfo=PARIS_TZ)
        expected_iso = expected_start.isoformat()

        assert result == expected_iso
        assert "2025-05-21T00:00:00" in result
        assert result.endswith("+02:00")  # Paris TZ offset


def test_tomorrow_str_dash(fixed_time: datetime) -> None:
    with freeze_time(fixed_time):
        result = tomorrow_str_dash()

        expected_date = "2025-05-21"
        assert result == expected_date


def test_tomorrow_str_no_dash(fixed_time: datetime) -> None:
    with freeze_time(fixed_time):
        result = tomorrow_str_no_dash()

        expected_date = "20250521"
        assert result == expected_date
