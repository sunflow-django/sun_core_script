# ruff: noqa: PLR2004
import pytest

from app.services.streem.utils.validation_context import ValidationContext


@pytest.mark.parametrize(
    ("delivery_date", "freq", "mini", "maxi"),
    [("2025-05-20", "1h", 1.0, 5.0), ("2025-05-20", "15min", 1.0, 5.0)],
    ids=[
        "valide_1h",
        "valide_15min",
    ],
)
def test_valid_context(delivery_date: str, freq: str, mini: str, maxi: str) -> None:
    context = ValidationContext(delivery_date, freq, mini, maxi)
    assert context.delivery_date == delivery_date
    assert context.freq == freq
    assert context.mini == mini
    assert context.maxi == maxi


@pytest.mark.parametrize("bad_date", ["2025/05/20", "20-05-2025", "May 20, 2025", "20250520"])
def test_invalid_date_format(bad_date: str) -> None:
    with pytest.raises(ValueError, match="delivery_date must be in 'YYYY-MM-DD' format"):
        ValidationContext(delivery_date=bad_date, freq="1h", mini=1.0, maxi=5.0)


def test_invalid_freq() -> None:
    with pytest.raises(ValueError, match="freq must be one of '1h' or '15min'"):
        ValidationContext(delivery_date="2025-05-20", freq="invalide_freq", mini=1.0, maxi=5.0)


def test_mini_greater_than_maxi() -> None:
    with pytest.raises(ValueError, match="0 <= mini <= maxi"):
        ValidationContext(delivery_date="2025-05-20", freq="1h", mini=10.0, maxi=5.0)


def test_negative_min() -> None:
    with pytest.raises(ValueError, match="0 <= mini <= maxi"):
        ValidationContext(delivery_date="2025-05-20", freq="1h", mini=-1.0, maxi=2.0)
