import pytest

from app.services.nordpool.schema.base_schema import AuctionResultState
from app.services.nordpool.schema.base_schema import OrderResultType
from app.services.nordpool.schema.base_schema import TradeSide
from app.services.nordpool.schema.order_result_response_schema import OrderResultResponse


@pytest.mark.parametrize(
    ("data", "expected_order_id", "expected_order_type"),
    [
        (
            {
                "orderId": "order1",
                "orderType": "Curve",
                "auctionId": "auction1",
                "userId": "user1",
                "companyName": "Company1",
                "portfolio": "Portfolio1",
                "currencyCode": "EUR",
                "areaCode": "DK1",
                "trades": [
                    {
                        "tradeId": "trade1",
                        "contractId": "contract1",
                        "deliveryStart": "2023-01-01T00:00:00",
                        "deliveryEnd": "2023-01-02T00:00:00",
                        "volume": 100.0,
                        "price": 50.0,
                        "side": "Buy",
                        "status": "Final",
                    },
                ],
            },
            "order1",
            OrderResultType.CURVE,
        ),
        (
            {
                "orderId": None,
                "orderType": "Block",
                "auctionId": None,
                "userId": None,
                "companyName": None,
                "portfolio": None,
                "currencyCode": None,
                "areaCode": None,
                "trades": None,
            },
            None,
            OrderResultType.BLOCK,
        ),
    ],
)
def test_order_result_response_validation(
    data: dict,
    expected_order_id: str | None,
    expected_order_type: OrderResultType,
) -> None:
    """Test OrderResultResponse model validation."""
    response = OrderResultResponse(**data)
    assert response.order_id == expected_order_id
    assert response.order_type == expected_order_type
    assert response.auction_id == data.get("auctionId")
    assert response.user_id == data.get("userId")
    assert response.company_name == data.get("companyName")
    assert response.portfolio == data.get("portfolio")
    assert response.currency_code == data.get("currencyCode")
    assert response.area_code == data.get("areaCode")
    if response.trades:
        assert len(response.trades) == 1
        assert response.trades[0].trade_id == "trade1"
        assert response.trades[0].side == TradeSide.BUY
        assert response.trades[0].status == AuctionResultState.FINAL
