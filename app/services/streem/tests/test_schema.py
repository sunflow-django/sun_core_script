from datetime import datetime
from uuid import UUID
from zoneinfo import ZoneInfo

import pytest
from pydantic import ValidationError

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
from app.services.nordpool.schema import BlockList
from app.services.nordpool.schema import BlockListResponse
from app.services.nordpool.schema import BlockOrderPatch
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
from app.services.nordpool.schema import CurveOrder
from app.services.nordpool.schema import CurveOrderPatch
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


# Constants for test data
PRICE = 100.0
VOLUME = 200.0
MAX_VOLUME = 1000.0
TRADING_RESOLUTION = 3600
MARKET_PRICE = 50.0
TEST_UUID = UUID("00000000-0000-0000-0000-000000000000")
TEST_DATE = datetime(2023, 1, 1, tzinfo=ZoneInfo("Europe/Paris"))
TEST_END_DATE = datetime(2023, 1, 2, tzinfo=ZoneInfo("Europe/Paris"))


@pytest.fixture
def curve_point() -> CurvePoint:
    """Fixture for a CurvePoint instance."""
    return CurvePoint(price=MARKET_PRICE, volume=VOLUME)


@pytest.fixture
def curve(curve_point: CurvePoint) -> Curve:
    """Fixture for a Curve instance."""
    return Curve(contractId="contract1", curvePoints=[curve_point])


@pytest.fixture
def block_period() -> BlockPeriod:
    """Fixture for a BlockPeriod instance."""
    return BlockPeriod(contractId="contract1", volume=VOLUME)


@pytest.fixture
def block(block_period: BlockPeriod) -> Block:
    """Fixture for a Block instance."""
    return Block(
        name="Block1",
        price=MARKET_PRICE,
        minimumAcceptanceRatio=1.0,
        linkedTo="block2",
        exclusiveGroup="group1",
        periods=[block_period],
        isSpreadBlock=False,
    )


@pytest.fixture
def contract() -> Contract:
    """Fixture for a Contract instance."""
    return Contract(
        id="contract1",
        deliveryStart=TEST_DATE,
        deliveryEnd=TEST_END_DATE,
    )


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


def test_trade_side_enum() -> None:
    """Test TradeSide enum values."""
    assert TradeSide.BUY == "Buy"
    assert TradeSide.SELL == "Sell"


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


def test_contract_validation(contract: Contract) -> None:
    """Test Contract model validation."""
    assert contract.id == "contract1"
    assert contract.delivery_start == TEST_DATE
    assert contract.delivery_end == TEST_END_DATE


def test_area_contract_group_validation(contract: Contract) -> None:
    """Test AreaContractGroup model validation."""
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
        deliveryStart=TEST_DATE,
        deliveryEnd=TEST_END_DATE,
    )
    assert net_volume.net_volume == VOLUME
    assert net_volume.contract_id == "contract1"
    assert net_volume.delivery_start == TEST_DATE
    assert net_volume.delivery_end == TEST_END_DATE


def test_area_net_volume_validation() -> None:
    """Test AreaNetVolume model validation."""
    net_volume = ContractNetVolume(
        netVolume=VOLUME,
        contractId="contract1",
        deliveryStart=TEST_DATE,
        deliveryEnd=TEST_END_DATE,
    )
    area_net = AreaNetVolume(areaCode="DK1", netVolumes=[net_volume])
    assert area_net.area_code == "DK1"
    assert len(area_net.net_volumes) == 1


def test_portfolio_net_volume_validation() -> None:
    """Test PortfolioNetVolume model validation."""
    net_volume = ContractNetVolume(
        netVolume=VOLUME,
        contractId="contract1",
        deliveryStart=TEST_DATE,
        deliveryEnd=TEST_END_DATE,
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
        deliveryStart=TEST_DATE,
        deliveryEnd=TEST_END_DATE,
        areas=[area_price],
    )
    assert contract_price.contract_id == "contract1"
    assert len(contract_price.areas) == 1


def test_block_period_validation(block_period: BlockPeriod) -> None:
    """Test BlockPeriod model validation."""
    assert block_period.contract_id == "contract1"
    assert block_period.volume == VOLUME


def test_block_validation(block: Block) -> None:
    """Test Block model validation."""
    assert block.name == "Block1"
    assert block.price == MARKET_PRICE
    assert block.minimum_acceptance_ratio == 1.0
    assert block.linked_to == "block2"
    assert block.exclusive_group == "group1"
    assert len(block.periods) == 1
    assert block.is_spread_block is False


def test_block_response_validation(block_period: BlockPeriod) -> None:
    """Test BlockResponse model validation."""
    block_response = BlockResponse(
        name="Block1",
        price=MARKET_PRICE,
        minimumAcceptanceRatio=1.0,
        linkedTo="block2",
        exclusiveGroup="group1",
        periods=[block_period],
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


def test_curve_order_validation(curve: Curve) -> None:
    """Test CurveOrder model validation."""
    order = CurveOrder(
        auctionId="auction1",
        portfolio="Portfolio1",
        areaCode="DK1",
        comment="Test comment",
        curves=[curve],
    )
    assert order.auction_id == "auction1"
    assert order.portfolio == "Portfolio1"
    assert order.area_code == "DK1"
    assert order.comment == "Test comment"
    assert len(order.curves) == 1
    assert order.curves[0].contract_id == "contract1"


def test_block_list_validation(block: Block) -> None:
    """Test BlockList model validation."""
    block_list = BlockList(
        auctionId="auction1",
        portfolio="Portfolio1",
        areaCode="DK1",
        comment="Test comment",
        blocks=[block],
    )
    assert block_list.auction_id == "auction1"
    assert block_list.portfolio == "Portfolio1"
    assert block_list.area_code == "DK1"
    assert block_list.comment == "Test comment"
    assert len(block_list.blocks) == 1
    assert block_list.blocks[0].name == "Block1"


def test_block_order_patch_validation(block: Block) -> None:
    """Test BlockOrderPatch model validation."""
    patch = BlockOrderPatch(
        blocks=[block],
        comment="Test comment",
    )
    assert len(patch.blocks) == 1
    assert patch.blocks[0].name == "Block1"
    assert patch.comment == "Test comment"


def test_order_response_validation() -> None:
    """Test OrderResponse model validation."""
    order_response = OrderResponse(
        orderId=TEST_UUID,
        auctionId="auction1",
        companyName="Company1",
        portfolio="Portfolio1",
        areaCode="DK1",
        modifier="User1",
        modified=TEST_DATE,
        currencyCode="EUR",
        comment="Test comment",
        resolutionSeconds=TRADING_RESOLUTION,
    )
    assert order_response.order_id == TEST_UUID
    assert order_response.auction_id == "auction1"
    assert order_response.company_name == "Company1"
    assert order_response.currency_code == "EUR"


def test_trade_validation() -> None:
    """Test Trade model validation."""
    trade = Trade(
        tradeId="trade1",
        contractId="contract1",
        deliveryStart=TEST_DATE,
        deliveryEnd=TEST_END_DATE,
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


def test_curve_point_validation(curve_point: CurvePoint) -> None:
    """Test CurvePoint model validation."""
    assert curve_point.price == MARKET_PRICE
    assert curve_point.volume == VOLUME


def test_curve_validation(curve: Curve) -> None:
    """Test Curve model validation."""
    assert curve.contract_id == "contract1"
    assert len(curve.curve_points) == 1


def test_validated_curve_validation() -> None:
    """Test ValidatedCurve model validation."""
    curve = ValidatedCurve(
        id=TEST_UUID,
        timeStep=TRADING_RESOLUTION,
        contractId="contract1",
        isValid=True,
        validationMessage="Valid",
    )
    assert curve.id == TEST_UUID
    assert curve.time_step == TRADING_RESOLUTION
    assert curve.contract_id == "contract1"
    assert curve.is_valid is True
    assert curve.validation_message == "Valid"


def test_block_list_response_validation(block: Block) -> None:
    """Test BlockListResponse model validation."""
    data = {
        "orderId": str(TEST_UUID),
        "auctionId": "auction1",
        "companyName": "Company1",
        "portfolio": "Portfolio1",
        "areaCode": "DK1",
        "modifier": "User1",
        "modified": TEST_DATE.isoformat(),
        "currencyCode": "EUR",
        "comment": "Test comment",
        "resolutionSeconds": TRADING_RESOLUTION,
        "blocks": [
            {
                "name": "Block1",
                "price": MARKET_PRICE,
                "minimumAcceptanceRatio": 1.0,
                "linkedTo": "block2",
                "exclusiveGroup": "group1",
                "periods": [
                    {"contractId": "contract1", "volume": VOLUME},
                ],
                "isSpreadBlock": False,
                "modifier": "User1",
                "state": "Accepted",
            },
        ],
    }
    response = BlockListResponse(**data)
    assert response.order_id == TEST_UUID
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
        "orderId": str(TEST_UUID),
        "auctionId": "auction1",
        "companyName": "Company1",
        "portfolio": "Portfolio1",
        "areaCode": "DK1",
        "modifier": "User1",
        "modified": TEST_DATE.isoformat(),
        "currencyCode": "EUR",
        "comment": "Test comment",
        "resolutionSeconds": TRADING_RESOLUTION,
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
                        "deliveryStart": TEST_DATE.isoformat(),
                        "deliveryEnd": TEST_END_DATE.isoformat(),
                        "volume": VOLUME,
                        "price": MARKET_PRICE,
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


def test_curve_order_patch_sort(curve: Curve) -> None:
    """Test CurveOrderPatch.sort method for in-place sorting."""
    curve2 = Curve(contractId="contract2", curvePoints=[CurvePoint(price=MARKET_PRICE, volume=VOLUME)])
    patch = CurveOrderPatch(curves=[curve2, curve], comment="Test")
    patch.sort()
    assert patch.curves[0].contract_id == "contract1"
    assert patch.curves[1].contract_id == "contract2"


def test_curve_order_patch_sorted(curve: Curve) -> None:
    """Test CurveOrderPatch.sorted method for returning a sorted copy."""
    curve2 = Curve(contractId="contract2", curvePoints=[CurvePoint(price=MARKET_PRICE, volume=VOLUME)])
    patch = CurveOrderPatch(curves=[curve2, curve], comment="Test")
    sorted_patch = patch.sorted()
    assert sorted_patch.curves[0].contract_id == "contract1"
    assert sorted_patch.curves[1].contract_id == "contract2"
    assert patch.curves[0].contract_id == "contract2"  # Original unchanged
    assert patch.comment == sorted_patch.comment


def test_curve_order_patch_zero_volumes(curve: Curve) -> None:
    """Test CurveOrderPatch.zero_volumes method for setting volumes to zero."""
    patch = CurveOrderPatch(curves=[curve], comment="Test")
    zeroed_patch = patch.zero_volumes()
    assert zeroed_patch.curves[0].curve_points[0].volume == 0.0
    assert zeroed_patch.curves[0].curve_points[0].price == MARKET_PRICE  # Price unchanged
    assert patch.curves[0].curve_points[0].volume == VOLUME  # Original unchanged
    assert zeroed_patch.comment == "Test"


def test_curve_order_response_sort(curve: Curve) -> None:
    """Test CurveOrderResponse.sort method for in-place sorting."""
    curve2 = Curve(contractId="contract2", curvePoints=[CurvePoint(price=MARKET_PRICE, volume=VOLUME)])
    response = CurveOrderResponse(
        orderId=TEST_UUID,
        auctionId="auction1",
        companyName="Company1",
        portfolio="Portfolio1",
        areaCode="DK1",
        modifier="User1",
        modified=TEST_DATE,
        currencyCode="EUR",
        comment="Test comment",
        resolutionSeconds=TRADING_RESOLUTION,
        state=OrderStateType.ACCEPTED,
        curves=[curve2, curve],
    )
    response.sort()
    assert response.curves[0].contract_id == "contract1"
    assert response.curves[1].contract_id == "contract2"


def test_curve_order_response_sorted(curve: Curve) -> None:
    """Test CurveOrderResponse.sorted method for returning a sorted copy."""
    curve2 = Curve(contractId="contract2", curvePoints=[CurvePoint(price=MARKET_PRICE, volume=VOLUME)])
    response = CurveOrderResponse(
        orderId=TEST_UUID,
        auctionId="auction1",
        companyName="Company1",
        portfolio="Portfolio1",
        areaCode="DK1",
        modifier="User1",
        modified=TEST_DATE,
        currencyCode="EUR",
        comment="Test comment",
        resolutionSeconds=TRADING_RESOLUTION,
        state=OrderStateType.ACCEPTED,
        curves=[curve2, curve],
    )
    sorted_response = response.sorted()
    assert sorted_response.curves[0].contract_id == "contract1"
    assert sorted_response.curves[1].contract_id == "contract2"
    assert response.curves[0].contract_id == "contract2"  # Original unchanged
    assert sorted_response.comment == response.comment


def test_curve_order_response_to_curve_order_patch(curve: Curve) -> None:
    """Test CurveOrderResponse.to_curve_order_patch method."""
    response = CurveOrderResponse(
        orderId=TEST_UUID,
        auctionId="auction1",
        companyName="Company1",
        portfolio="Portfolio1",
        areaCode="DK1",
        modifier="User1",
        modified=TEST_DATE,
        currencyCode="EUR",
        comment="Test comment",
        resolutionSeconds=TRADING_RESOLUTION,
        state=OrderStateType.ACCEPTED,
        curves=[curve],
    )
    patch = response.to_curve_order_patch()
    assert patch.curves[0].contract_id == "contract1"
    assert patch.curves[0].curve_points[0].volume == VOLUME
    assert patch.comment == "Test comment"
    assert response.curves[0].curve_points[0].volume == VOLUME  # Original unchanged


@pytest.mark.parametrize(
    ("curves", "expected_invalid"),
    [
        (
            [
                ValidatedCurve(
                    id=TEST_UUID,
                    timeStep=TRADING_RESOLUTION,
                    contractId="contract1",
                    isValid=True,
                    validationMessage="Valid",
                ),
                ValidatedCurve(
                    id=TEST_UUID,
                    timeStep=TRADING_RESOLUTION,
                    contractId="contract2",
                    isValid=False,
                    validationMessage="Invalid",
                ),
                ValidatedCurve(
                    id=TEST_UUID,
                    timeStep=TRADING_RESOLUTION,
                    contractId="contract3",
                    isValid=None,
                    validationMessage="Unknown",
                ),
            ],
            ["contract2", "contract3"],
        ),
        ([], []),
        (None, []),
    ],
)
def test_reasonability_results_info_extract_invalid_curves(
    curves: list[ValidatedCurve] | None,
    expected_invalid: list[str],
) -> None:
    """Test ReasonabilityResultsInfo.extract_invalid_curves method."""
    info = ReasonabilityResultsInfo(
        portfolio="Portfolio1",
        area="DK1",
        orderApprovalState=OrderApprovalState.APPROVED,
        curves=curves,
        referenceDay="2023-01-01",
        auctionId="auction1",
        orderId=TEST_UUID,
        approvalModifier="User1",
        approvalSource=ApprovalSource.AUTOMATIC,
    )
    invalid_curves = info.extract_invalid_curves()
    assert len(invalid_curves) == len(expected_invalid)
    assert [curve.contract_id for curve in invalid_curves] == expected_invalid


def test_combined_orders_response_validation(curve: Curve, block: Block) -> None:
    """Test CombinedOrdersResponse model validation."""
    data = {
        "curveOrders": [
            {
                "orderId": str(TEST_UUID),
                "auctionId": "auction1",
                "companyName": "Company1",
                "portfolio": "Portfolio1",
                "areaCode": "DK1",
                "modifier": "User1",
                "modified": TEST_DATE.isoformat(),
                "currencyCode": "EUR",
                "comment": "Test comment",
                "resolutionSeconds": TRADING_RESOLUTION,
                "state": "Accepted",
                "curves": [
                    {
                        "contractId": "contract1",
                        "curvePoints": [
                            {"price": MARKET_PRICE, "volume": VOLUME},
                        ],
                    },
                ],
            },
        ],
        "blockLists": [
            {
                "orderId": str(UUID("00000000-0000-0000-0000-000000000001")),
                "auctionId": "auction2",
                "companyName": "Company2",
                "portfolio": "Portfolio2",
                "areaCode": "DK2",
                "modifier": "User2",
                "modified": TEST_DATE.isoformat(),
                "currencyCode": "EUR",
                "comment": "Test block",
                "resolutionSeconds": TRADING_RESOLUTION,
                "blocks": [
                    {
                        "name": "Block1",
                        "price": MARKET_PRICE,
                        "minimumAcceptanceRatio": 1.0,
                        "linkedTo": None,
                        "exclusiveGroup": None,
                        "periods": [
                            {"contractId": "contract2", "volume": VOLUME},
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
    assert response.curve_orders[0].order_id == TEST_UUID
    assert len(response.block_lists) == 1
    assert response.block_lists[0].order_id == UUID("00000000-0000-0000-0000-000000000001")


def test_combined_orders_response_list_orders_details(curve: Curve, block: Block) -> None:
    """Test CombinedOrdersResponse.list_orders_details method."""
    response = CombinedOrdersResponse(
        curveOrders=[
            CurveOrderResponse(
                orderId=TEST_UUID,
                auctionId="auction1",
                companyName="Company1",
                portfolio="Portfolio1",
                areaCode="DK1",
                modifier="User1",
                modified=TEST_DATE,
                currencyCode="EUR",
                comment="Test comment",
                resolutionSeconds=TRADING_RESOLUTION,
                state=OrderStateType.ACCEPTED,
                curves=[curve],
            ),
        ],
        blockLists=[
            BlockListResponse(
                orderId=UUID("00000000-0000-0000-0000-000000000001"),
                auctionId="auction2",
                companyName="Company2",
                portfolio="Portfolio2",
                areaCode="DK2",
                modifier="User2",
                modified=TEST_DATE,
                currencyCode="EUR",
                comment="Test block",
                resolutionSeconds=TRADING_RESOLUTION,
                blocks=[
                    BlockResponse(
                        name="Block1",
                        price=MARKET_PRICE,
                        minimumAcceptanceRatio=1.0,
                        linkedTo=None,
                        exclusiveGroup=None,
                        periods=[BlockPeriod(contractId="contract2", volume=VOLUME)],
                        isSpreadBlock=False,
                        modifier="User2",
                        state=OrderStateType.ACCEPTED,
                    ),
                ],
            ),
        ],
    )
    details = response.list_orders_details()
    assert len(details) == 2  # noqa: PLR2004
    assert details[0] == {
        "order_id": str(TEST_UUID),
        "auction_id": "auction1",
        "state": "Accepted",
        "modified": TEST_DATE.isoformat(),
        "type": "Curve",
    }
    assert details[1] == {
        "order_id": str(UUID("00000000-0000-0000-0000-000000000001")),
        "auction_id": "auction2",
        "state": "Accepted",
        "modified": TEST_DATE.isoformat(),
        "type": "Block",
    }


@pytest.mark.parametrize(
    ("curve_orders", "auction_id", "expected_order_id", "expect_error"),
    [
        (
            [
                CurveOrderResponse(
                    orderId=TEST_UUID,
                    auctionId="auction1",
                    companyName="Company1",
                    portfolio="Portfolio1",
                    areaCode="DK1",
                    modifier="User1",
                    modified=TEST_DATE,
                    currencyCode="EUR",
                    comment="Test comment",
                    resolutionSeconds=TRADING_RESOLUTION,
                    state=OrderStateType.ACCEPTED,
                    curves=[],
                ),
            ],
            "auction1",
            TEST_UUID,
            False,
        ),
        ([], "auction1", None, False),
        (
            [
                CurveOrderResponse(
                    orderId=TEST_UUID,
                    auctionId="auction1",
                    companyName="Company1",
                    portfolio="Portfolio1",
                    areaCode="DK1",
                    modifier="User1",
                    modified=TEST_DATE,
                    currencyCode="EUR",
                    comment="Test comment",
                    resolutionSeconds=TRADING_RESOLUTION,
                    state=OrderStateType.ACCEPTED,
                    curves=[],
                ),
                CurveOrderResponse(
                    orderId=UUID("00000000-0000-0000-0000-000000000001"),
                    auctionId="auction1",
                    companyName="Company2",
                    portfolio="Portfolio2",
                    areaCode="DK2",
                    modifier="User2",
                    modified=TEST_DATE,
                    currencyCode="EUR",
                    comment="Test comment 2",
                    resolutionSeconds=TRADING_RESOLUTION,
                    state=OrderStateType.ACCEPTED,
                    curves=[],
                ),
            ],
            "auction1",
            None,
            True,
        ),
    ],
)
def test_combined_orders_response_select_curve_order_by_auction_id(
    curve_orders: list[CurveOrderResponse],
    auction_id: str,
    expected_order_id: UUID | None,
    *,
    expect_error: bool,
) -> None:
    """Test CombinedOrdersResponse.select_curve_order_by_auction_id method."""
    response = CombinedOrdersResponse(curveOrders=curve_orders, blockLists=None)
    if expect_error:
        with pytest.raises(ValueError, match=f"Multiple CurveOrderResponse found for auction_id: {auction_id}"):
            response.select_curve_order_by_auction_id(auction_id)
    else:
        result = response.select_curve_order_by_auction_id(auction_id)
        assert result == expected_order_id


@pytest.mark.parametrize(
    ("curve_orders", "block_lists", "expected_counts"),
    [
        (
            [
                CurveOrderResponse(
                    orderId=TEST_UUID,
                    auctionId="auction1",
                    companyName="Company1",
                    portfolio="Portfolio1",
                    areaCode="DK1",
                    modifier="User1",
                    modified=TEST_DATE,
                    currencyCode="EUR",
                    comment="Test comment",
                    resolutionSeconds=TRADING_RESOLUTION,
                    state=OrderStateType.ACCEPTED,
                    curves=[],
                ),
                CurveOrderResponse(
                    orderId=UUID("00000000-0000-0000-0000-000000000001"),
                    auctionId="auction2",
                    companyName="Company2",
                    portfolio="Portfolio2",
                    areaCode="DK2",
                    modifier="User2",
                    modified=TEST_DATE,
                    currencyCode="EUR",
                    comment="Test comment 2",
                    resolutionSeconds=TRADING_RESOLUTION,
                    state=OrderStateType.CANCELLED,
                    curves=[],
                ),
            ],
            [
                BlockListResponse(
                    orderId=UUID("00000000-0000-0000-0000-000000000002"),
                    auctionId="auction3",
                    companyName="Company3",
                    portfolio="Portfolio3",
                    areaCode="DK3",
                    modifier="User3",
                    modified=TEST_DATE,
                    currencyCode="EUR",
                    comment="Test block",
                    resolutionSeconds=TRADING_RESOLUTION,
                    blocks=[
                        BlockResponse(
                            name="Block1",
                            price=MARKET_PRICE,
                            minimumAcceptanceRatio=1.0,
                            linkedTo=None,
                            exclusiveGroup=None,
                            periods=[BlockPeriod(contractId="contract2", volume=VOLUME)],
                            isSpreadBlock=False,
                            modifier="User3",
                            state=OrderStateType.ACCEPTED,
                        ),
                    ],
                ),
            ],
            {
                "CurveOrder": {"Accepted": 1, "Cancelled": 1},
                "BlockOrder": {"Accepted": 1},
            },
        ),
        ([], [], {"CurveOrder": {}, "BlockOrder": {}}),
        (None, None, {"CurveOrder": {}, "BlockOrder": {}}),
    ],
)
def test_combined_orders_response_count_by_state_and_type(
    curve_orders: list[CurveOrderResponse] | None,
    block_lists: list[BlockListResponse] | None,
    expected_counts: dict,
) -> None:
    """Test CombinedOrdersResponse.count_by_state_and_type method."""
    response = CombinedOrdersResponse(curveOrders=curve_orders, blockLists=block_lists)
    counts = response.count_by_state_and_type()
    assert counts == expected_counts


def test_combined_orders_response_empty() -> None:
    """Test CombinedOrdersResponse with empty lists."""
    response = CombinedOrdersResponse(curveOrders=None, blockLists=None)
    assert response.curve_orders is None
    assert response.block_lists is None


def test_curve_order_response_validation(curve: Curve) -> None:
    """Test CurveOrderResponse model validation."""
    data = {
        "orderId": str(TEST_UUID),
        "auctionId": "auction1",
        "companyName": "Company1",
        "portfolio": "Portfolio1",
        "areaCode": "DK1",
        "modifier": "User1",
        "modified": TEST_DATE.isoformat(),
        "currencyCode": "EUR",
        "comment": "Test comment",
        "resolutionSeconds": TRADING_RESOLUTION,
        "state": "Accepted",
        "curves": [
            {
                "contractId": "contract1",
                "curvePoints": [
                    {"price": MARKET_PRICE, "volume": VOLUME},
                ],
            },
        ],
    }
    response = CurveOrderResponse(**data)
    assert response.order_id == TEST_UUID
    assert response.auction_id == "auction1"
    assert response.company_name == "Company1"
    assert response.state == OrderStateType.ACCEPTED
    assert len(response.curves) == 1
    assert response.curves[0].contract_id == "contract1"
    assert len(response.curves[0].curve_points) == 1
    assert response.curves[0].curve_points[0].price == MARKET_PRICE


def test_curve_order_response_invalid_state() -> None:
    """Test CurveOrderResponse with invalid state."""
    data = {
        "orderId": str(TEST_UUID),
        "auctionId": "auction1",
        "companyName": "Company1",
        "portfolio": "Portfolio1",
        "areaCode": "DK1",
        "modifier": "User1",
        "modified": TEST_DATE.isoformat(),
        "currencyCode": "EUR",
        "comment": "Test comment",
        "resolutionSeconds": TRADING_RESOLUTION,
        "state": "InvalidState",
        "curves": None,
    }
    with pytest.raises(ValidationError):
        CurveOrderResponse(**data)


def test_curve_order_response_empty_curves() -> None:
    """Test CurveOrderResponse with empty curves."""
    data = {
        "orderId": str(TEST_UUID),
        "auctionId": "auction1",
        "companyName": "Company1",
        "portfolio": "Portfolio1",
        "areaCode": "DK1",
        "modifier": "User1",
        "modified": TEST_DATE.isoformat(),
        "currencyCode": "EUR",
        "comment": "Test comment",
        "resolutionSeconds": TRADING_RESOLUTION,
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
                        "deliveryStart": TEST_DATE.isoformat(),
                        "deliveryEnd": TEST_END_DATE.isoformat(),
                        "volume": VOLUME,
                        "price": MARKET_PRICE,
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
                                "netVolume": VOLUME,  # Fixed: Use float instead of string
                                "contractId": "contract1",
                                "deliveryStart": TEST_DATE.isoformat(),
                                "deliveryEnd": TEST_END_DATE.isoformat(),
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
    assert response.portfolio_net_volumes[0].area_net_volumes[0].net_volumes[0].net_volume == VOLUME


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
                        "id": str(TEST_UUID),
                        "timeStep": TRADING_RESOLUTION,
                        "contractId": "contract1",
                        "isValid": True,
                        "validationMessage": "Valid",
                    },
                ],
                "referenceDay": "2023-01-01",
                "auctionId": "auction1",
                "orderId": str(TEST_UUID),
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
                "orderId": str(TEST_UUID),
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
    assert response.order_id == TEST_UUID
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
        "orderId": str(TEST_UUID),
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
                "closeForBidding": TEST_DATE.isoformat(),
                "deliveryStart": TEST_DATE.isoformat(),
                "deliveryEnd": TEST_END_DATE.isoformat(),
            },
            "auction1",
            AuctionStateType.OPEN,
        ),
        (
            {
                "id": None,
                "name": None,
                "state": "Closed",
                "closeForBidding": TEST_DATE.isoformat(),
                "deliveryStart": TEST_DATE.isoformat(),
                "deliveryEnd": TEST_END_DATE.isoformat(),
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
    assert auction.close_for_bidding == TEST_DATE
    assert auction.delivery_start == TEST_DATE
    assert auction.delivery_end == TEST_END_DATE


def test_auction_multi_resolution_response_with_nested_fields() -> None:
    """Test AuctionMultiResolutionResponse with nested fields."""
    data = {
        "id": "auction1",
        "name": "Test Auction",
        "state": "Open",
        "closeForBidding": TEST_DATE.isoformat(),
        "deliveryStart": TEST_DATE.isoformat(),
        "deliveryEnd": TEST_END_DATE.isoformat(),
        "availableOrderTypes": [{"id": 1, "name": "Curve"}],
        "currencies": [{"currencyCode": "EUR", "minPrice": 0.0, "maxPrice": PRICE}],
        "contracts": [
            {
                "areaCode": "DK1",
                "contracts": [
                    {
                        "id": "contract1",
                        "deliveryStart": TEST_DATE.isoformat(),
                        "deliveryEnd": TEST_END_DATE.isoformat(),
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
                        "curveMaxVolumeLimit": MAX_VOLUME,
                        "auctionTradingResolution": TRADING_RESOLUTION,
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
        "closeForBidding": TEST_DATE.isoformat(),
        "deliveryStart": TEST_DATE.isoformat(),
        "deliveryEnd": TEST_END_DATE.isoformat(),
    }
    with pytest.raises(ValidationError):
        AuctionMultiResolutionResponse(**data)


def test_auction_price_validation() -> None:
    """Test AuctionPrice model validation."""
    data = {
        "auction": "auction1",
        "auctionDeliveryStart": TEST_DATE.isoformat(),
        "auctionDeliveryEnd": TEST_END_DATE.isoformat(),
        "contracts": [
            {
                "contractId": "contract1",
                "deliveryStart": TEST_DATE.isoformat(),
                "deliveryEnd": TEST_END_DATE.isoformat(),
                "areas": [
                    {
                        "areaCode": "DK1",
                        "prices": [
                            {
                                "currencyCode": "EUR",
                                "marketPrice": MARKET_PRICE,
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
    assert response.auction_delivery_start == TEST_DATE
    assert response.auction_delivery_end == TEST_END_DATE
    assert len(response.contracts) == 1
    assert response.contracts[0].contract_id == "contract1"
    assert len(response.contracts[0].areas) == 1
    assert response.contracts[0].areas[0].area_code == "DK1"
    assert response.contracts[0].areas[0].prices[0].status == AuctionResultState.FINAL


def test_auction_price_empty_contracts() -> None:
    """Test AuctionPrice with empty contracts."""
    data = {
        "auction": None,
        "auctionDeliveryStart": TEST_DATE.isoformat(),
        "auctionDeliveryEnd": TEST_END_DATE.isoformat(),
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
                "closeForBidding": TEST_DATE.isoformat(),
                "deliveryStart": TEST_DATE.isoformat(),
                "deliveryEnd": TEST_END_DATE.isoformat(),
            },
            "auction1",
            AuctionStateType.OPEN,
        ),
        (
            {
                "id": None,
                "name": None,
                "state": "Closed",
                "closeForBidding": TEST_DATE.isoformat(),
                "deliveryStart": TEST_DATE.isoformat(),
                "deliveryEnd": TEST_END_DATE.isoformat(),
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
    assert auction.close_for_bidding == TEST_DATE
    assert auction.delivery_start == TEST_DATE
    assert auction.delivery_end == TEST_END_DATE


def test_auction_response_with_nested_fields() -> None:
    """Test AuctionResponse with nested fields like currencies and contracts."""
    data = {
        "id": "auction1",
        "name": "Test Auction",
        "state": "Open",
        "closeForBidding": TEST_DATE.isoformat(),
        "deliveryStart": TEST_DATE.isoformat(),
        "deliveryEnd": TEST_END_DATE.isoformat(),
        "availableOrderTypes": [{"id": 1, "name": "Curve"}],
        "currencies": [{"currencyCode": "EUR", "minPrice": 0.0, "maxPrice": PRICE}],
        "contracts": [
            {
                "id": "contract1",
                "deliveryStart": TEST_DATE.isoformat(),
                "deliveryEnd": TEST_END_DATE.isoformat(),
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
                        "curveMaxVolumeLimit": MAX_VOLUME,
                        "auctionTradingResolution": TRADING_RESOLUTION,
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
        "closeForBidding": TEST_DATE.isoformat(),
        "deliveryStart": TEST_DATE.isoformat(),
        "deliveryEnd": TEST_END_DATE.isoformat(),
    }
    with pytest.raises(ValidationError):
        AuctionResponse(**data)
