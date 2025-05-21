from datetime import datetime
from uuid import UUID

import pytest
from pydantic import ValidationError

from app.constants.time_zones import PARIS_TZ
from app.services.nordpool.schema.base_schema import ApprovalSource
from app.services.nordpool.schema.base_schema import AreaContractGroup
from app.services.nordpool.schema.base_schema import AreaNetVolume
from app.services.nordpool.schema.base_schema import AreaPrice
from app.services.nordpool.schema.base_schema import AuctionPortfolio
from app.services.nordpool.schema.base_schema import AuctionResultState
from app.services.nordpool.schema.base_schema import AuctionStateType
from app.services.nordpool.schema.base_schema import Block
from app.services.nordpool.schema.base_schema import BlockPeriod
from app.services.nordpool.schema.base_schema import BlockResponse
from app.services.nordpool.schema.base_schema import Contract
from app.services.nordpool.schema.base_schema import ContractNetVolume
from app.services.nordpool.schema.base_schema import ContractPrice
from app.services.nordpool.schema.base_schema import Currency
from app.services.nordpool.schema.base_schema import CurrencyPrice
from app.services.nordpool.schema.base_schema import Curve
from app.services.nordpool.schema.base_schema import CurvePoint
from app.services.nordpool.schema.base_schema import Order
from app.services.nordpool.schema.base_schema import OrderApprovalState
from app.services.nordpool.schema.base_schema import OrderResponse
from app.services.nordpool.schema.base_schema import OrderResultType
from app.services.nordpool.schema.base_schema import OrderStateType
from app.services.nordpool.schema.base_schema import OrderType
from app.services.nordpool.schema.base_schema import PortfolioArea
from app.services.nordpool.schema.base_schema import PortfolioNetVolume
from app.services.nordpool.schema.base_schema import Trade
from app.services.nordpool.schema.base_schema import TradeSide
from app.services.nordpool.schema.base_schema import ValidatedCurve


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
