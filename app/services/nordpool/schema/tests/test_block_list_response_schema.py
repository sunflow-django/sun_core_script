from uuid import UUID

from app.services.nordpool.schema.base_schema import OrderStateType
from app.services.nordpool.schema.block_list_response_schema import BlockListResponse


def test_block_list_response_validation() -> None:
    """Test BlockListResponse model validation."""
    data = {
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
        "blocks": [
            {
                "name": "Block1",
                "price": 50.0,
                "minimumAcceptanceRatio": 1.0,
                "linkedTo": None,
                "exclusiveGroup": None,
                "periods": [
                    {"contractId": "contract1", "volume": 100.0},
                ],
                "isSpreadBlock": False,
                "modifier": "User1",
                "state": "Accepted",
            },
        ],
    }
    response = BlockListResponse(**data)
    assert response.order_id == UUID("00000000-0000-0000-0000-000000000000")
    assert response.auction_id == "auction1"
    assert response.company_name == "Company1"
    assert len(response.blocks) == 1
    assert response.blocks[0].name == "Block1"
    assert response.blocks[0].state == OrderStateType.ACCEPTED
    assert len(response.blocks[0].periods) == 1
    assert response.blocks[0].periods[0].contract_id == "contract1"


def test_block_list_response_empty_blocks() -> None:
    """Test BlockListResponse with empty blocks."""
    data = {
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
        "blocks": None,
    }
    response = BlockListResponse(**data)
    assert response.blocks is None
