from datetime import datetime

from app.services.nordpool.schema.auction_price_schema import AuctionPrice
from app.services.nordpool.schema.base_schema import AuctionResultState


def test_auction_price_validation() -> None:
    """Test AuctionPrice model validation."""
    data = {
        "auction": "auction1",
        "auctionDeliveryStart": "2023-01-01T00:00:00",
        "auctionDeliveryEnd": "2023-01-02T00:00:00",
        "contracts": [
            {
                "contractId": "contract1",
                "deliveryStart": "2023-01-01T00:00:00",
                "deliveryEnd": "2023-01-02T00:00:00",
                "areas": [
                    {
                        "areaCode": "DK1",
                        "prices": [
                            {
                                "currencyCode": "EUR",
                                "marketPrice": 50.0,
                                "status": "Final",
                            },
                        ],
                    },
                ],
            },
        ],
    }
    response = AuctionPrice(**data)
    assert response.auction == "auction1"
    assert response.auction_delivery_start == datetime(2023, 1, 1)  # noqa: DTZ001
    assert response.auction_delivery_end == datetime(2023, 1, 2)  # noqa: DTZ001
    assert len(response.contracts) == 1
    assert response.contracts[0].contract_id == "contract1"
    assert len(response.contracts[0].areas) == 1
    assert response.contracts[0].areas[0].area_code == "DK1"
    assert response.contracts[0].areas[0].prices[0].status == AuctionResultState.FINAL


def test_auction_price_empty_contracts() -> None:
    """Test AuctionPrice with empty contracts."""
    data = {
        "auction": None,
        "auctionDeliveryStart": "2023-01-01T00:00:00",
        "auctionDeliveryEnd": "2023-01-02T00:00:00",
        "contracts": None,
    }
    response = AuctionPrice(**data)
    assert response.auction is None
    assert response.contracts is None
