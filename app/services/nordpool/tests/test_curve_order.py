import json

import jsonschema
import pytest
from jsonschema.exceptions import ValidationError

from app.services.nordpool.curve_order import Curve
from app.services.nordpool.curve_order import CurveOrder
from app.services.nordpool.curve_order import CurvePoint


# Constants for magic values
AUCTION_ID = "NPIDA_1-20181101"
PORTFOLIO = "Test Automation Auctions DK1"
AREA_CODE = "DK1"
CONTRACT_ID = "NPIDA_1-20181101-01"
PRICE_1 = -500.0
VOLUME_1 = 100.0
PRICE_2 = 3000.0
VOLUME_2 = -100.0
EXPECTED_CURVE_COUNT = 1
EXPECTED_CURVE_POINT_COUNT = 2


@pytest.fixture
def valid_curve_point_json() -> str:
    """Fixture providing a valid JSON string for a single curve point."""
    return json.dumps(
        {
            "price": PRICE_1,
            "volume": VOLUME_1,
        },
    )


@pytest.fixture
def valid_curve_json() -> str:
    """Fixture providing a valid JSON string for a single curve."""
    return json.dumps(
        {
            "contractId": CONTRACT_ID,
            "curvePoints": [
                {"price": PRICE_1, "volume": VOLUME_1},
                {"price": PRICE_2, "volume": VOLUME_2},
            ],
        },
    )


@pytest.fixture
def valid_curve_order_json() -> str:
    """Fixture providing a valid JSON string for a curve order."""
    return json.dumps(
        {
            "auctionId": AUCTION_ID,
            "portfolio": PORTFOLIO,
            "areaCode": AREA_CODE,
            "comment": "Test order",
            "curves": [
                {
                    "contractId": CONTRACT_ID,
                    "curvePoints": [
                        {"price": PRICE_1, "volume": VOLUME_1},
                        {"price": PRICE_2, "volume": VOLUME_2},
                    ],
                },
            ],
        },
    )


@pytest.fixture
def invalid_curve_order_json_missing_auction_id() -> str:
    """Fixture providing an invalid JSON string missing the 'auctionId' field."""
    return json.dumps(
        {
            "portfolio": PORTFOLIO,
            "areaCode": AREA_CODE,
            "curves": [],
        },
    )


@pytest.fixture
def invalid_curve_order_json_extra_field() -> str:
    """Fixture providing an invalid JSON string with an extra field."""
    return json.dumps(
        {
            "auctionId": AUCTION_ID,
            "portfolio": PORTFOLIO,
            "areaCode": AREA_CODE,
            "curves": [],
            "extra_field": "invalid",
        },
    )


@pytest.fixture
def invalid_curve_json_missing_contract_id() -> str:
    """Fixture providing an invalid JSON string missing the 'contractId' field."""
    return json.dumps(
        {
            "curvePoints": [
                {"price": PRICE_1, "volume": VOLUME_1},
            ],
        },
    )


@pytest.fixture
def invalid_curve_point_json_missing_price() -> str:
    """Fixture providing an invalid JSON string missing the 'price' field."""
    return json.dumps(
        {
            "volume": VOLUME_1,
        },
    )


# Tests for CurvePoint class
def test_curve_point_from_json_valid(valid_curve_point_json: str) -> None:
    """Test that a valid JSON string correctly initializes a CurvePoint."""
    data = json.loads(valid_curve_point_json)
    curve_point = CurvePoint(**data)
    assert curve_point.price == PRICE_1
    assert curve_point.volume == VOLUME_1


def test_curve_point_from_json_missing_price(invalid_curve_point_json_missing_price: str) -> None:
    """Test that missing 'price' raises a ValidationError."""
    data = json.loads(invalid_curve_point_json_missing_price)
    with pytest.raises(ValidationError, match=r".*'price' is a required property.*"):
        jsonschema.validate(instance=data, schema=CurvePoint._schema)  # noqa: SLF001


# Tests for Curve class
def test_curve_from_json_valid(valid_curve_json: str) -> None:
    """Test that a valid JSON string correctly initializes a Curve."""
    data = json.loads(valid_curve_json)
    curve = Curve(
        contract_id=data["contractId"],
        curve_points=[CurvePoint(**point) for point in data["curvePoints"]],
    )
    assert curve.contract_id == CONTRACT_ID
    assert len(curve.curve_points) == EXPECTED_CURVE_POINT_COUNT
    assert curve.curve_points[0].price == PRICE_1
    assert curve.curve_points[0].volume == VOLUME_1
    assert curve.curve_points[1].price == PRICE_2
    assert curve.curve_points[1].volume == VOLUME_2


def test_curve_from_json_missing_contract_id(invalid_curve_json_missing_contract_id: str) -> None:
    """Test that missing 'contractId' raises a ValidationError."""
    data = json.loads(invalid_curve_json_missing_contract_id)
    with pytest.raises(ValidationError, match=r".*'contractId' is a required property.*"):
        jsonschema.validate(instance=data, schema=Curve._schema)  # noqa: SLF001


# Tests for CurveOrder class
def test_curve_order_from_json_valid(valid_curve_order_json: str) -> None:
    """Test that a valid JSON string correctly initializes a CurveOrder."""
    curve_order = CurveOrder.from_json(valid_curve_order_json)
    assert curve_order.auction_id == AUCTION_ID
    assert curve_order.portfolio == PORTFOLIO
    assert curve_order.area_code == AREA_CODE
    assert curve_order.comment == "Test order"
    assert len(curve_order.curves) == EXPECTED_CURVE_COUNT
    assert curve_order.curves[0].contract_id == CONTRACT_ID
    assert len(curve_order.curves[0].curve_points) == EXPECTED_CURVE_POINT_COUNT
    assert curve_order.curves[0].curve_points[0].price == PRICE_1
    assert curve_order.curves[0].curve_points[0].volume == VOLUME_1


def test_curve_order_from_json_missing_auction_id(invalid_curve_order_json_missing_auction_id: str) -> None:
    """Test that missing 'auctionId' raises a ValidationError."""
    with pytest.raises(ValidationError, match=r".*'auctionId' is a required property.*"):
        CurveOrder.from_json(invalid_curve_order_json_missing_auction_id)


def test_curve_order_from_json_extra_field(invalid_curve_order_json_extra_field: str) -> None:
    """Test that extra fields raise a ValidationError."""
    with pytest.raises(ValidationError, match=r".*Additional properties are not allowed.*"):
        CurveOrder.from_json(invalid_curve_order_json_extra_field)


def test_curve_order_from_json_empty_curves() -> None:
    """Test that a valid JSON with empty curves list is accepted."""
    json_data = json.dumps(
        {
            "auctionId": AUCTION_ID,
            "portfolio": PORTFOLIO,
            "areaCode": AREA_CODE,
            "curves": [],
        },
    )
    curve_order = CurveOrder.from_json(json_data)
    assert len(curve_order.curves) == 0


def test_curve_order_iter_contract_ids(valid_curve_order_json: str) -> None:
    """Test that iter_contract_ids yields the correct contract IDs."""
    curve_order = CurveOrder.from_json(valid_curve_order_json)
    contract_ids = list(curve_order.iter_contract_ids())
    assert contract_ids == [CONTRACT_ID]


def test_curve_order_iter_contract_ids_empty_curves() -> None:
    """Test that iter_contract_ids yields nothing for empty curves list."""
    json_data = json.dumps(
        {
            "auctionId": AUCTION_ID,
            "portfolio": PORTFOLIO,
            "areaCode": AREA_CODE,
            "curves": [],
        },
    )
    curve_order = CurveOrder.from_json(json_data)
    contract_ids = list(curve_order.iter_contract_ids())
    assert contract_ids == []
