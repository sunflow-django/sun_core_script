from uuid import UUID

from pydantic import BaseModel
from pydantic import Field

from app.services.nordpool.schema.base_schema import ApprovalSource
from app.services.nordpool.schema.base_schema import OrderApprovalState
from app.services.nordpool.schema.base_schema import ValidatedCurve


class ReasonabilityResultsInfo(BaseModel):
    """Schema for reasonability results info data.

    Attributes:
        portfolio: The portfolio name.
        area: The area code.
        order_approval_state: The approval state of the order.
        curves: List of validated curves.
        reference_day: The reference day for the results.
        auction_id: The auction identifier.
        order_id: The unique identifier for the order.
        approval_modifier: The modifier for approval.
        approval_source: The source of approval.

    Returns:
        ReasonabilityResultsInfo: The validated reasonability results info instance.
    """

    portfolio: str | None = None
    area: str | None = None
    order_approval_state: OrderApprovalState = Field(alias="orderApprovalState")
    curves: list[ValidatedCurve] | None = None
    reference_day: str | None = Field(default=None, alias="referenceDay")
    auction_id: str | None = Field(default=None, alias="auctionId")
    order_id: UUID = Field(alias="orderId")
    approval_modifier: str | None = Field(default=None, alias="approvalModifier")
    approval_source: ApprovalSource = Field(alias="approvalSource")
