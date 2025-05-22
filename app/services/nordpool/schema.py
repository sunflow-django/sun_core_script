from datetime import datetime
from enum import Enum
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel
from pydantic import Field


class ApprovalSource(str, Enum):
    AUTOMATIC = "Automatic"
    OPERATOR = "Operator"
    MEMBER = "Member"


class AuctionResultState(str, Enum):
    NOT_AVAILABLE = "NotAvailable"
    PRELIMINARY_RESULTS = "PreliminaryResults"
    FINAL = "Final"
    INITIAL_PRICE = "InitialPrice"


class AuctionStateType(str, Enum):
    OPEN = "Open"
    CLOSED = "Closed"
    RESULTS_PUBLISHED = "ResultsPublished"
    CANCELLED = "Cancelled"


class BlockPeriod(BaseModel, extra="forbid"):
    contract_id: Annotated[str, Field(alias="contractId", min_length=1)]
    volume: float


class Contract(BaseModel, extra="forbid"):
    id: str | None = None
    delivery_start: Annotated[datetime | None, Field(alias="deliveryStart")] = None
    delivery_end: Annotated[datetime | None, Field(alias="deliveryEnd")] = None


class ContractNetVolume(BaseModel, extra="forbid"):
    net_volume: Annotated[float | None, Field(alias="netVolume")] = None
    contract_id: Annotated[str | None, Field(alias="contractId")] = None
    delivery_start: Annotated[datetime | None, Field(alias="deliveryStart")] = None
    delivery_end: Annotated[datetime | None, Field(alias="deliveryEnd")] = None


class Currency(BaseModel, extra="forbid"):
    currency_code: Annotated[str | None, Field(alias="currencyCode")] = None
    min_price: Annotated[float | None, Field(alias="minPrice")] = None
    max_price: Annotated[float | None, Field(alias="maxPrice")] = None


class CurrencyPrice(BaseModel, extra="forbid"):
    currency_code: Annotated[str | None, Field(alias="currencyCode")] = None
    market_price: Annotated[float | None, Field(alias="marketPrice")] = None
    status: AuctionResultState | None = None


class CurvePoint(BaseModel, extra="forbid"):
    price: float
    volume: float


class Order(BaseModel, extra="forbid"):
    auction_id: Annotated[str, Field(alias="auctionId", min_length=1)]
    portfolio: Annotated[str, Field(min_length=1)]
    area_code: Annotated[str, Field(alias="areaCode", min_length=1)]
    comment: Annotated[str | None, Field(max_length=255, min_length=0)] = None


class OrderApprovalState(str, Enum):
    UNDEFINED = "Undefined"
    APPROVED = "Approved"
    NOT_APPROVED = "NotApproved"


class OrderResponse(BaseModel, extra="forbid"):
    order_id: Annotated[UUID | None, Field(alias="orderId")] = None
    auction_id: Annotated[str | None, Field(alias="auctionId")] = None
    company_name: Annotated[str | None, Field(alias="companyName")] = None
    portfolio: str | None = None
    area_code: Annotated[str | None, Field(alias="areaCode")] = None
    modifier: str | None = None
    modified: datetime | None = None
    currency_code: Annotated[str | None, Field(alias="currencyCode")] = None
    comment: str | None = None
    resolution_seconds: Annotated[int | None, Field(alias="resolutionSeconds")] = None


class OrderResultType(str, Enum):
    CURVE = "Curve"
    BLOCK = "Block"
    ROUNDING_RESIDUAL = "RoundingResidual"


class OrderStateType(str, Enum):
    NEW = "New"
    ACCEPTED = "Accepted"
    CANCELLED = "Cancelled"
    USER_ACCEPTED = "UserAccepted"
    RESULTS_PUBLISHED = "ResultsPublished"
    NONE = "None"


class OrderType(BaseModel, extra="forbid"):
    id: int | None = None
    name: str | None = None


class PortfolioArea(BaseModel, extra="forbid"):
    code: str | None = None
    name: str | None = None
    eic_code: Annotated[str | None, Field(alias="eicCode")] = None
    curve_min_volume_limit: Annotated[float | None, Field(alias="curveMinVolumeLimit")] = None
    curve_max_volume_limit: Annotated[float | None, Field(alias="curveMaxVolumeLimit")] = None
    auction_trading_resolution: Annotated[int | None, Field(alias="auctionTradingResolution")] = None


class ProblemDetails(BaseModel, extra="forbid"):
    type: str | None = None
    title: str | None = None
    status: int | None = None
    detail: str | None = None
    instance: str | None = None


class TradeSide(str, Enum):
    BUY = "Buy"
    SELL = "Sell"


class ValidatedCurve(BaseModel, extra="forbid"):
    id: UUID | None = None
    time_step: Annotated[int | None, Field(alias="timeStep")] = None
    contract_id: Annotated[str | None, Field(alias="contractId")] = None
    is_valid: Annotated[bool | None, Field(alias="isValid")] = None
    validation_message: Annotated[str | None, Field(alias="validationMessage")] = None


class AreaContractGroup(BaseModel, extra="forbid"):
    area_code: Annotated[str | None, Field(alias="areaCode")] = None
    contracts: list[Contract] | None = None


class AreaNetVolume(BaseModel, extra="forbid"):
    area_code: Annotated[str | None, Field(alias="areaCode")] = None
    net_volumes: Annotated[list[ContractNetVolume] | None, Field(alias="netVolumes")] = None


class AreaPrice(BaseModel, extra="forbid"):
    area_code: Annotated[str | None, Field(alias="areaCode")] = None
    prices: list[CurrencyPrice] | None = None


class AuctionPortfolio(BaseModel, extra="forbid"):
    name: str | None = None
    id: str | None = None
    currency: str | None = None
    company_id: Annotated[str | None, Field(alias="companyId")] = None
    company_name: Annotated[str | None, Field(alias="companyName")] = None
    permission: str | None = None
    areas: list[PortfolioArea] | None = None


class AuctionResponse(BaseModel, extra="forbid"):
    id: str | None = None
    name: str | None = None
    state: AuctionStateType | None = None
    close_for_bidding: Annotated[datetime | None, Field(alias="closeForBidding")] = None
    delivery_start: Annotated[datetime | None, Field(alias="deliveryStart")] = None
    delivery_end: Annotated[datetime | None, Field(alias="deliveryEnd")] = None
    available_order_types: Annotated[list[OrderType] | None, Field(alias="availableOrderTypes")] = None
    currencies: list[Currency] | None = None
    contracts: list[Contract] | None = None
    portfolios: list[AuctionPortfolio] | None = None


class Block(BaseModel, extra="forbid"):
    name: Annotated[str, Field(min_length=1)]
    price: float
    minimum_acceptance_ratio: Annotated[float, Field(alias="minimumAcceptanceRatio")]
    linked_to: Annotated[str | None, Field(alias="linkedTo")] = None
    exclusive_group: Annotated[str | None, Field(alias="exclusiveGroup")] = None
    periods: list[BlockPeriod]
    is_spread_block: Annotated[bool | None, Field(alias="isSpreadBlock")] = None


class BlockResponse(Block, extra="forbid"):
    modifier: str | None = None
    state: OrderStateType | None = None


class ContractPrice(BaseModel, extra="forbid"):
    contract_id: Annotated[str | None, Field(alias="contractId")] = None
    delivery_start: Annotated[datetime | None, Field(alias="deliveryStart")] = None
    delivery_end: Annotated[datetime | None, Field(alias="deliveryEnd")] = None
    areas: list[AreaPrice] | None = None


class Curve(BaseModel, extra="forbid"):
    contract_id: Annotated[str, Field(alias="contractId", min_length=1)]
    curve_points: Annotated[list[CurvePoint], Field(alias="curvePoints")]


class CurveOrder(Order, extra="forbid"):
    curves: list[Curve]


class CurveOrderPatch(BaseModel, extra="forbid"):
    curves: list[Curve] | None = None
    comment: Annotated[str | None, Field(max_length=255, min_length=0)] = None


class CurveOrderResponse(OrderResponse, extra="forbid"):
    state: OrderStateType | None = None
    curves: list[Curve] | None = None


class PortfolioNetVolume(BaseModel, extra="forbid"):
    portfolio: str | None = None
    company_name: Annotated[str | None, Field(alias="companyName")] = None
    area_net_volumes: Annotated[list[AreaNetVolume] | None, Field(alias="areaNetVolumes")] = None


class PortfolioVolumeResponse(BaseModel, extra="forbid"):
    auction_id: Annotated[str | None, Field(alias="auctionId")] = None
    portfolio_net_volumes: Annotated[list[PortfolioNetVolume] | None, Field(alias="portfolioNetVolumes")] = None


class ReasonabilityResultsInfo(BaseModel, extra="forbid"):
    portfolio: str | None = None
    area: str | None = None
    order_approval_state: Annotated[OrderApprovalState | None, Field(alias="orderApprovalState")] = None
    curves: list[ValidatedCurve] | None = None
    reference_day: Annotated[str | None, Field(alias="referenceDay")] = None
    auction_id: Annotated[str | None, Field(alias="auctionId")] = None
    order_id: Annotated[UUID | None, Field(alias="orderId")] = None
    approval_modifier: Annotated[str | None, Field(alias="approvalModifier")] = None
    approval_source: Annotated[ApprovalSource | None, Field(alias="approvalSource")] = None


class Trade(BaseModel, extra="forbid"):
    trade_id: Annotated[str | None, Field(alias="tradeId")] = None
    contract_id: Annotated[str | None, Field(alias="contractId")] = None
    delivery_start: Annotated[datetime | None, Field(alias="deliveryStart")] = None
    delivery_end: Annotated[datetime | None, Field(alias="deliveryEnd")] = None
    volume: float | None = None
    price: float | None = None
    side: TradeSide | None = None
    status: AuctionResultState | None = None


class AuctionMultiResolutionResponse(BaseModel, extra="forbid"):
    id: str | None = None
    name: str | None = None
    state: AuctionStateType | None = None
    close_for_bidding: Annotated[datetime | None, Field(alias="closeForBidding")] = None
    delivery_start: Annotated[datetime | None, Field(alias="deliveryStart")] = None
    delivery_end: Annotated[datetime | None, Field(alias="deliveryEnd")] = None
    available_order_types: Annotated[list[OrderType] | None, Field(alias="availableOrderTypes")] = None
    currencies: list[Currency] | None = None
    contracts: list[AreaContractGroup] | None = None
    portfolios: list[AuctionPortfolio] | None = None


class AuctionPrice(BaseModel, extra="forbid"):
    auction: str | None = None
    auction_delivery_start: Annotated[datetime | None, Field(alias="auctionDeliveryStart")] = None
    auction_delivery_end: Annotated[datetime | None, Field(alias="auctionDeliveryEnd")] = None
    contracts: list[ContractPrice] | None = None


class BlockList(Order, extra="forbid"):
    blocks: list[Block | BlockResponse] | None = None


class BlockListResponse(OrderResponse, extra="forbid"):
    blocks: list[BlockResponse] | None = None


class BlockOrderPatch(BaseModel, extra="forbid"):
    blocks: list[Block | BlockResponse] | None = None
    comment: Annotated[str | None, Field(max_length=255, min_length=0)] = None


class CombinedOrdersResponse(BaseModel, extra="forbid"):
    curve_orders: Annotated[list[CurveOrderResponse] | None, Field(alias="curveOrders")] = None
    block_lists: Annotated[list[BlockListResponse] | None, Field(alias="blockLists")] = None


class OrderResultResponse(BaseModel, extra="forbid"):
    order_id: Annotated[str | None, Field(alias="orderId")] = None
    order_type: Annotated[OrderResultType | None, Field(alias="orderType")] = None
    auction_id: Annotated[str | None, Field(alias="auctionId")] = None
    user_id: Annotated[str | None, Field(alias="userId")] = None
    company_name: Annotated[str | None, Field(alias="companyName")] = None
    portfolio: str | None = None
    currency_code: Annotated[str | None, Field(alias="currencyCode")] = None
    area_code: Annotated[str | None, Field(alias="areaCode")] = None
    trades: list[Trade] | None = None


class BlockResultResponse(OrderResultResponse, extra="forbid"):
    name: str | None = None
    exclusive_group: Annotated[str | None, Field(alias="exclusiveGroup")] = None
    linked_to: Annotated[str | None, Field(alias="linkedTo")] = None
    is_spread_block: Annotated[bool | None, Field(alias="isSpreadBlock")] = None
