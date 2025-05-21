from uuid import UUID

import pytest
from pydantic import ValidationError

from app.services.nordpool.schema.base_schema import OrderStateType
from app.services.nordpool.schema.curve_order_response_schema import CurveOrderResponse


def test_curve_order_response_validation() -> None:
    """Test CurveOrderResponse model validation."""
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
        "state": "Accepted",
        "curves": [
            {
                "contractId": "contract1",
                "curvePoints": [
                    {"price": 50.0, "volume": 100.0},
                ],
            },
        ],
    }
    response = CurveOrderResponse(**data)
    assert response.order_id == UUID("00000000-0000-0000-0000-000000000000")
    assert response.auction_id == "auction1"
    assert response.company_name == "Company1"
    assert response.state == OrderStateType.ACCEPTED
    assert len(response.curves) == 1
    assert response.curves[0].contract_id == "contract1"
    assert len(response.curves[0].curve_points) == 1
    assert response.curves[0].curve_points[0].price == 50.0  # noqa: PLR2004


def test_curve_order_response_invalid_state() -> None:
    """Test CurveOrderResponse with invalid state."""
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
        "state": "InvalidState",
        "curves": None,
    }
    with pytest.raises(ValidationError):
        CurveOrderResponse(**data)


def test_curve_order_response_empty_curves() -> None:
    """Test CurveOrderResponse with empty curves."""
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
        "state": "Accepted",
        "curves": None,
    }
    response = CurveOrderResponse(**data)
    assert response.curves is None
