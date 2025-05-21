from uuid import UUID

import pytest
from pydantic import ValidationError

from app.services.nordpool.schema.base_schema import OrderApprovalState
from app.services.nordpool.schema.reasonability_results_info_schema import ReasonabilityResultsInfo


@pytest.mark.parametrize(
    ("data", "expected_portfolio", "expected_approval_state"),
    [
        (
            {
                "portfolio": "Portfolio1",
                "area": "DK1",
                "orderApprovalState": "Approved",
                "curves": [
                    {
                        "id": "00000000-0000-0000-0000-000000000000",
                        "timeStep": 3600,
                        "contractId": "contract1",
                        "isValid": True,
                        "validationMessage": "Valid",
                    },
                ],
                "referenceDay": "2023-01-01",
                "auctionId": "auction1",
                "orderId": "00000000-0000-0000-0000-000000000000",
                "approvalModifier": "User1",
                "approvalSource": "Automatic",
            },
            "Portfolio1",
            OrderApprovalState.APPROVED,
        ),
        (
            {
                "portfolio": None,
                "area": None,
                "orderApprovalState": "Undefined",
                "curves": None,
                "referenceDay": None,
                "auctionId": None,
                "orderId": "00000000-0000-0000-0000-000000000000",
                "approvalModifier": None,
                "approvalSource": "Operator",
            },
            None,
            OrderApprovalState.UNDEFINED,
        ),
    ],
)
def test_reasonability_results_info_validation(
    data: dict,
    expected_portfolio: str | None,
    expected_approval_state: OrderApprovalState,
) -> None:
    """Test ReasonabilityResultsInfo model validation."""
    response = ReasonabilityResultsInfo(**data)
    assert response.portfolio == expected_portfolio
    assert response.area == data.get("area")
    assert response.order_approval_state == expected_approval_state
    assert response.reference_day == data.get("referenceDay")
    assert response.auction_id == data.get("auctionId")
    assert response.order_id == UUID("00000000-0000-0000-0000-000000000000")
    assert response.approval_modifier == data.get("approvalModifier")
    assert response.approval_source == data.get("approvalSource")
    if response.curves:
        assert len(response.curves) == 1
        assert response.curves[0].contract_id == "contract1"
        assert response.curves[0].is_valid is True


def test_reasonability_results_info_invalid_approval_source() -> None:
    """Test ReasonabilityResultsInfo with invalid approval source."""
    data = {
        "portfolio": "Portfolio1",
        "area": "DK1",
        "orderApprovalState": "Approved",
        "curves": None,
        "referenceDay": "2023-01-01",
        "auctionId": "auction1",
        "orderId": "00000000-0000-0000-0000-000000000000",
        "approvalModifier": "User1",
        "approvalSource": "InvalidSource",
    }
    with pytest.raises(ValidationError):
        ReasonabilityResultsInfo(**data)
