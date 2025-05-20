# ruff: noqa: PLR2004
import pytest

from app.services.streem.utils.validation_context import ValidationContext


@pytest.mark.parametrize(
    ("delivery_date", "freq", "mini", "maxi"),
    [
        ("2025-05-20", "1h", 1.0, 5.0),
        ("2025-05-20", "15min", 1.0, 5.0),
        ("2025-12-31", "1h", 0.0, 0.0),
    ],
    ids=["valid_1h", "valid_15min", "valid_zero_values"],
)
def test_valid_context(delivery_date: str, freq: str, mini: float, maxi: float) -> None:
    """Test valid ValidationContext initialization."""
    context = ValidationContext(delivery_date, freq, mini, maxi)
    assert context.delivery_date == delivery_date
    assert context.freq == freq
    assert context.mini == mini
    assert context.maxi == maxi


@pytest.mark.parametrize(
    ("freq", "expected_multiplier", "expected_min_length", "expected_max_length"),
    [
        ("1h", 1, 23, 25),
        ("15min", 4, 92, 100),
    ],
    ids=["1h_properties", "15min_properties"],
)
def test_calculated_properties(
    freq: str,
    expected_multiplier: int,
    expected_min_length: int,
    expected_max_length: int,
) -> None:
    """Test calculated properties (multiplier, min_length, max_length)."""
    context = ValidationContext(delivery_date="2025-05-20", freq=freq, mini=1.0, maxi=5.0)
    assert context.multiplier == expected_multiplier
    assert context.min_length == expected_min_length
    assert context.max_length == expected_max_length


@pytest.mark.parametrize(
    "bad_date",
    [
        "2025/05/20",
        "20-05-2025",
        "May 20, 2025",
        "20250520",
        "2025-13-01",
        "2025-00-01",
        "2025-05-32",
    ],
    ids=[
        "slash_format",
        "reversed_format",
        "text_format",
        "no_hyphen",
        "invalid_month_high",
        "invalid_month_zero",
        "invalid_day",
    ],
)
def test_invalid_date_format(bad_date: str) -> None:
    """Test invalid date formats raise appropriate ValueError."""
    with pytest.raises(ValueError, match="delivery_date must be in 'YYYY-MM-DD' format"):
        ValidationContext(delivery_date=bad_date, freq="1h", mini=1.0, maxi=5.0)


@pytest.mark.parametrize(
    "invalid_freq",
    ["30min", "hourly", "", "1H"],  # Added more invalid cases
    ids=["invalid_30min", "invalid_hourly", "empty_freq", "case_sensitive"],
)
def test_invalid_freq(invalid_freq: str) -> None:
    """Test invalid frequency values raise appropriate ValueError."""
    with pytest.raises(ValueError, match="freq must be one of '1h' or '15min'"):
        ValidationContext(delivery_date="2025-05-20", freq=invalid_freq, mini=1.0, maxi=5.0)


def test_mini_greater_than_maxi() -> None:
    """Test mini > maxi raises appropriate ValueError."""
    with pytest.raises(ValueError, match="0 <= mini <= maxi"):
        ValidationContext(delivery_date="2025-05-20", freq="1h", mini=10.0, maxi=5.0)


def test_negative_min() -> None:
    """Test negative mini raises appropriate ValueError."""
    with pytest.raises(ValueError, match="0 <= mini <= maxi"):
        ValidationContext(delivery_date="2025-05-20", freq="1h", mini=-1.0, maxi=2.0)


def test_negative_maxi() -> None:
    """Test negative maxi raises appropriate ValueError."""
    with pytest.raises(ValueError, match="0 <= mini <= maxi"):
        ValidationContext(delivery_date="2025-05-20", freq="1h", mini=0.0, maxi=-1.0)
