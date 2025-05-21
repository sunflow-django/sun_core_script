from uuid import UUID

from app.services.nordpool.schema.combined_orders_response_schema import CombinedOrdersResponse


def test_combined_orders_response_validation() -> None:
    """Test CombinedOrdersResponse model validation."""
    data = {
        "curveOrders": [
            {
                "orderId": "00000000-0000-0000-0000-000000000000",
                "auctionId": "auction1",
                "companyName": "Company1",
                "portfolio": "Portfolio1",
                "areaCode": "DK1",
                "modifier": "User1",
                "modified": "2023-01-01T00:00:00",
                "currencyCode": "EUR",
                "comment": "Test comment",
                "resolutionSeconds": 3600,
                "state": "Accepted",
                "curves": [
                    {
                        "contractId": "contract1",
                        "curvePoints": [
                            {"price": 50.0, "volume": 100.0},
                        ],
                    },
                ],
            },
        ],
        "blockLists": [
            {
                "orderId": "00000000-0000-0000-0000-000000000001",
                "auctionId": "auction2",
                "companyName": "Company2",
                "portfolio": "Portfolio2",
                "areaCode": "DK2",
                "modifier": "User2",
                "modified": "2023-01-01T00:00:00",
                "currencyCode": "EUR",
                "comment": "Test block",
                "resolutionSeconds": 3600,
                "blocks": [
                    {
                        "name": "Block1",
                        "price": 50.0,
                        "minimumAcceptanceRatio": 1.0,
                        "linkedTo": None,
                        "exclusiveGroup": None,
                        "periods": [
                            {"contractId": "contract2", "volume": 100.0},
                        ],
                        "isSpreadBlock": False,
                        "modifier": "User2",
                        "state": "Accepted",
                    },
                ],
            },
        ],
    }
    response = CombinedOrdersResponse(**data)
    assert len(response.curve_orders) == 1
    assert response.curve_orders[0].order_id == UUID(
        "00000000-0000-0000-0000-000000000000",
    )
    assert len(response.block_lists) == 1
    assert response.block_lists[0].order_id == UUID(
        "00000000-0000-0000-0000-000000000001",
    )


def test_combined_orders_response_empty() -> None:
    """Test CombinedOrdersResponse with empty lists."""
    response = CombinedOrdersResponse(curveOrders=None, blockLists=None)
    assert response.curve_orders is None
    assert response.block_lists is None
