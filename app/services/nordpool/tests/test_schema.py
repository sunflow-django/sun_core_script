from datetime import datetime
from uuid import UUID

import pytest
from pydantic import ValidationError

from app.constants.time_zones import PARIS_TZ
from app.services.nordpool.schema import ApprovalSource
from app.services.nordpool.schema import AreaContractGroup
from app.services.nordpool.schema import AreaNetVolume
from app.services.nordpool.schema import AreaPrice
from app.services.nordpool.schema import AuctionMultiResolutionResponse
from app.services.nordpool.schema import AuctionPortfolio
from app.services.nordpool.schema import AuctionPrice
from app.services.nordpool.schema import AuctionResponse
from app.services.nordpool.schema import AuctionResultState
from app.services.nordpool.schema import AuctionStateType
from app.services.nordpool.schema import Block
from app.services.nordpool.schema import BlockListResponse
from app.services.nordpool.schema import BlockPeriod
from app.services.nordpool.schema import BlockResponse
from app.services.nordpool.schema import BlockResultResponse
from app.services.nordpool.schema import CombinedOrdersResponse
from app.services.nordpool.schema import Contract
from app.services.nordpool.schema import ContractNetVolume
from app.services.nordpool.schema import ContractPrice
from app.services.nordpool.schema import Currency
from app.services.nordpool.schema import CurrencyPrice
from app.services.nordpool.schema import Curve
from app.services.nordpool.schema import CurveOrderResponse
from app.services.nordpool.schema import CurvePoint
from app.services.nordpool.schema import Order
from app.services.nordpool.schema import OrderApprovalState
from app.services.nordpool.schema import OrderResponse
from app.services.nordpool.schema import OrderResultResponse
from app.services.nordpool.schema import OrderResultType
from app.services.nordpool.schema import OrderStateType
from app.services.nordpool.schema import OrderType
from app.services.nordpool.schema import PortfolioArea
from app.services.nordpool.schema import PortfolioNetVolume
from app.services.nordpool.schema import PortfolioVolumeResponse
from app.services.nordpool.schema import ReasonabilityResultsInfo
from app.services.nordpool.schema import Trade
from app.services.nordpool.schema import TradeSide
from app.services.nordpool.schema import ValidatedCurve


# Constants to avoid magic value used in comparison
PRICE = 100.0
VOLUME = 200.0
MAX_VOLUME = 1000.0
TRADING_RESOLUTION = 3600
MARKET_PRICE = 50.0



def test_approval_source_enum() -> None:
    """Test ApprovalSource enum values."""
    assert ApprovalSource.AUTOMATIC == "Automatic"
    assert ApprovalSource.OPERATOR == "Operator"
    assert ApprovalSource.MEMBER == "Member"


def test_auction_state_type_enum() -> None:
    """Test AuctionStateType enum values."""
    assert AuctionStateType.OPEN == "Open"
    assert AuctionStateType.CLOSED == "Closed"
    assert AuctionStateType.RESULTS_PUBLISHED == "ResultsPublished"
    assert AuctionStateType.CANCELLED == "Cancelled"


@pytest.mark.parametrize(
    ("data", "expected_id", "expected_name"),
    [
        ({"id": 1, "name": "Test"}, 1, "Test"),
        ({"id": 2, "name": None}, 2, None),
    ],
)
def test_order_type(data: dict, expected_id: int, expected_name: str | None) -> None:
    """Test OrderType model validation."""
    order_type = OrderType(**data)
    assert order_type.id == expected_id
    assert order_type.name == expected_name


def test_currency_validation() -> None:
    """Test Currency model validation."""
    currency = Currency(currencyCode="EUR", minPrice=0.0, maxPrice=PRICE)
    assert currency.currency_code == "EUR"
    assert currency.min_price == 0.0
    assert currency.max_price == PRICE


def test_contract_validation() -> None:
    """Test Contract model validation."""
    contract = Contract(
        id="contract1",
        deliveryStart=datetime(2023, 1, 1, tzinfo=PARIS_TZ),
        deliveryEnd=datetime(2023, 1, 2, tzinfo=PARIS_TZ),
    )
    assert contract.id == "contract1"
    assert contract.delivery_start == datetime(2023, 1, 1, tzinfo=PARIS_TZ)
    assert contract.delivery_end == datetime(2023, 1, 2, tzinfo=PARIS_TZ)


def test_area_contract_group_validation() -> None:
    """Test AreaContractGroup model validation."""
    contract = Contract(
        id="contract1",
        deliveryStart=datetime(2023, 1, 1, tzinfo=PARIS_TZ),
        deliveryEnd=datetime(2023, 1, 2, tzinfo=PARIS_TZ),
    )
    group = AreaContractGroup(areaCode="DK1", contracts=[contract])
    assert group.area_code == "DK1"
    assert len(group.contracts) == 1
    assert group.contracts[0].id == "contract1"


def test_portfolio_area_validation() -> None:
    """Test PortfolioArea model validation."""
    area = PortfolioArea(
        code="DK1",
        name="Denmark 1",
        eicCode="EIC1",
        curveMinVolumeLimit=0.0,
        curveMaxVolumeLimit=MAX_VOLUME,
        auctionTradingResolution=TRADING_RESOLUTION,
    )
    assert area.code == "DK1"
    assert area.name == "Denmark 1"
    assert area.eic_code == "EIC1"
    assert area.curve_min_volume_limit == 0.0
    assert area.curve_max_volume_limit == MAX_VOLUME
    assert area.auction_trading_resolution == TRADING_RESOLUTION


def test_auction_portfolio_validation() -> None:
    """Test AuctionPortfolio model validation."""
    area = PortfolioArea(
        code="DK1",
        name="Denmark 1",
        eicCode="EIC1",
        curveMinVolumeLimit=0.0,
        curveMaxVolumeLimit=MAX_VOLUME,
        auctionTradingResolution=TRADING_RESOLUTION,
    )
    portfolio = AuctionPortfolio(
        name="Portfolio1",
        id="p1",
        currency="EUR",
        companyId="c1",
        companyName="Company1",
        permission="read",
        areas=[area],
    )
    assert portfolio.name == "Portfolio1"
    assert portfolio.id == "p1"
    assert portfolio.currency == "EUR"
    assert portfolio.company_id == "c1"
    assert portfolio.company_name == "Company1"
    assert portfolio.permission == "read"
    assert len(portfolio.areas) == 1


def test_contract_net_volume_validation() -> None:
    """Test ContractNetVolume model validation."""
    net_volume = ContractNetVolume(
        netVolume=VOLUME,
        contractId="contract1",
        deliveryStart=datetime(2023, 1, 1, tzinfo=PARIS_TZ),
        deliveryEnd=datetime(2023, 1, 2, tzinfo=PARIS_TZ),
    )
    assert net_volume.net_volume == VOLUME
    assert net_volume.contract_id == "contract1"
    assert net_volume.delivery_start == datetime(2023, 1, 1, tzinfo=PARIS_TZ)
    assert net_volume.delivery_end == datetime(2023, 1, 2, tzinfo=PARIS_TZ)


def test_area_net_volume_validation() -> None:
    """Test AreaNetVolume model validation."""
    net_volume = ContractNetVolume(
        netVolume=VOLUME,
        contractId="contract1",
        deliveryStart=datetime(2023, 1, 1, tzinfo=PARIS_TZ),
        deliveryEnd=datetime(2023, 1, 2, tzinfo=PARIS_TZ),
    )
    area_net = AreaNetVolume(areaCode="DK1", netVolumes=[net_volume])
    assert area_net.area_code == "DK1"
    assert len(area_net.net_volumes) == 1


def test_portfolio_net_volume_validation() -> None:
    """Test PortfolioNetVolume model validation."""
    net_volume = ContractNetVolume(
        netVolume=VOLUME,
        contractId="contract1",
        deliveryStart=datetime(2023, 1, 1, tzinfo=PARIS_TZ),
        deliveryEnd=datetime(2023, 1, 2, tzinfo=PARIS_TZ),
    )
    area_net = AreaNetVolume(areaCode="DK1", netVolumes=[net_volume])
    portfolio_net = PortfolioNetVolume(
        portfolio="Portfolio1",
        companyName="Company1",
        areaNetVolumes=[area_net],
    )
    assert portfolio_net.portfolio == "Portfolio1"
    assert portfolio_net.company_name == "Company1"
    assert len(portfolio_net.area_net_volumes) == 1


def test_currency_price_validation() -> None:
    """Test CurrencyPrice model validation."""
    price = CurrencyPrice(
        currencyCode="EUR",
        marketPrice=MARKET_PRICE,
        status=AuctionResultState.FINAL,
    )
    assert price.currency_code == "EUR"
    assert price.market_price == MARKET_PRICE
    assert price.status == AuctionResultState.FINAL


def test_area_price_validation() -> None:
    """Test AreaPrice model validation."""
    price = CurrencyPrice(
        currencyCode="EUR",
        marketPrice=MARKET_PRICE,
        status=AuctionResultState.FINAL,
    )
    area_price = AreaPrice(areaCode="DK1", prices=[price])
    assert area_price.area_code == "DK1"
    assert len(area_price.prices) == 1


def test_contract_price_validation() -> None:
    """Test ContractPrice model validation."""
    price = CurrencyPrice(
        currencyCode="EUR",
        marketPrice=MARKET_PRICE,
        status=AuctionResultState.FINAL,
    )
    area_price = AreaPrice(areaCode="DK1", prices=[price])
    contract_price = ContractPrice(
        contractId="contract1",
        deliveryStart=datetime(2023, 1, 1, tzinfo=PARIS_TZ),
        deliveryEnd=datetime(2023, 1, 2, tzinfo=PARIS_TZ),
        areas=[area_price],
    )
    assert contract_price.contract_id == "contract1"
    assert len(contract_price.areas) == 1


def test_block_period_validation() -> None:
    """Test BlockPeriod model validation."""
    period = BlockPeriod(contractId="contract1", volume=VOLUME)
    assert period.contract_id == "contract1"
    assert period.volume == VOLUME


def test_block_validation() -> None:
    """Test Block model validation."""
    period = BlockPeriod(contractId="contract1", volume=VOLUME)
    block = Block(
        name="Block1",
        price=MARKET_PRICE,
        minimumAcceptanceRatio=1.0,
        linkedTo="block2",
        exclusiveGroup="group1",
        periods=[period],
        isSpreadBlock=False,
    )
    assert block.name == "Block1"
    assert block.price == MARKET_PRICE
    assert block.minimum_acceptance_ratio == 1.0
    assert block.linked_to == "block2"
    assert block.exclusive_group == "group1"
    assert len(block.periods) == 1
    assert block.is_spread_block is False


def test_block_response_validation() -> None:
    """Test BlockResponse model validation."""
    period = BlockPeriod(contractId="contract1", volume=VOLUME)
    block_response = BlockResponse(
        name="Block1",
        price=MARKET_PRICE,
        minimumAcceptanceRatio=1.0,
        linkedTo="block2",
        exclusiveGroup="group1",
        periods=[period],
        isSpreadBlock=False,
        modifier="User1",
        state=OrderStateType.ACCEPTED,
    )
    assert block_response.name == "Block1"
    assert block_response.modifier == "User1"
    assert block_response.state == OrderStateType.ACCEPTED


def test_order_validation() -> None:
    """Test Order model validation."""
    order = Order(
        auctionId="auction1",
        portfolio="Portfolio1",
        areaCode="DK1",
        comment="Test comment",
    )
    assert order.auction_id == "auction1"
    assert order.portfolio == "Portfolio1"
    assert order.area_code == "DK1"
    assert order.comment == "Test comment"

    with pytest.raises(ValidationError):
        Order(
            auctionId="",  # Invalid: empty string
            portfolio="Portfolio1",
            areaCode="DK1",
        )


def test_order_response_validation() -> None:
    """Test OrderResponse model validation."""
    order_response = OrderResponse(
        orderId=UUID("00000000-0000-0000-0000-000000000000"),
        auctionId="auction1",
        companyName="Company1",
        portfolio="Portfolio1",
        areaCode="DK1",
        modifier="User1",
        modified=datetime(2023, 1, 1, tzinfo=PARIS_TZ),
        currencyCode="EUR",
        comment="Test comment",
        resolutionSeconds=TRADING_RESOLUTION,
    )
    assert order_response.order_id == UUID("00000000-0000-0000-0000-000000000000")
    assert order_response.auction_id == "auction1"
    assert order_response.company_name == "Company1"
    assert order_response.currency_code == "EUR"


def test_trade_validation() -> None:
    """Test Trade model validation."""
    trade = Trade(
        tradeId="trade1",
        contractId="contract1",
        deliveryStart=datetime(2023, 1, 1, tzinfo=PARIS_TZ),
        deliveryEnd=datetime(2023, 1, 2, tzinfo=PARIS_TZ),
        volume=VOLUME,
        price=MARKET_PRICE,
        side=TradeSide.BUY,
        status=AuctionResultState.FINAL,
    )
    assert trade.trade_id == "trade1"
    assert trade.contract_id == "contract1"
    assert trade.volume == VOLUME
    assert trade.price == MARKET_PRICE
    assert trade.side == TradeSide.BUY
    assert trade.status == AuctionResultState.FINAL


def test_curve_point_validation() -> None:
    """Test CurvePoint model validation."""
    point = CurvePoint(price=MARKET_PRICE, volume=VOLUME)
    assert point.price == MARKET_PRICE
    assert point.volume == VOLUME


def test_curve_validation() -> None:
    """Test Curve model validation."""
    point = CurvePoint(price=MARKET_PRICE, volume=VOLUME)
    curve = Curve(contractId="contract1", curvePoints=[point])
    assert curve.contract_id == "contract1"
    assert len(curve.curve_points) == 1


def test_validated_curve_validation() -> None:
    """Test ValidatedCurve model validation."""
    curve = ValidatedCurve(
        id=UUID("00000000-0000-0000-0000-000000000000"),
        timeStep=TRADING_RESOLUTION,
        contractId="contract1",
        isValid=True,
        validationMessage="Valid",
    )
    assert curve.id == UUID("00000000-0000-0000-0000-000000000000")
    assert curve.time_step == TRADING_RESOLUTION
    assert curve.contract_id == "contract1"
    assert curve.is_valid is True
    assert curve.validation_message == "Valid"


def test_order_result_type_enum() -> None:
    """Test OrderResultType enum values."""
    assert OrderResultType.CURVE == "Curve"
    assert OrderResultType.BLOCK == "Block"
    assert OrderResultType.ROUNDING_RESIDUAL == "RoundingResidual"


def test_order_approval_state_enum() -> None:
    """Test OrderApprovalState enum values."""
    assert OrderApprovalState.UNDEFINED == "Undefined"
    assert OrderApprovalState.APPROVED == "Approved"
    assert OrderApprovalState.NOT_APPROVED == "NotApproved"


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



@pytest.mark.parametrize(
    ("data", "expected_name", "expected_is_spread_block"),
    [
        (
            {
                "orderId": "order1",
                "orderType": "Block",
                "auctionId": "auction1",
                "userId": "user1",
                "companyName": "Company1",
                "portfolio": "Portfolio1",
                "currencyCode": "EUR",
                "areaCode": "DK1",
                "trades": [
                    {
                        "tradeId": "trade1",
                        "contractId": "contract1",
                        "deliveryStart": "2023-01-01T00:00:00",
                        "deliveryEnd": "2023-01-02T00:00:00",
                        "volume": 100.0,
                        "price": 50.0,
                        "side": "Buy",
                        "status": "Final",
                    },
                ],
                "name": "Block1",
                "exclusiveGroup": "Group1",
                "linkedTo": "Block2",
                "isSpreadBlock": False,
            },
            "Block1",
            False,
        ),
        (
            {
                "orderId": None,
                "orderType": "Block",
                "auctionId": None,
                "userId": None,
                "companyName": None,
                "portfolio": None,
                "currencyCode": None,
                "areaCode": None,
                "trades": None,
                "name": None,
                "exclusiveGroup": None,
                "linkedTo": None,
                "isSpreadBlock": None,
            },
            None,
            None,
        ),
    ],
)
def test_block_result_response_validation(
    data: dict,
    expected_name: str | None,
    expected_is_spread_block: bool | None,
) -> None:
    """Test BlockResultResponse model validation."""
    response = BlockResultResponse(**data)
    assert response.order_id == data.get("orderId")
    assert response.order_type == OrderResultType.BLOCK
    assert response.name == expected_name
    assert response.exclusive_group == data.get("exclusiveGroup")
    assert response.linked_to == data.get("linkedTo")
    assert response.is_spread_block == expected_is_spread_block
    if response.trades:
        assert len(response.trades) == 1
        assert response.trades[0].trade_id == "trade1"
        assert response.trades[0].side == TradeSide.BUY
        assert response.trades[0].status == AuctionResultState.FINAL

def test_combined_orders_response_validation() -> None:
    """Test CombinedOrdersResponse model validation."""
    data = {
        "curveOrders": [
            {
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
            },
        ],
        "blockLists": [
            {
                "orderId": "00000000-0000-0000-0000-000000000001",
                "auctionId": "auction2",
                "companyName": "Company2",
                "portfolio": "Portfolio2",
                "areaCode": "DK2",
                "modifier": "User2",
                "modified": "2023-01-01T00:00:00",
                "currencyCode": "EUR",
                "comment": "Test block",
                "resolutionSeconds": 3600,
                "blocks": [
                    {
                        "name": "Block1",
                        "price": 50.0,
                        "minimumAcceptanceRatio": 1.0,
                        "linkedTo": None,
                        "exclusiveGroup": None,
                        "periods": [
                            {"contractId": "contract2", "volume": 100.0},
                        ],
                        "isSpreadBlock": False,
                        "modifier": "User2",
                        "state": "Accepted",
                    },
                ],
            },
        ],
    }
    response = CombinedOrdersResponse(**data)
    assert len(response.curve_orders) == 1
    assert response.curve_orders[0].order_id == UUID(
        "00000000-0000-0000-0000-000000000000",
    )
    assert len(response.block_lists) == 1
    assert response.block_lists[0].order_id == UUID(
        "00000000-0000-0000-0000-000000000001",
    )


def test_combined_orders_response_empty() -> None:
    """Test CombinedOrdersResponse with empty lists."""
    response = CombinedOrdersResponse(curveOrders=None, blockLists=None)
    assert response.curve_orders is None
    assert response.block_lists is None



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


@pytest.mark.parametrize(
    ("data", "expected_order_id", "expected_order_type"),
    [
        (
            {
                "orderId": "order1",
                "orderType": "Curve",
                "auctionId": "auction1",
                "userId": "user1",
                "companyName": "Company1",
                "portfolio": "Portfolio1",
                "currencyCode": "EUR",
                "areaCode": "DK1",
                "trades": [
                    {
                        "tradeId": "trade1",
                        "contractId": "contract1",
                        "deliveryStart": "2023-01-01T00:00:00",
                        "deliveryEnd": "2023-01-02T00:00:00",
                        "volume": 100.0,
                        "price": 50.0,
                        "side": "Buy",
                        "status": "Final",
                    },
                ],
            },
            "order1",
            OrderResultType.CURVE,
        ),
        (
            {
                "orderId": None,
                "orderType": "Block",
                "auctionId": None,
                "userId": None,
                "companyName": None,
                "portfolio": None,
                "currencyCode": None,
                "areaCode": None,
                "trades": None,
            },
            None,
            OrderResultType.BLOCK,
        ),
    ],
)
def test_order_result_response_validation(
    data: dict,
    expected_order_id: str | None,
    expected_order_type: OrderResultType,
) -> None:
    """Test OrderResultResponse model validation."""
    response = OrderResultResponse(**data)
    assert response.order_id == expected_order_id
    assert response.order_type == expected_order_type
    assert response.auction_id == data.get("auctionId")
    assert response.user_id == data.get("userId")
    assert response.company_name == data.get("companyName")
    assert response.portfolio == data.get("portfolio")
    assert response.currency_code == data.get("currencyCode")
    assert response.area_code == data.get("areaCode")
    if response.trades:
        assert len(response.trades) == 1
        assert response.trades[0].trade_id == "trade1"
        assert response.trades[0].side == TradeSide.BUY
        assert response.trades[0].status == AuctionResultState.FINAL




def test_portfolio_volume_response_validation() -> None:
    """Test PortfolioVolumeResponse model validation."""
    data = {
        "auctionId": "auction1",
        "portfolioNetVolumes": [
            {
                "portfolio": "Portfolio1",
                "companyName": "Company1",
                "areaNetVolumes": [
                    {
                        "areaCode": "DK1",
                        "netVolumes": [
                            {
                                "netVolume": f"{VOLUME}",
                                "contractId": "contract1",
                                "deliveryStart": "2023-01-01T00:00:00",
                                "deliveryEnd": "2023-01-02T00:00:00",
                            },
                        ],
                    },
                ],
            },
        ],
    }
    response = PortfolioVolumeResponse(**data)
    assert response.auction_id == "auction1"
    assert len(response.portfolio_net_volumes) == 1
    assert response.portfolio_net_volumes[0].portfolio == "Portfolio1"
    assert len(response.portfolio_net_volumes[0].area_net_volumes) == 1
    assert response.portfolio_net_volumes[0].area_net_volumes[0].area_code == "DK1"
    assert (
        response.portfolio_net_volumes[0].area_net_volumes[0].net_volumes[0].net_volume
        == VOLUME
    )

def test_portfolio_volume_response_empty() -> None:
    """Test PortfolioVolumeResponse with empty portfolio net volumes."""
    response = PortfolioVolumeResponse(auctionId=None, portfolioNetVolumes=None)
    assert response.auction_id is None
    assert response.portfolio_net_volumes is None

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

@pytest.mark.parametrize(
    ("data", "expected_id", "expected_state"),
    [
        (
            {
                "id": "auction1",
                "name": "Test Auction",
                "state": "Open",
                "closeForBidding": "2023-01-01T00:00:00",
                "deliveryStart": "2023-01-02T00:00:00",
                "deliveryEnd": "2023-01-03T00:00:00",
            },
            "auction1",
            AuctionStateType.OPEN,
        ),
        (
            {
                "id": None,
                "name": None,
                "state": "Closed",
                "closeForBidding": "2023-01-01T00:00:00",
                "deliveryStart": "2023-01-02T00:00:00",
                "deliveryEnd": "2023-01-03T00:00:00",
            },
            None,
            AuctionStateType.CLOSED,
        ),
    ],
)
def test_auction_multi_resolution_response_validation(
    data: dict,
    expected_id: str | None,
    expected_state: AuctionStateType,
) -> None:
    """Test AuctionMultiResolutionResponse model validation."""
    auction = AuctionMultiResolutionResponse(**data)
    assert auction.id == expected_id
    assert auction.name == data.get("name")
    assert auction.state == expected_state
    assert auction.close_for_bidding == datetime(2023, 1, 1)  # noqa: DTZ001
    assert auction.delivery_start == datetime(2023, 1, 2)  # noqa: DTZ001
    assert auction.delivery_end == datetime(2023, 1, 3)  # noqa: DTZ001


def test_auction_multi_resolution_response_with_nested_fields() -> None:
    """Test AuctionMultiResolutionResponse with nested fields."""
    data = {
        "id": "auction1",
        "name": "Test Auction",
        "state": "Open",
        "closeForBidding": "2023-01-01T00:00:00",
        "deliveryStart": "2023-01-02T00:00:00",
        "deliveryEnd": "2023-01-03T00:00:00",
        "availableOrderTypes": [{"id": 1, "name": "Curve"}],
        "currencies": [{"currencyCode": "EUR", "minPrice": 0.0, "maxPrice": 100.0}],
        "contracts": [
            {
                "areaCode": "DK1",
                "contracts": [
                    {
                        "id": "contract1",
                        "deliveryStart": "2023-01-02T00:00:00",
                        "deliveryEnd": "2023-01-03T00:00:00",
                    },
                ],
            },
        ],
        "portfolios": [
            {
                "name": "Portfolio1",
                "id": "p1",
                "currency": "EUR",
                "companyId": "c1",
                "companyName": "Company1",
                "permission": "read",
                "areas": [
                    {
                        "code": "DK1",
                        "name": "Denmark 1",
                        "eicCode": "EIC1",
                        "curveMinVolumeLimit": 0.0,
                        "curveMaxVolumeLimit": 1000.0,
                        "auctionTradingResolution": 3600,
                    },
                ],
            },
        ],
    }
    auction = AuctionMultiResolutionResponse(**data)
    assert auction.id == "auction1"
    assert len(auction.available_order_types) == 1
    assert auction.available_order_types[0].id == 1
    assert len(auction.currencies) == 1
    assert auction.currencies[0].currency_code == "EUR"
    assert len(auction.contracts) == 1
    assert auction.contracts[0].area_code == "DK1"
    assert len(auction.portfolios) == 1
    assert auction.portfolios[0].name == "Portfolio1"


def test_auction_multi_resolution_response_invalid_state() -> None:
    """Test AuctionMultiResolutionResponse with invalid state."""
    data = {
        "id": "auction1",
        "name": "Test Auction",
        "state": "InvalidState",
        "closeForBidding": "2023-01-01T00:00:00",
        "deliveryStart": "2023-01-02T00:00:00",
        "deliveryEnd": "2023-01-03T00:00:00",
    }
    with pytest.raises(ValidationError):
        AuctionMultiResolutionResponse(**data)


def test_auction_price_validation() -> None:
    """Test AuctionPrice model validation."""
    data = {
        "auction": "auction1",
        "auctionDeliveryStart": "2023-01-01T00:00:00",
        "auctionDeliveryEnd": "2023-01-02T00:00:00",
        "contracts": [
            {
                "contractId": "contract1",
                "deliveryStart": "2023-01-01T00:00:00",
                "deliveryEnd": "2023-01-02T00:00:00",
                "areas": [
                    {
                        "areaCode": "DK1",
                        "prices": [
                            {
                                "currencyCode": "EUR",
                                "marketPrice": 50.0,
                                "status": "Final",
                            },
                        ],
                    },
                ],
            },
        ],
    }
    response = AuctionPrice(**data)
    assert response.auction == "auction1"
    assert response.auction_delivery_start == datetime(2023, 1, 1)  # noqa: DTZ001
    assert response.auction_delivery_end == datetime(2023, 1, 2)  # noqa: DTZ001
    assert len(response.contracts) == 1
    assert response.contracts[0].contract_id == "contract1"
    assert len(response.contracts[0].areas) == 1
    assert response.contracts[0].areas[0].area_code == "DK1"
    assert response.contracts[0].areas[0].prices[0].status == AuctionResultState.FINAL


def test_auction_price_empty_contracts() -> None:
    """Test AuctionPrice with empty contracts."""
    data = {
        "auction": None,
        "auctionDeliveryStart": "2023-01-01T00:00:00",
        "auctionDeliveryEnd": "2023-01-02T00:00:00",
        "contracts": None,
    }
    response = AuctionPrice(**data)
    assert response.auction is None
    assert response.contracts is None



@pytest.mark.parametrize(
    ("data", "expected_id", "expected_state"),
    [
        (
            {
                "id": "auction1",
                "name": "Test Auction",
                "state": "Open",
                "closeForBidding": "2023-01-01T00:00:00",
                "deliveryStart": "2023-01-02T00:00:00",
                "deliveryEnd": "2023-01-03T00:00:00",
            },
            "auction1",
            AuctionStateType.OPEN,
        ),
        (
            {
                "id": None,
                "name": None,
                "state": "Closed",
                "closeForBidding": "2023-01-01T00:00:00",
                "deliveryStart": "2023-01-02T00:00:00",
                "deliveryEnd": "2023-01-03T00:00:00",
            },
            None,
            AuctionStateType.CLOSED,
        ),
    ],
)
def test_auction_response_validation(
    data: dict,
    expected_id: str | None,
    expected_state: AuctionStateType,
) -> None:
    """Test AuctionResponse model validation."""
    auction = AuctionResponse(**data)
    assert auction.id == expected_id
    assert auction.name == data.get("name")
    assert auction.state == expected_state
    assert auction.close_for_bidding == datetime(2023, 1, 1)# noqa: DTZ001
    assert auction.delivery_start == datetime(2023, 1, 2)# noqa: DTZ001
    assert auction.delivery_end == datetime(2023, 1, 3)  # noqa: DTZ001


def test_auction_response_with_nested_fields() -> None:
    """Test AuctionResponse with nested fields like currencies and contracts."""
    data = {
        "id": "auction1",
        "name": "Test Auction",
        "state": "Open",
        "closeForBidding": "2023-01-01T00:00:00",
        "deliveryStart": "2023-01-02T00:00:00",
        "deliveryEnd": "2023-01-03T00:00:00",
        "availableOrderTypes": [{"id": 1, "name": "Curve"}],
        "currencies": [{"currencyCode": "EUR", "minPrice": 0.0, "maxPrice": 100.0}],
        "contracts": [
            {
                "id": "contract1",
                "deliveryStart": "2023-01-02T00:00:00",
                "deliveryEnd": "2023-01-03T00:00:00",
            },
        ],
        "portfolios": [
            {
                "name": "Portfolio1",
                "id": "p1",
                "currency": "EUR",
                "companyId": "c1",
                "companyName": "Company1",
                "permission": "read",
                "areas": [
                    {
                        "code": "DK1",
                        "name": "Denmark 1",
                        "eicCode": "EIC1",
                        "curveMinVolumeLimit": 0.0,
                        "curveMaxVolumeLimit": 1000.0,
                        "auctionTradingResolution": 3600,
                    },
                ],
            },
        ],
    }
    auction = AuctionResponse(**data)
    assert auction.id == "auction1"
    assert len(auction.available_order_types) == 1
    assert auction.available_order_types[0].id == 1
    assert len(auction.currencies) == 1
    assert auction.currencies[0].currency_code == "EUR"
    assert len(auction.contracts) == 1
    assert auction.contracts[0].id == "contract1"
    assert len(auction.portfolios) == 1
    assert auction.portfolios[0].name == "Portfolio1"


def test_auction_response_invalid_state() -> None:
    """Test AuctionResponse with invalid state."""
    data = {
        "id": "auction1",
        "name": "Test Auction",
        "state": "InvalidState",
        "closeForBidding": "2023-01-01T00:00:00",
        "deliveryStart": "2023-01-02T00:00:00",
        "deliveryEnd": "2023-01-03T00:00:00",
    }
    with pytest.raises(ValidationError):
        AuctionResponse(**data)
