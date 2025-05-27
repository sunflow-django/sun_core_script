import base64
from dataclasses import FrozenInstanceError
from typing import Any

import pytest

from app.services.nordpool.constants import AUCTION_API
from app.services.nordpool.constants import BASE_URL_PROD
from app.services.nordpool.constants import BASE_URL_TEST
from app.services.nordpool.constants import CLIENT_AUCTION_API
from app.services.nordpool.constants import CLIENT_AUTHORISATION_STRING
from app.services.nordpool.constants import ENDPOINTS
from app.services.nordpool.constants import PRODUCT_ID
from app.services.nordpool.constants import TIMEOUT
from app.services.nordpool.constants import TOKEN_URL_PROD
from app.services.nordpool.constants import TOKEN_URL_TEST
from app.services.nordpool.constants import Area
from app.services.nordpool.constants import Areas


# Expected test data
EXPECTED_AREAS = {
    "UK": {"name": "Great Britain", "code": "UK", "eic_code": "10Y1001A1001A57G"},
    "50Hz": {"code": "50Hz", "name": "50Hertz Transmission GmbH", "eic_code": "10YDE-VE-------2"},
    "TBW": {"code": "TBW", "name": "TransnetBW", "eic_code": "10YDE-ENBW-----N"},
    "AMP": {"code": "AMP", "name": "Amprion", "eic_code": "10YDE-RWENET---I"},
    "TTG": {"code": "TTG", "name": "TenneT Germany", "eic_code": "10YDE-EON------1"},
    "AT": {"code": "AT", "name": "Austria", "eic_code": "10YAT-APG------L"},
    "NL": {"code": "NL", "name": "Netherlands", "eic_code": "10YNL----------L"},
    "FR": {"code": "FR", "name": "France", "eic_code": "10YFR-RTE------C"},
    "NO1": {"code": "NO1", "name": "NO1 Norway", "eic_code": "10YNO-1--------2"},
    "NO2": {"code": "NO2", "name": "NO2 Norway", "eic_code": "10YNO-2--------T"},
    "NO3": {"code": "NO3", "name": "NO3 Norway", "eic_code": "10YNO-3--------J"},
    "NO4": {"code": "NO4", "name": "NO4 Norway", "eic_code": "10YNO-4--------9"},
    "NO5": {"code": "NO5", "name": "NO5 Norway", "eic_code": "10Y1001A1001A48H"},
    "FI": {"code": "FI", "name": "Finland", "eic_code": "10YFI-1--------U"},
    "BE": {"code": "BE", "name": "Belgium", "eic_code": "10YBE----------2"},
    "DK1": {"code": "DK1", "name": "DK1 Denmark", "eic_code": "10YDK-1--------W"},
    "DK2": {"code": "DK2", "name": "DK2 Denmark", "eic_code": "10YDK-2--------M"},
    "SE1": {"code": "SE1", "name": "SE1 Sweden", "eic_code": "10Y1001A1001A44P"},
    "SE2": {"code": "SE2", "name": "SE2 Sweden", "eic_code": "10Y1001A1001A45N"},
    "SE3": {"code": "SE3", "name": "SE3 Sweden", "eic_code": "10Y1001A1001A46L"},
    "SE4": {"code": "SE4", "name": "SE4 Sweden", "eic_code": "10Y1001A1001A47J"},
    "EE": {"code": "EE", "name": "Estonia", "eic_code": "10Y1001A1001A39I"},
    "LV": {"code": "LV", "name": "Latvia", "eic_code": "10YLV-1001A00074"},
    "LT": {"code": "LT", "name": "Lithuania", "eic_code": "10YLT-1001A0008Q"},
    "PL": {"code": "PL", "name": "Poland", "eic_code": "10YPL-AREA-----S"},
}


@pytest.fixture
def areas() -> Areas:
    """Fixture to create an Areas instance for testing."""
    return Areas()


@pytest.fixture
def sample_area() -> Area:
    """Fixture to create a sample Area instance for testing."""
    return Area(name="Test Area", code="TEST", eic_code="10YTEST-------X")


def test_urls() -> None:
    """Test URL constants are correctly defined."""
    assert BASE_URL_TEST == "https://auctions-api.test.nordpoolgroup.com"
    assert TOKEN_URL_TEST == "https://sts.test.nordpoolgroup.com/connect/token"
    assert BASE_URL_PROD == "https://auctions-api.nordpoolgroup.com"
    assert TOKEN_URL_PROD == "https://sts.nordpoolgroup.com/connect/token"


def test_endpoints() -> None:
    """Test ENDPOINTS dictionary contains expected keys and values."""
    expected_keys = {
        "auctions",
        "orders",
        "trades",
        "prices",
        "portfolio_volumes",
        "auction",
        "block_order",
        "block_orders",
        "curve_order",
        "curve_orders",
        "reasonability_result",
        "state",
    }
    assert set(ENDPOINTS.keys()) == expected_keys
    assert ENDPOINTS["auctions"] == "/api/v{version}/auctions"
    assert ENDPOINTS["reasonability_result"] == "/api/v{version}/auctions/{externalAuctionId}/orders/{orderId}/results"


def test_timeout() -> None:
    """Test TIMEOUT constant is correctly defined."""
    assert TIMEOUT == 3  # noqa: PLR2004


def test_api_constants() -> None:
    """Test API-related constants are correctly defined."""
    assert AUCTION_API == "auction_api"
    assert CLIENT_AUCTION_API == "client_auction_api"
    # Y2xpZW50X2F1Y3Rpb25fYXBpOmNsaWVudF9hdWN0aW9uX2FwaQ==
    assert (
        base64.b64encode(
            f"{CLIENT_AUCTION_API}:{CLIENT_AUCTION_API}".encode(),
        ).decode()
        == CLIENT_AUTHORISATION_STRING
    )
    assert PRODUCT_ID == "CORE_IDA_1"


@pytest.mark.parametrize(
    ("key", "expected_name", "expected_code", "expected_eic"),
    [(key, data["name"], data["code"], data["eic_code"]) for key, data in EXPECTED_AREAS.items()],
)
def test_get_area_valid_key(
    areas: Areas,
    key: str,
    expected_name: str,
    expected_code: str,
    expected_eic: str,
) -> None:
    """Test retrieving areas with valid keys."""
    area = areas.get_area(key)
    assert area is not None
    assert area.name == expected_name
    assert area.code == expected_code
    assert area.eic_code == expected_eic


@pytest.mark.parametrize(
    "key",
    [
        "INVALID",
        "",
        " ",
        "uk",  # Lowercase
        "Uk",  # Mixed case
        None,  # Non-string
    ],
)
def test_get_area_invalid_key(areas: Areas, key: Any) -> None:  # noqa: ANN401
    """Test retrieving areas with invalid or edge-case keys."""
    area = areas.get_area(key)
    assert area is None


def test_all_areas_content(areas: Areas) -> None:
    """Test that all_areas returns a dictionary with expected areas."""
    all_areas = areas.all_areas()
    assert isinstance(all_areas, dict)
    assert len(all_areas) == len(EXPECTED_AREAS)
    for key, expected in EXPECTED_AREAS.items():
        assert key in all_areas
        area = all_areas[key]
        assert isinstance(area, Area)
        assert area.name == expected["name"]
        assert area.code == expected["code"]
        assert area.eic_code == expected["eic_code"]


def test_all_areas_deep_copy(areas: Areas) -> None:
    """Test that all_areas returns a deep copy of the areas dictionary."""
    all_areas = areas.all_areas()
    all_areas["UK"] = Area(name="Invalid", code="INV", eic_code="10YINVALID----X")
    assert areas["UK"].name == "Great Britain"  # Original unchanged
    assert areas["UK"] != all_areas["UK"]  # Copy modified


@pytest.mark.parametrize(
    ("key", "expected_name", "expected_code", "expected_eic"),
    [(key, data["name"], data["code"], data["eic_code"]) for key, data in EXPECTED_AREAS.items()],
)
def test_getitem_valid_key(
    areas: Areas,
    key: str,
    expected_name: str,
    expected_code: str,
    expected_eic: str,
) -> None:
    """Test dictionary-like access with valid keys."""
    area = areas[key]
    assert area.name == expected_name
    assert area.code == expected_code
    assert area.eic_code == expected_eic


@pytest.mark.parametrize(
    "key",
    [
        "INVALID",
        "",
        " ",
        "uk",  # Lowercase
        "Uk",  # Mixed case
        None,  # Non-string
    ],
)
def test_getitem_invalid_key(areas: Areas, key: Any) -> None:  # noqa: ANN401
    """Test dictionary-like access with invalid keys raises KeyError."""
    with pytest.raises(KeyError) as exc_info:
        _ = areas[key]
    expected_msg = f"Area with key '{key}' not found" if key is not None else "Area with key 'None' not found"
    assert str(exc_info.value) == f'"{expected_msg}"'


def test_area_dataclass_attributes(sample_area: Area) -> None:
    """Test that Area dataclass attributes are correctly set."""
    assert sample_area.name == "Test Area"
    assert sample_area.code == "TEST"
    assert sample_area.eic_code == "10YTEST-------X"


def test_area_immutability(sample_area: Area) -> None:
    """Test that Area dataclass attributes cannot be modified after creation."""
    with pytest.raises(FrozenInstanceError):
        sample_area.name = "Modified Area"


def test_area_equality(sample_area: Area) -> None:
    """Test equality and hashability of Area instances."""
    same_area = Area(name="Test Area", code="TEST", eic_code="10YTEST-------X")
    different_area = Area(name="Different", code="DIFF", eic_code="10YDIFF-------Y")
    assert sample_area == same_area
    assert sample_area != different_area
    assert hash(sample_area) == hash(same_area)
    assert hash(sample_area) != hash(different_area)


def test_areas_iteration(areas: Areas) -> None:
    """Test that Areas can be iterated over like a dictionary."""
    keys = list(areas)
    assert set(keys) == set(EXPECTED_AREAS.keys())
    assert len(keys) == len(EXPECTED_AREAS)


def test_areas_empty(subclass_areas: Areas) -> None:
    """Test Areas behavior with an empty areas dictionary."""
    assert subclass_areas.get_area("UK") is None
    assert subclass_areas.all_areas() == {}
    with pytest.raises(KeyError):
        _ = subclass_areas["UK"]
    assert list(subclass_areas) == []


def test_areas_case_sensitivity(areas: Areas) -> None:
    """Test that area keys are case-sensitive."""
    assert areas.get_area("uk") is None
    assert areas.get_area("Uk") is None
    assert areas.get_area("UK") is not None
    with pytest.raises(KeyError):
        _ = areas["uk"]


@pytest.fixture
def subclass_areas() -> Areas:
    """Fixture to create an Areas subclass with an empty areas dictionary."""

    class EmptyAreas(Areas):
        def __init__(self) -> None:
            self._areas: dict[str, Area] = {}

    return EmptyAreas()
