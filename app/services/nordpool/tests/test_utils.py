from collections.abc import Iterator
from datetime import date
from datetime import datetime
from unittest.mock import Mock
from unittest.mock import patch
from uuid import UUID
from zoneinfo import ZoneInfo

import pytest

from app.services.nordpool.utils import does_order_exist
from app.services.nordpool.utils import extract_uuid
from app.services.nordpool.utils import tomorrow_date
from app.services.nordpool.utils import tomorrow_str


# Constants for test data
TEST_UUID = UUID("123e4567-e89b-12d3-a456-426614174000")
TEST_UUID_STR = "123e4567-e89b-12d3-a456-426614174000"
PARIS_TZ = ZoneInfo("Europe/Paris")
TEST_DATE = datetime(2023, 1, 1, 12, 0, tzinfo=PARIS_TZ)


@pytest.fixture
def mock_paris_tz() -> Iterator[None]:
    """Fixture to mock PARIS_TZ."""
    with patch("app.services.nordpool.utils.PARIS_TZ", PARIS_TZ):
        yield


@pytest.fixture
def mock_datetime_now() -> Iterator[None]:
    """Fixture to mock datetime.now to return a fixed date."""
    with patch("app.services.nordpool.utils.datetime") as mock_datetime:
        mock_datetime.now.return_value = TEST_DATE
        mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs, tzinfo=PARIS_TZ)
        yield mock_datetime


@pytest.mark.parametrize(
    ("text", "expected_uuid"),
    [
        (TEST_UUID_STR, TEST_UUID),
        (f"Order with id {TEST_UUID_STR} found", TEST_UUID),
        ("no uuid here", None),
        ("", None),
        ("123e4567-e89b-12d3-a456-42661417400", None),  # Partial UUID
        ("123e4567-e89b-12d3-a456-4266141740000", None),  # Too long
        ("GGGG4567-e89b-12d3-a456-426614174000", None),  # Invalid characters
        (f"{TEST_UUID_STR.upper()}", TEST_UUID),  # Case insensitivity
        (f"{TEST_UUID_STR} extra", TEST_UUID),  # UUID with trailing word
        (f"prefix {TEST_UUID_STR}", TEST_UUID),  # UUID with prefix
        (f"{TEST_UUID_STR}extra", None),  # UUID with appended characters
        (f"{TEST_UUID_STR}0", None),  # UUID with single extra character
    ],
)
def test_extract_uuid(text: str, expected_uuid: UUID | None) -> None:
    """Test extract_uuid function for various input strings."""
    result = extract_uuid(text)
    assert result == expected_uuid


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Error: Order with id 123 already exists in the system.", True),
        ("Error: 123 already exists in the system.", False),
        ("Order with id 123 was just created successfully.", False),
        ("No relevant message here.", False),
        ("order with id 123 already exists", False),  # case sensitivity
        ("System message: Order with id 456 has failed because it already exists.", True),
    ],
)
def test_does_order_exist(text: str, *, expected: bool) -> None:
    assert does_order_exist(text) == expected


def test_tomorrow_str(mock_paris_tz: Mock, mock_datetime_now: Mock) -> None:
    """Test tomorrow_str function returns correct date string."""
    result = tomorrow_str()
    expected = "20230102"  # January 2, 2023
    assert result == expected


def test_tomorrow_date(mock_paris_tz: Mock, mock_datetime_now: Mock) -> None:
    """Test tomorrow_date function returns correct date object."""
    result = tomorrow_date()
    expected = date(2023, 1, 2)
    assert result == expected


def test_tomorrow_str_timezone_handling(mock_datetime_now: Mock) -> None:
    """Test tomorrow_str with a different timezone."""
    with patch("app.services.nordpool.utils.PARIS_TZ", ZoneInfo("UTC")):
        result = tomorrow_str()
        expected = "20230102"  # Same date, as UTC is same day
        assert result == expected


def test_tomorrow_date_day_rollover(mock_paris_tz: Mock) -> None:
    """Test tomorrow_date handles day rollover correctly."""
    mock_date = datetime(2023, 12, 31, 23, 59, tzinfo=PARIS_TZ)
    with patch("app.services.nordpool.utils.datetime") as mock_datetime:
        mock_datetime.now.return_value = mock_date
        mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs, tzinfo=PARIS_TZ)
        result = tomorrow_date()
        expected = date(2024, 1, 1)
        assert result == expected
