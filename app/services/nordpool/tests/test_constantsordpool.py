import pytest

from app.services.nordpool.constants import PRODUCT_ID
from app.services.nordpool.constants import Area
from app.services.nordpool.constants import Areas


def test_product_id() -> None:
    assert PRODUCT_ID == "CORE_IDA_1"

@pytest.fixture
def areas() -> Areas:
    """Fixture to create an Areas instance for testing."""
    return Areas()


def test_get_area_valid_key(areas: Areas) -> None:
    """Test retrieving an area with a valid key."""
    area = areas.get_area("UK")
    assert area is not None
    assert area.name == "Great Britain"
    assert area.code == "UK"
    assert area.eic_code == "10Y1001A1001A57G"


def test_get_area_invalid_key(areas: Areas) -> None:
    """Test retrieving an area with an invalid key."""
    area = areas.get_area("INVALID")
    assert area is None


def test_all_areas(areas: Areas) -> None:
    """Test retrieving all areas."""
    all_areas = areas.all_areas()
    assert isinstance(all_areas, dict)
    assert len(all_areas) == 25  # noqa: PLR2004
    assert "UK" in all_areas
    assert "FI" in all_areas
    assert all(isinstance(area, Area) for area in all_areas.values())


def test_getitem_valid_key(areas: Areas) -> None:
    """Test dictionary-like access with a valid key."""
    area = areas["NO1"]
    assert area.name == "NO1 Norway"
    assert area.code == "NO1"
    assert area.eic_code == "10YNO-1--------2"


def test_getitem_invalid_key(areas: Areas) -> None:
    """Test dictionary-like access with an invalid key raises KeyError."""
    with pytest.raises(KeyError) as exc_info:
        _ = areas["INVALID"]
    error_message = "\"Area with key 'INVALID' not found\""
    assert str(exc_info.value) == error_message


def test_area_dataclass_attributes() -> None:
    """Test Area dataclass attributes."""
    area = Area(name="Test Area", code="TEST", eic_code="10YTEST-------X")
    assert area.name == "Test Area"
    assert area.code == "TEST"
    assert area.eic_code == "10YTEST-------X"
