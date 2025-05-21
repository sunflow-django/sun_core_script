from pydantic import BaseModel
from pydantic import Field

from app.services.nordpool.schema.base_schema import PortfolioNetVolume


class PortfolioVolumeResponse(BaseModel):
    """Schema for portfolio volume response data.

    Attributes:
        auction_id: The auction identifier.
        portfolio_net_volumes: List of portfolio net volumes.

    Returns:
        PortfolioVolumeResponse: The validated portfolio volume response instance.
    """

    auction_id: str | None = Field(default=None, alias="auctionId")
    portfolio_net_volumes: list[PortfolioNetVolume] | None = Field(
        default=None,
        alias="portfolioNetVolumes",
        json_schema_extra={"readOnly": True},
    )
