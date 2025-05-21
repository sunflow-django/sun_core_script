
from pydantic import BaseModel
from pydantic import Field

from app.services.nordpool.schema.block_list_response_schema import BlockListResponse
from app.services.nordpool.schema.curve_order_response_schema import CurveOrderResponse


class CombinedOrdersResponse(BaseModel):
    """Schema for combined orders response data.

    Attributes:
        curve_orders: List of curve order responses.
        block_lists: List of block list responses.

    Returns:
        CombinedOrdersResponse: The validated combined orders response instance.
    """
    curve_orders: list[CurveOrderResponse] | None = Field(
        default=None, alias="curveOrders",
    )
    block_lists: list[BlockListResponse] | None = Field(
        default=None, alias="blockLists",
    )
