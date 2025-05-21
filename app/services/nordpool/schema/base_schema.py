import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel
from pydantic import Field


class ApprovalSource(str, Enum):
    """Enum for approval source types."""

    AUTOMATIC = "Automatic"
    OPERATOR = "Operator"
    MEMBER = "Member"


class AuctionStateType(str, Enum):
    """Enum for auction state types."""

    OPEN = "Open"
    CLOSED = "Closed"
    RESULTS_PUBLISHED = "ResultsPublished"
    CANCELLED = "Cancelled"


class OrderType(BaseModel):
    """Schema for order type."""

    id: int = Field(...)
    name: str | None = Field(default=None, min_length=0)


class Currency(BaseModel):
    """Schema for currency details."""

    currency_code: str | None = Field(default=None, alias="currencyCode", min_length=0)
    min_price: float = Field(..., alias="minPrice")
    max_price: float = Field(..., alias="maxPrice")


class Contract(BaseModel):
    """Schema for contract details."""

    id: str | None = Field(default=None, min_length=0)
    delivery_start: datetime.datetime = Field(..., alias="deliveryStart")
    delivery_end: datetime.datetime = Field(..., alias="deliveryEnd")


class AreaContractGroup(BaseModel):
    """Schema for area contract group."""

    area_code: str | None = Field(default=None, alias="areaCode", min_length=0)
    contracts: list[Contract] | None = Field(default=None)


class PortfolioArea(BaseModel):
    """Schema for portfolio area details."""

    code: str | None = Field(default=None, min_length=0)
    name: str | None = Field(default=None, min_length=0)
    eic_code: str | None = Field(default=None, alias="eicCode", min_length=0)
    curve_min_volume_limit: float = Field(..., alias="curveMinVolumeLimit")
    curve_max_volume_limit: float = Field(..., alias="curveMaxVolumeLimit")
    auction_trading_resolution: int = Field(..., alias="auctionTradingResolution")


class AuctionPortfolio(BaseModel):
    """Schema for auction portfolio details."""

    name: str | None = Field(default=None, min_length=0)
    id: str | None = Field(default=None, min_length=0)
    currency: str | None = Field(default=None, min_length=0)
    company_id: str | None = Field(default=None, alias="companyId", min_length=0)
    company_name: str | None = Field(default=None, alias="companyName", min_length=0)
    permission: str | None = Field(default=None, min_length=0)
    areas: list[PortfolioArea] | None = Field(default=None)


class ContractNetVolume(BaseModel):
    """Schema for contract net volume."""

    net_volume: float | None = Field(default=None, alias="netVolume")
    contract_id: str | None = Field(default=None, alias="contractId", min_length=0)
    delivery_start: datetime.datetime = Field(..., alias="deliveryStart")
    delivery_end: datetime.datetime = Field(..., alias="deliveryEnd")


class AreaNetVolume(BaseModel):
    """Schema for area net volume."""

    area_code: str | None = Field(default=None, alias="areaCode", min_length=0)
    net_volumes: list[ContractNetVolume] | None = Field(default=None, alias="netVolumes")


class PortfolioNetVolume(BaseModel):
    """Schema for portfolio net volume."""

    portfolio: str | None = Field(default=None, min_length=0)
    company_name: str | None = Field(default=None, alias="companyName", min_length=0)
    area_net_volumes: list[AreaNetVolume] | None = Field(default=None, alias="areaNetVolumes")


class CurrencyPrice(BaseModel):
    """Schema for currency price details."""

    currency_code: str | None = Field(default=None, alias="currencyCode", min_length=0)
    market_price: float | None = Field(default=None, alias="marketPrice")
    status: str = Field(...)


class AreaPrice(BaseModel):
    """Schema for area price details."""

    area_code: str | None = Field(default=None, alias="areaCode", min_length=0)
    prices: list[CurrencyPrice] | None = Field(default=None)


class ContractPrice(BaseModel):
    """Schema for contract price details."""

    contract_id: str | None = Field(default=None, alias="contractId", min_length=0)
    delivery_start: datetime.datetime = Field(..., alias="deliveryStart")
    delivery_end: datetime.datetime = Field(..., alias="deliveryEnd")
    areas: list[AreaPrice] | None = Field(default=None)


class BlockPeriod(BaseModel):
    """Schema for block period details."""

    contract_id: str = Field(..., alias="contractId", min_length=1)
    volume: float = Field(...)


class Block(BaseModel):
    """Schema for block details."""

    name: str = Field(..., min_length=1)
    price: float = Field(...)
    minimum_acceptance_ratio: float = Field(..., alias="minimumAcceptanceRatio")
    linked_to: str | None = Field(default=None, alias="linkedTo", min_length=0)
    exclusive_group: str | None = Field(default=None, alias="exclusiveGroup", min_length=0)
    periods: list[BlockPeriod] = Field(...)
    is_spread_block: bool = Field(..., alias="isSpreadBlock")


class BlockResponse(Block):
    """Schema for block response details, extending Block."""

    modifier: str | None = Field(default=None, min_length=0)
    state: str = Field(...)


class Order(BaseModel):
    """Represents order details for the NPS Auction API."""

    auction_id: str = Field(..., alias="auctionId", min_length=1)
    portfolio: str = Field(..., min_length=1)
    area_code: str = Field(..., alias="areaCode", min_length=1)
    comment: str | None = Field(default=None, max_length=255, min_length=0)


class OrderStateType(str, Enum):
    """Enum for order state types."""

    NEW = "New"
    ACCEPTED = "Accepted"
    CANCELLED = "Cancelled"
    USER_ACCEPTED = "UserAccepted"
    RESULTS_PUBLISHED = "ResultsPublished"
    NONE = "None"


class OrderResponse(BaseModel):
    """Schema for order response details."""

    order_id: UUID = Field(..., alias="orderId")
    auction_id: str | None = Field(default=None, alias="auctionId", min_length=0)
    company_name: str | None = Field(default=None, alias="companyName", min_length=0)
    portfolio: str | None = Field(default=None, min_length=0)
    area_code: str | None = Field(default=None, alias="areaCode", min_length=0)
    modifier: str | None = Field(default=None, min_length=0)
    modified: datetime.datetime = Field(...)
    currency_code: str | None = Field(default=None, alias="currencyCode", min_length=0)
    comment: str | None = Field(default=None, min_length=0)
    resolution_seconds: int = Field(..., alias="resolutionSeconds")


class TradeSide(str, Enum):
    """Enum for trade side types."""

    BUY = "Buy"
    SELL = "Sell"


class AuctionResultState(str, Enum):
    """Enum for auction result state types."""

    NOT_AVAILABLE = "NotAvailable"
    PRELIMINARY_RESULTS = "PreliminaryResults"
    FINAL = "Final"
    INITIAL_PRICE = "InitialPrice"


class Trade(BaseModel):
    """Schema for trade details."""

    trade_id: str | None = Field(default=None, alias="tradeId", min_length=0)
    contract_id: str | None = Field(default=None, alias="contractId", min_length=0)
    delivery_start: datetime.datetime = Field(..., alias="deliveryStart")
    delivery_end: datetime.datetime = Field(..., alias="deliveryEnd")
    volume: float = Field(...)
    price: float = Field(...)
    side: TradeSide = Field(...)
    status: AuctionResultState = Field(...)


class CurvePoint(BaseModel):
    """Schema for curve point details."""

    price: float = Field(...)
    volume: float = Field(...)


class Curve(BaseModel):
    """Schema for curve details."""

    contract_id: str = Field(..., alias="contractId", min_length=1)
    curve_points: list[CurvePoint] = Field(..., alias="curvePoints")


class ValidatedCurve(BaseModel):
    """Schema for validated curve details."""

    id: UUID = Field(...)
    time_step: int = Field(..., alias="timeStep")
    contract_id: str | None = Field(default=None, alias="contractId", min_length=0)
    is_valid: bool = Field(..., alias="isValid")
    validation_message: str | None = Field(default=None, alias="validationMessage", min_length=0)


class OrderResultType(str, Enum):
    """Enum for order result types."""

    CURVE = "Curve"
    BLOCK = "Block"
    ROUNDING_RESIDUAL = "RoundingResidual"


class OrderApprovalState(str, Enum):
    """Enum for order approval state types."""

    UNDEFINED = "Undefined"
    APPROVED = "Approved"
    NOT_APPROVED = "NotApproved"
