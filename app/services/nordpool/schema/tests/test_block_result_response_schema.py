import pytest

from app.services.nordpool.schema.base_schema import AuctionResultState
from app.services.nordpool.schema.base_schema import OrderResultType
from app.services.nordpool.schema.base_schema import TradeSide
from app.services.nordpool.schema.block_result_response_schema import BlockResultResponse


@pytest.mark.parametrize(
    ("data", "expected_name", "expected_is_spread_block"),
    [
        (
            {
                "orderId": "order1",
                "orderType": "Block",
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
                "name": "Block1",
                "exclusiveGroup": "Group1",
                "linkedTo": "Block2",
                "isSpreadBlock": False,
            },
            "Block1",
            False,
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
                "name": None,
                "exclusiveGroup": None,
                "linkedTo": None,
                "isSpreadBlock": None,
            },
            None,
            None,
        ),
    ],
)
def test_block_result_response_validation(
    data: dict,
    expected_name: str | None,
    expected_is_spread_block: bool | None,
) -> None:
    """Test BlockResultResponse model validation."""
    response = BlockResultResponse(**data)
    assert response.order_id == data.get("orderId")
    assert response.order_type == OrderResultType.BLOCK
    assert response.name == expected_name
    assert response.exclusive_group == data.get("exclusiveGroup")
    assert response.linked_to == data.get("linkedTo")
    assert response.is_spread_block == expected_is_spread_block
    if response.trades:
        assert len(response.trades) == 1
        assert response.trades[0].trade_id == "trade1"
        assert response.trades[0].side == TradeSide.BUY
        assert response.trades[0].status == AuctionResultState.FINAL
