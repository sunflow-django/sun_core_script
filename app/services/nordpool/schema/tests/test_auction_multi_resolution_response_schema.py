from datetime import datetime

import pytest
from pydantic import ValidationError

from app.services.nordpool.schema.auction_multi_resolution_response_schema import AuctionMultiResolutionResponse
from app.services.nordpool.schema.base_schema import AuctionStateType


@pytest.mark.parametrize(
    ("data", "expected_id", "expected_state"),
    [
        (
            {
                "id": "auction1",
                "name": "Test Auction",
                "state": "Open",
                "closeForBidding": "2023-01-01T00:00:00",
                "deliveryStart": "2023-01-02T00:00:00",
                "deliveryEnd": "2023-01-03T00:00:00",
            },
            "auction1",
            AuctionStateType.OPEN,
        ),
        (
            {
                "id": None,
                "name": None,
                "state": "Closed",
                "closeForBidding": "2023-01-01T00:00:00",
                "deliveryStart": "2023-01-02T00:00:00",
                "deliveryEnd": "2023-01-03T00:00:00",
            },
            None,
            AuctionStateType.CLOSED,
        ),
    ],
)
def test_auction_multi_resolution_response_validation(
    data: dict,
    expected_id: str | None,
    expected_state: AuctionStateType,
) -> None:
    """Test AuctionMultiResolutionResponse model validation."""
    auction = AuctionMultiResolutionResponse(**data)
    assert auction.id == expected_id
    assert auction.name == data.get("name")
    assert auction.state == expected_state
    assert auction.close_for_bidding == datetime(2023, 1, 1)  # noqa: DTZ001
    assert auction.delivery_start == datetime(2023, 1, 2)  # noqa: DTZ001
    assert auction.delivery_end == datetime(2023, 1, 3)  # noqa: DTZ001


def test_auction_multi_resolution_response_with_nested_fields() -> None:
    """Test AuctionMultiResolutionResponse with nested fields."""
    data = {
        "id": "auction1",
        "name": "Test Auction",
        "state": "Open",
        "closeForBidding": "2023-01-01T00:00:00",
        "deliveryStart": "2023-01-02T00:00:00",
        "deliveryEnd": "2023-01-03T00:00:00",
        "availableOrderTypes": [{"id": 1, "name": "Curve"}],
        "currencies": [{"currencyCode": "EUR", "minPrice": 0.0, "maxPrice": 100.0}],
        "contracts": [
            {
                "areaCode": "DK1",
                "contracts": [
                    {
                        "id": "contract1",
                        "deliveryStart": "2023-01-02T00:00:00",
                        "deliveryEnd": "2023-01-03T00:00:00",
                    },
                ],
            },
        ],
        "portfolios": [
            {
                "name": "Portfolio1",
                "id": "p1",
                "currency": "EUR",
                "companyId": "c1",
                "companyName": "Company1",
                "permission": "read",
                "areas": [
                    {
                        "code": "DK1",
                        "name": "Denmark 1",
                        "eicCode": "EIC1",
                        "curveMinVolumeLimit": 0.0,
                        "curveMaxVolumeLimit": 1000.0,
                        "auctionTradingResolution": 3600,
                    },
                ],
            },
        ],
    }
    auction = AuctionMultiResolutionResponse(**data)
    assert auction.id == "auction1"
    assert len(auction.available_order_types) == 1
    assert auction.available_order_types[0].id == 1
    assert len(auction.currencies) == 1
    assert auction.currencies[0].currency_code == "EUR"
    assert len(auction.contracts) == 1
    assert auction.contracts[0].area_code == "DK1"
    assert len(auction.portfolios) == 1
    assert auction.portfolios[0].name == "Portfolio1"


def test_auction_multi_resolution_response_invalid_state() -> None:
    """Test AuctionMultiResolutionResponse with invalid state."""
    data = {
        "id": "auction1",
        "name": "Test Auction",
        "state": "InvalidState",
        "closeForBidding": "2023-01-01T00:00:00",
        "deliveryStart": "2023-01-02T00:00:00",
        "deliveryEnd": "2023-01-03T00:00:00",
    }
    with pytest.raises(ValidationError):
        AuctionMultiResolutionResponse(**data)
