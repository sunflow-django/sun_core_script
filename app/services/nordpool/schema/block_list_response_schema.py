from app.services.nordpool.schema.base_schema import BlockResponse
from app.services.nordpool.schema.base_schema import OrderResponse


class BlockListResponse(OrderResponse):
    """Schema for block list response data, inheriting from OrderResponse.

    Attributes:
        blocks: List of block responses.

    Returns:
        BlockListResponse: The validated block list response instance.
    """

    blocks: list[BlockResponse] | None = None
