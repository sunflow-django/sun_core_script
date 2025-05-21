from pydantic import BaseModel
from pydantic import Field

from app.services.nordpool.schema.base_schema import OrderResultType
from app.services.nordpool.schema.base_schema import Trade


class BlockResultResponse(BaseModel):
    """Schema for block result response data.

    Attributes:
        order_id: The unique identifier for the order.
        order_type: The type of the order.
        auction_id: The auction identifier.
        user_id: The user identifier.
        company_name: The name of the company.
        portfolio: The portfolio name.
        currency_code: The currency code.
        area_code: The area code.
        trades: List of trades associated with the order.
        name: The name of the block.
        exclusive_group: The exclusive group identifier.
        linked_to: The linked block identifier.
        is_spread_block: Whether the block is a spread block.

    Returns:
        BlockResultResponse: The validated block result response instance.
    """

    order_id: str | None = Field(default=None, alias="orderId")
    order_type: OrderResultType = Field(alias="orderType")
    auction_id: str | None = Field(default=None, alias="auctionId")
    user_id: str | None = Field(default=None, alias="userId")
    company_name: str | None = Field(default=None, alias="companyName")
    portfolio: str | None = None
    currency_code: str | None = Field(default=None, alias="currencyCode")
    area_code: str | None = Field(default=None, alias="areaCode")
    trades: list[Trade] | None = None
    name: str | None = None
    exclusive_group: str | None = Field(default=None, alias="exclusiveGroup")
    linked_to: str | None = Field(default=None, alias="linkedTo")
    is_spread_block: bool | None = Field(default=None, alias="isSpreadBlock")
