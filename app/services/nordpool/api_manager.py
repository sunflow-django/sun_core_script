import re
from collections import defaultdict
from http import HTTPStatus
from typing import Annotated
from uuid import UUID

from loguru import logger
from pydantic import BaseModel
from pydantic import Field
from pydantic import ValidationError

from app.services.nordpool.api import AuctionAPI
from app.services.nordpool.schema import CombinedOrdersResponse
from app.services.nordpool.schema import CurveOrder
from app.services.nordpool.schema import CurveOrderPatch
from app.services.nordpool.schema import CurveOrderResponse
from app.services.nordpool.schema import OrderApprovalState
from app.services.nordpool.schema import ProblemDetails
from app.services.nordpool.schema import ReasonabilityResultsInfo
from app.services.nordpool.schema import ValidatedCurve


class GetReasonabilityResultInput(BaseModel):
    """Class to validate inputs of the get_reasonability_result_for_order function"""

    external_auction_id: str
    order_id: Annotated[UUID | None, Field(alias="orderId")] = None


class GetOrderInput(BaseModel):
    """Class to validate inputs of the get_order function"""

    auction_id: Annotated[str, Field(description="The ID of the auction")]
    portfolios: Annotated[list[str], Field(default=None, description="List of portfolios to filter")]
    area_codes: Annotated[list[str], Field(default=None, description="List of area codes to filter")]


class AuctionApiManager:
    """Manage a connection to Nordpool Auction API (high level)"""

    def __init__(
        self,
        username: str,
        password: str,
        *,
        prod: bool = False,
    ) -> None:
        """Initialize the AuctionApiManager client.

        Args:
            username (str): The username for authentication.
            password (str): The password for authentication.
            prod (bool): Set to True for production environment
        """
        self.username: str = username
        self.password: str = password
        try:  # Authenticate with Nordpool API
            self.auction_api: AuctionAPI = AuctionAPI(username=username, password=password, prod=prod)
            logger.info("Authenticated with Nordpool API")
        except Exception:
            logger.exception("Failed to authenticate with Nordpool API")
            raise

    def get_order(
        self,
        auction_id: str,
        portfolios: list[str] | None = None,
        area_codes: list[str] | None = None,
    ) -> CombinedOrdersResponse:
        """
        Get orders placed for a specific auction, limited to company, portfolios and areas user has access to.
        Selection can be filtered by specifying portfolios and areas in the search parameters. Returns all order types.

        Args:
            auction_id (str): The ID of the auction.
            portfolios (list[str] | None): List of portfolios to filter.
            area_codes (list[str] | None): List of area codes to filter.

        Returns:
            dict[str, Any]: Combined orders response.
        """
        # Before
        try:
            GetOrderInput(
                auction_id=auction_id,
                portfolios=portfolios,
                area_codes=area_codes,
            )
        except ValidationError:
            logger.exception("Input validation failed")
            raise

        # Request
        code, result = self.auction_api.get_orders(auction_id=auction_id, portfolios=portfolios, area_codes=area_codes)

        # After
        if code != HTTPStatus.OK:
            self.log_http_error_and_exit(code, result)
        try:
            cor = CombinedOrdersResponse.model_validate(result)
        except ValidationError:
            logger.exception(f"Not a CombinedOrdersResponse: {result}")
            raise
        return cor

    def post_curve_order(self, order: CurveOrder | dict) -> CurveOrderResponse:
        """Posts the curve order to the Nordpool API.

        Args:
            order: Curve order data to post.

        Returns:
            The full response from API.

        Raises:
            ValidationError: If the order is invalid.
        """
        # Before
        try:
            curve_order = CurveOrder.model_validate(order)
        except ValidationError:
            logger.exception(f"Not a CurveOrder: {order}")
            raise

        # Request
        code, result = self.auction_api.post_curve_order(curve_order=curve_order.model_dump(by_alias=True))

        # After
        if code != HTTPStatus.CREATED:
            self.log_http_error_and_exit(code, result)
        try:
            curve_order_response = CurveOrderResponse.model_validate(result)
        except ValidationError:
            logger.exception(f"Not a CurveOrderResponse: {result}")
            raise

        logger.info(f"Order created, with id: {curve_order_response.order_id}")
        return curve_order_response

    def patch_curve_order(self, order_id: str, patch: CurveOrderPatch | dict) -> CurveOrderResponse:
        """Patch the curve order to the Nordpool API.

        Args:
            order_id: The ID of the order.
            order: The patch data for the curve order.

        Returns:
            Curve order response..

        Raises:
            ValidationError: If the order is invalid.
        """
        # Before
        try:
            curve_order_patch = CurveOrderPatch.model_validate(patch)
        except ValidationError:
            logger.exception(f"Not a CurveOrderPatch: {patch}")
            raise

        # Request
        code, result = self.auction_api.patch_curve_order(
            order_id=order_id,
            patch_data=curve_order_patch.model_dump(by_alias=True),
        )

        # After
        if code != HTTPStatus.OK:
            self.log_http_error_and_exit(code, result)
        try:
            curve_order_response = CurveOrderResponse.model_validate(result)
        except ValidationError:
            logger.exception(f"Not a CurveOrderResponse: {result}")
            raise

        logger.info(f"Order patched successfully. Order id: {curve_order_response.order_id}")
        return curve_order_response

    @staticmethod
    def get_auction_id(order: CurveOrder) -> str:
        return order.auction_id

    @staticmethod
    def get_order_id(order: CurveOrderResponse) -> str:
        return order.order_id

    @staticmethod
    def list_invalid_curves(info: ReasonabilityResultsInfo) -> list[ValidatedCurve]:
        """
        List all curves in ReasonabilityResultsInfo that have is_valid in [False or None].
        Return a list of curves where is_valid is False or None.
        """
        # Handle case where curves is None or empty
        if not info.curves:
            return []

        # Filter curves where is_valid is not True (i.e., False or None)
        return [curve for curve in info.curves if curve.is_valid is not True]

    def is_order_reasonable(
        self,
        external_auction_id: str,
        order_id: str,
    ) -> bool:
        """Check is the order is reasonible"""
        results = self.get_reasonability_result_for_order(external_auction_id, order_id)
        state: str | None = results.get("orderApprovalState", None)
        print("state: ", state)
        if state != OrderApprovalState.APPROVED:
            logger.error(f"Order not approved by Nordpool: {state}")
            return False

        invalids: list[ValidatedCurve] = self.list_invalid_curves(results)
        print("invalids: ", invalids)
        if len(invalids) > 0:
            logger.error(f"Invalid curves: {invalids}")
            return False

        logger.info("Order approved by Nordpool")
        return True

    def get_reasonability_result_for_order(
        self,
        external_auction_id: str,
        order_id: str,
    ) -> ReasonabilityResultsInfo:
        """
        curve_order is the orignal order
        """
        # Before
        try:
            GetReasonabilityResultInput(
                external_auction_id=external_auction_id,
                order_id=order_id,
            )
        except ValidationError:
            logger.exception("Input validation failed")
            raise
        print("external_auction_id: ", external_auction_id)
        print("order_id: ", order_id)
        # Request
        code, result = self.auction_api.get_reasonability_result_for_order(
            external_auction_id=external_auction_id,
            order_id=order_id,
        )

        # After
        if code != HTTPStatus.OK:
            self.log_http_error_and_exit(code, result)
        try:
            rri = ReasonabilityResultsInfo.model_validate(result)
        except ValidationError:
            logger.exception("Not a ReasonabilityResultsInfo: {result}")
            raise
        return rri

    @staticmethod
    def extract_uuid(text: str) -> UUID | None:
        """
        Extract a UUID from a string.
        Returns the UUID if found, otherwise None.
        """
        uuid_pattern = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
        match = re.search(uuid_pattern, text, re.IGNORECASE)
        if match:
            return UUID(match.group(0))
        return None

    @staticmethod
    def contains_order_exists_phrases(text: str) -> bool:
        """
        Check if the string contains both 'Order with id' 'already exists'.
        Returns True if both phrases are present, False otherwise.
        """
        return "already exists" in text and "Order with id" in text

    @staticmethod
    def log_http_error_and_exit(code: int, problem_details: ProblemDetails) -> None:
        """Logs HTTP error details using the provided code and response, than exits.

        Args:
            code: The HTTP status code of the error.
            problem_details: The ProblemDetails dict with deails on error.

        Returns:
            None

        Raise:
            SystemExit
        """
        detail: str | None = problem_details.get("detail", None)
        msg = f"Failed request. Code: {code} Detail: {detail}."
        logger.error(msg)
        raise SystemExit(msg)

    @staticmethod
    def count_existing_orders(response: CombinedOrdersResponse) -> dict[str, dict[str, int]]:
        """
        Count orders by type and state from a CombinedOrdersResponse.
        Returns a dictionary with order types as keys and state counts as nested dictionaries.
        """
        result = {"CurveOrder": defaultdict(int), "BlockOrder": defaultdict(int)}

        # Count Curve Orders
        if response.curve_orders:
            for order in response.curve_orders:
                state = order.state.value if order.state else "None"
                result["CurveOrder"][state] += 1

        # Count Block Orders
        if response.block_lists:
            for block_list in response.block_lists:
                if block_list.blocks:
                    for block in block_list.blocks:
                        state = block.state.value if block.state else "None"
                        result["BlockOrder"][state] += 1

        # Convert defaultdict to regular dict for clean output
        return {"CurveOrder": dict(result["CurveOrder"]), "BlockOrder": dict(result["BlockOrder"])}

    @staticmethod
    def list_existing_orders(data: CombinedOrdersResponse) -> list[dict[str, str]]:
        """
        Extract order details (order_id, auction_id, state, modified, type) from a CombinedOrdersResponse.
        Returns a list of dictionaries formatted for rich table printing.
        """
        curve_orders = [
            {
                "order_id": str(order.order_id) if order.order_id else "N/A",
                "auction_id": order.auction_id if order.auction_id else "N/A",
                "state": order.state.value if order.state else "None",
                "modified": order.modified.isoformat() if order.modified else "N/A",
                "type": "Curve",
            }
            for order in data.curve_orders or []
        ]

        block_orders = [
            {
                "order_id": str(block_list.order_id) if block_list.order_id else "N/A",
                "auction_id": block_list.auction_id if block_list.auction_id else "N/A",
                "state": block.state.value if block.state else "None",
                "modified": block_list.modified.isoformat() if block_list.modified else "N/A",
                "type": "Block",
            }
            for block_list in data.block_lists or []
            for block in block_list.blocks or []
        ]

        return curve_orders + block_orders

    @staticmethod
    def find_order_id_by_auction_id(combined_orders: CombinedOrdersResponse, auction_id: str) -> UUID | None:
        """
        Find all CurveOrderResponse with the given auction_id, raise error if more than one is found,
        and return the order_id of the first matching response.

        Args:
            combined_orders: CombinedOrdersResponse containing list of curve orders
            auction_id: String representing the contract ID to search for

        Returns:
            UUID of the matching order_id or None if not found

        Raises:
            ValueError: If more than one CurveOrderResponse matches the auction_id
        """
        if combined_orders.curve_orders is None:
            return None

        matching_orders = [
            curve_order for curve_order in combined_orders.curve_orders if curve_order.auction_id == auction_id
        ]

        if len(matching_orders) > 1:
            msg = f"Multiple CurveOrderResponse found for auction_id: {auction_id}"
            raise ValueError(msg)

        return matching_orders[0].order_id if matching_orders else None

    @staticmethod
    def convert_curve_order_to_patch(curve_order: CurveOrder) -> CurveOrderPatch:
        """
        Convert a CurveOrder to a CurveOrderPatch.

        Args:
            curve_order: CurveOrder object to convert

        Returns:
            CurveOrderPatch with the same curves and comment as the input CurveOrder
        """
        return CurveOrderPatch(curves=curve_order.curves, comment=curve_order.comment)
