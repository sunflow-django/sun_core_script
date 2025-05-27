import base64
from datetime import datetime
from http import HTTPStatus
from typing import Any
from uuid import UUID

import requests
from loguru import logger
from pydantic import BaseModel
from pydantic import ValidationError
from pydantic import field_validator

from app.services.nordpool.constants import BASE_URL_PROD
from app.services.nordpool.constants import BASE_URL_TEST
from app.services.nordpool.constants import ENDPOINTS
from app.services.nordpool.constants import TIMEOUT
from app.services.nordpool.constants import TOKEN_URL_PROD
from app.services.nordpool.constants import TOKEN_URL_TEST
from app.services.nordpool.schema import AuctionMultiResolutionResponse
from app.services.nordpool.schema import AuctionPrice
from app.services.nordpool.schema import AuctionResponse
from app.services.nordpool.schema import BlockList
from app.services.nordpool.schema import BlockListResponse
from app.services.nordpool.schema import BlockOrderPatch
from app.services.nordpool.schema import BlockResultResponse
from app.services.nordpool.schema import CombinedOrdersResponse
from app.services.nordpool.schema import CurveOrder
from app.services.nordpool.schema import CurveOrderPatch
from app.services.nordpool.schema import CurveOrderResponse
from app.services.nordpool.schema import OrderResultResponse
from app.services.nordpool.schema import PortfolioVolumeResponse
from app.services.nordpool.schema import ProblemDetails
from app.services.nordpool.schema import ReasonabilityResultsInfo


# Definitions
# - Product: A traded product. Ex.: "CWE_H_DA_1" for CWE Hour Day Ahead on 19.05.2025. Available in several area codes
# - Area codes: A country. Ex.: "FR" for France
# - Auction: A trading day for a product (no area code). Ex.: "CWE_H_DA_1-20250519", for CWE Hour Day Ahead 19.05.2025
# - Contract:  A trading hour for an auction (no area code). Ex: "CWE_H_DA_1-20250520-01"

# Urls


# For client ID / client secret / client authorization string
# Refer to https://developers.nordpoolgroup.com/reference/clients-and-scopes and
# https://developers.nordpoolgroup.com/reference/auth-introduction#section-request-header
AUCTION_API = "auction_api"
CLIENT_AUCTION_API = "client_auction_api"
CLIENT_AUTHORISATION_STRING = base64.b64encode(f"{CLIENT_AUCTION_API}:{CLIENT_AUCTION_API}".encode()).decode()


class GetAuctionsInput(BaseModel):
    """Class to validate inputs of the get_auctions function."""

    close_bidding_from: str | None = None
    close_bidding_to: str | None = None

    @field_validator("close_bidding_from", "close_bidding_to")
    @classmethod
    def validate_iso8601(cls, value: str | None) -> str | None:
        """Validate that the input string is in ISO 8601 format if provided.

        Args:
            value: The date-time string to validate.

        Returns:
            str | None: The validated string if valid, or None if input is None.

        Raises:
            ValueError: If the string is not a valid ISO 8601 date-time.
        """
        if value is None:
            return value
        try:
            datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as e:
            msg = f"Invalid ISO 8601 date-time format for value: {value}. Expected format: YYYY-MM-DDThh:mm:ssZ"
            raise ValueError(msg) from e
        else:
            return value


class AuctionFilterInput(BaseModel):
    """Class to validate inputs for auction-related methods: get_orders, get_trades, def get_portfolio_volumes."""

    auction_id: str
    portfolios: list[str] | None = None
    area_codes: list[str] | None = None


class AuctionIdInput(BaseModel):
    """Class to validate inputs for auction_id methods: get_price, get_auction_detail."""

    auction_id: str


class GetOrderInput(BaseModel):
    """Class to validate inputs of the get_block_order and get_curve_order function."""

    order_id: UUID


class PatchBlockOrderInput(BaseModel):
    """Class to validate inputs of the patch_block_order function."""

    order_id: UUID
    patch_data: BlockOrderPatch


class PostBlockOrderInput(BaseModel):
    """Class to validate inputs of the post_block_order function."""

    block_list: BlockList


class PatchCurveOrderInput(BaseModel):
    """Class to validate inputs of the patch_curve_order function."""

    order_id: UUID
    patch_data: CurveOrderPatch


class PostCurveOrderInput(BaseModel):
    """Class to validate inputs of the post_curve_order function."""

    curve_order: CurveOrder


class GetReasonabilityResultInput(BaseModel):
    """Class to validate inputs of the get_reasonability_result_for_order function."""

    order_id: UUID
    external_auction_id: str


class AuctionAPI:
    """Handle raw connections to Nordpool Auction API.

    This class provides methods to interact with the Nordpool Auction API, including authentication,
    retrieving auctions, orders, trades, prices, portfolio volumes, and managing block and curve orders.
    """

    def __init__(
        self,
        username: str,
        password: str,
        *,
        prod: bool = False,
    ) -> None:
        """Initialize the AuctionAPI client with authentication credentials.

        Args:
            username: The username for API authentication.
            password: The password for API authentication.
            prod: If True, use the production environment; otherwise, use the test environment. Defaults to False.
        """
        self.username: str = username
        self.password: str = password
        self.prod: bool = prod

        # Refer to https://developers.nordpoolgroup.com/reference/auth-introduction
        self.base_url: str = BASE_URL_PROD if prod else BASE_URL_TEST
        self.token_url: str = TOKEN_URL_PROD if prod else TOKEN_URL_TEST
        self.version: str = "1"  # The API version

        self.token: str | None = None
        self.authenticate()

    def authenticate(self) -> None:
        """Authenticate with the Nordpool API using OAuth2 password flow to obtain an access token.

        Raises:
            requests.HTTPError: If the authentication request fails with a non-200 status code.
        """
        data = {
            "grant_type": "password",
            "username": self.username,
            "password": self.password,
            "scope": AUCTION_API,
            "client_id": CLIENT_AUCTION_API,
            "client_secret": CLIENT_AUCTION_API,
        }

        headers = {
            "Authorization": f"Basic {CLIENT_AUTHORISATION_STRING}",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        response = requests.post(url=self.token_url, data=data, headers=headers, timeout=TIMEOUT)
        response.raise_for_status()
        self.token = response.json()["access_token"]

    def _make_request(
        self,
        method: str,
        url: str,
        params: dict[str, str | list[str]] | None = None,
        json: dict[str, Any] | None = None,
    ) -> tuple[int, dict[str, Any] | ProblemDetails]:
        """Make an authenticated HTTP request to the Nordpool API.

        Args:
            method: The HTTP method (e.g., "GET", "POST", "PATCH").
            url: The API endpoint URL.
            params: Query parameters for the request. Defaults to None.
            json: JSON data for the request body. Defaults to None.

        Returns:
            tuple[int, dict[str, Any] | ProblemDetails]: A tuple containing the HTTP status code and either the JSON
                response as a dictionary or a ProblemDetails object if the response is not JSON-parsable or an error
                occurs.

        Raises:
            requests.RequestException: If a network error occurs during the request.
        """
        headers = {"Authorization": f"Bearer {self.token}"}
        try:
            response = requests.request(method, url, params=params, json=json, headers=headers, timeout=TIMEOUT)
            try:  # Normal response
                return response.status_code, response.json()
            except ValueError:  # Not a json response
                pb = ProblemDetails(
                    title="ValueError",
                    status=response.status_code,
                    detail=response.text,
                )
                return response.status_code, pb
        except requests.RequestException:  # Unidentified error
            pb = ProblemDetails(
                title="Unidentified error",
                status=0,
                detail="Request failed. Network error ?",
            )
            return 0, pb

    # Auctions endpoints
    def get_auctions(
        self,
        close_bidding_from: str | None = None,
        close_bidding_to: str | None = None,
    ) -> AuctionResponse | None:
        """Retrieve auctions that are closed for bidding within the specified time period.

        Args:
            close_bidding_from: Filter auctions with close bidding starting from this date (ISO 8601 format).
            Ex.: 2019-09-20T10:00:00Z
            close_bidding_to: Filter auctions with close bidding ending at this date (ISO 8601 format).
            Ex.: 2019-09-20T10:00:00Z

        Returns:
            AuctionResponse | None: An AuctionResponse object containing the auction data, or None if an error occurs.
        """
        # Input validation
        try:
            GetAuctionsInput(close_bidding_from=close_bidding_from, close_bidding_to=close_bidding_to)
        except ValidationError:
            logger.exception(f"Inputs not a valid GetAuctionsInput: {(close_bidding_from, close_bidding_to)}")
            return None

        # Request preparation
        url = f"{self.base_url}{ENDPOINTS['auctions'].format(version=self.version)}"
        params = {}
        if close_bidding_from:
            params["closeBiddingFrom"] = close_bidding_from
        if close_bidding_to:
            params["closeBiddingTo"] = close_bidding_to

        # Request
        code, result = self._make_request("GET", url, params=params)

        # Output validation
        if code != HTTPStatus.OK:
            self.log_http_error(code, result)
            return None
        try:
            ar = AuctionResponse.model_validate(result)
        except ValidationError:
            logger.exception(f"Not an AuctionResponse: {result}")
            return None
        return ar

    def get_orders(
        self,
        auction_id: str,
        portfolios: list[str] | None = None,
        area_codes: list[str] | None = None,
    ) -> CombinedOrdersResponse | None:
        """Retrieve orders for a specific auction, filtered by portfolios and area codes.

        Args:
            auction_id: The ID of the auction (e.g., "CWE_H_DA_1-20250519").
            portfolios: List of portfolio IDs to filter the orders. Defaults to None.
            area_codes: List of area codes (e.g., "FR") to filter the orders. Defaults to None.

        Returns:
            CombinedOrdersResponse | None: A CombinedOrdersResponse object containing the orders, or None if an error
            occurs.
        """
        # Input validation
        try:
            AuctionFilterInput(auction_id=auction_id, portfolios=portfolios, area_codes=area_codes)
        except ValidationError:
            msg = (
                f"Input validation failed for auction_id: {auction_id}"
                f", portfolios: {portfolios}, area_codes: {area_codes}"
            )
            logger.exception(msg)
            return None

        # Request preparation
        url = f"{self.base_url}{ENDPOINTS['orders'].format(version=self.version, auctionId=auction_id)}"
        params = {}
        if portfolios:
            params["portfolios"] = portfolios
        if area_codes:
            params["areaCodes"] = area_codes

        # Request
        code, result = self._make_request("GET", url, params=params)

        # Output validation
        if code != HTTPStatus.OK:
            self.log_http_error(code, result)
            return None
        try:
            ar = CombinedOrdersResponse.model_validate(result)
        except ValidationError:
            logger.exception(f"Not a CombinedOrdersResponse: {result}")
            return None
        return ar

    def get_trades(
        self,
        auction_id: str,
        portfolios: list[str] | None = None,
        area_codes: list[str] | None = None,
    ) -> OrderResultResponse | BlockResultResponse | None:
        """Retrieve trades for a specific auction, filtered by portfolios and area codes.

        Args:
            auction_id: The ID of the auction (e.g., "CWE_H_DA_1-20250519").
            portfolios: List of portfolio IDs to filter the trades. Defaults to None.
            area_codes: List of area codes (e.g., "FR") to filter the trades. Defaults to None.

        Returns:
            OrderResultResponse | BlockResultResponse | None: A response containing trade data, or None if an error
            occurs.
        """
        # Input validation
        try:
            AuctionFilterInput(auction_id=auction_id, portfolios=portfolios, area_codes=area_codes)
        except ValidationError:
            msg = (
                f"Input validation failed for auction_id: {auction_id}"
                f", portfolios: {portfolios}, area_codes: {area_codes}"
            )
            logger.exception(msg)
            return None

        # Request preparation
        url = f"{self.base_url}{ENDPOINTS['trades'].format(version=self.version, auctionId=auction_id)}"
        params = {}
        if portfolios:
            params["portfolios"] = portfolios
        if area_codes:
            params["areaCodes"] = area_codes

        # Request
        code, result = self._make_request("GET", url, params=params)

        # Output validation
        if code != HTTPStatus.OK:
            self.log_http_error(code, result)
            return None
        try:
            return BlockResultResponse.model_validate(result)
        except ValidationError:
            try:
                return OrderResultResponse.model_validate(result)
            except ValidationError:
                logger.exception(f"Not an OrderResultResponse or BlockResultResponse: {result}")
                return None

    def get_prices(
        self,
        auction_id: str,
    ) -> AuctionPrice | None:
        """Retrieve prices for a specific auction.

        Args:
            auction_id: The ID of the auction (e.g., "CWE_H_DA_1-20250519").

        Returns:
            AuctionPrice | None: An AuctionPrice object containing the price data, or None if an error occurs.

        Notes:
            Prices are only available for auctions up to seven days in the past.
        """
        # Input validation
        try:
            AuctionIdInput(auction_id=auction_id)
        except ValidationError:
            logger.exception(f"Input validation failed for auction_id: {auction_id}")
            return None

        # Request preparation
        url = f"{self.base_url}{ENDPOINTS['prices'].format(version=self.version, auctionId=auction_id)}"

        # Request
        code, result = self._make_request("GET", url)

        # Output validation
        if code != HTTPStatus.OK:
            self.log_http_error(code, result)
            return None
        try:
            ap = AuctionPrice.model_validate(result)
        except ValidationError:
            logger.exception(f"Not an AuctionPrice: {result}")
            return None
        return ap

    def get_portfolio_volumes(
        self,
        auction_id: str,
        portfolios: list[str] | None = None,
        area_codes: list[str] | None = None,
    ) -> PortfolioVolumeResponse | None:
        """Retrieve portfolio volumes for a specific auction, filtered by portfolios and area codes.

        Args:
            auction_id: The ID of the auction (e.g., "CWE_H_DA_1-20250519").
            portfolios: List of portfolio IDs to filter the volumes. Defaults to None.
            area_codes: List of area codes (e.g., "FR") to filter the volumes. Defaults to None.

        Returns:
            PortfolioVolumeResponse | None: A PortfolioVolumeResponse object containing volume data, or None if an error
            occurs.
        """
        # Input validation
        try:
            AuctionFilterInput(auction_id=auction_id, portfolios=portfolios, area_codes=area_codes)
        except ValidationError:
            msg = (
                f"Input validation failed for auction_id: {auction_id}"
                f", portfolios: {portfolios}, area_codes: {area_codes}"
            )
            logger.exception(msg)
            return None

        # Request preparation
        url = f"{self.base_url}{ENDPOINTS['portfolio_volumes'].format(version=self.version, auctionId=auction_id)}"
        params = {}
        if portfolios:
            params["portfolios"] = portfolios
        if area_codes:
            params["areaCodes"] = area_codes

        # Request
        code, result = self._make_request("GET", url, params=params)

        # Output validation
        if code != HTTPStatus.OK:
            self.log_http_error(code, result)
            return None
        try:
            pvr = PortfolioVolumeResponse.model_validate(result)
        except ValidationError:
            logger.exception(f"Not a PortfolioVolumeResponse: {result}")
            return None
        return pvr

    def get_auction_detail(
        self,
        auction_id: str,
    ) -> AuctionMultiResolutionResponse | None:
        """Retrieve detailed information for a specific auction.

        Args:
            auction_id: The ID of the auction (e.g., "CWE_H_DA_1-20250519").

        Returns:
            AuctionMultiResolutionResponse | None: An AuctionMultiResolutionResponse object containing auction details,
            or None if an error occurs.
        """
        # Input validation
        try:
            AuctionIdInput(auction_id=auction_id)
        except ValidationError:
            logger.exception(f"Input validation failed for auction_id: {auction_id}")
            return None

        # Request preparation
        url = f"{self.base_url}{ENDPOINTS['auction'].format(version=self.version, auctionId=auction_id)}"

        # Request
        code, result = self._make_request("GET", url)

        # Output validation
        if code != HTTPStatus.OK:
            self.log_http_error(code, result)
            return None
        try:
            amr = AuctionMultiResolutionResponse.model_validate(result)
        except ValidationError:
            logger.exception(f"Not an AuctionMultiResolutionResponse: {result}")
            return None
        return amr

    # Block Order
    def get_block_order(
        self,
        order_id: UUID,
    ) -> BlockListResponse | None:
        """Retrieve a block order by its order ID.

        Args:
            order_id: The ID of the block order.

        Returns:
            BlockListResponse | None: A BlockListResponse object containing block order data, or None if an error
            occurs.
        """
        # Input validation
        try:
            GetOrderInput(order_id=order_id)
        except ValidationError:
            logger.exception(f"Input validation failed for order_id: {order_id}")
            return None

        # Request preparation
        url = f"{self.base_url}{ENDPOINTS['block_order'].format(version=self.version, orderId=order_id)}"

        # Request
        code, result = self._make_request("GET", url)

        # Output validation
        if code != HTTPStatus.OK:
            self.log_http_error(code, result)
            return None
        try:
            blr = BlockListResponse.model_validate(result)
        except ValidationError:
            logger.exception(f"Not a BlockListResponse: {result}")
            return None
        return blr

    def patch_block_order(
        self,
        order_id: UUID,
        patch_data: BlockOrderPatch,
    ) -> BlockListResponse | None:
        """Update an existing block order with the provided patch data.

        Args:
            order_id: The ID of the block order to update.
            patch_data: The patch data to apply to the block order.

        Returns:
            BlockListResponse | None: A BlockListResponse object containing updated block order data,
            or None if an error occurs.
        """
        # Input validation
        try:
            PatchBlockOrderInput(order_id=order_id, patch_data=patch_data)
        except ValidationError:
            logger.exception(f"Input validation failed for order_id: {order_id}, patch_data: {patch_data}")
            return None

        # Request preparation
        url = f"{self.base_url}{ENDPOINTS['block_order'].format(version=self.version, orderId=order_id)}"

        # Request
        code, result = self._make_request("PATCH", url, json=patch_data.model_dump(by_alias=True))

        # Output validation
        if code != HTTPStatus.OK:
            self.log_http_error(code, result)
            return None
        try:
            blr = BlockListResponse.model_validate(result)
        except ValidationError:
            logger.exception(f"Not a BlockListResponse: {result}")
            return None
        return blr

    def post_block_order(
        self,
        block_list: BlockList,
    ) -> BlockListResponse | None:
        """Create a new block order.

        Args:
            block_list: The block order data to create.

        Returns:
            BlockListResponse | None: A BlockListResponse object containing created block order data,
            or None if an error occurs.
        """
        # Input validation
        try:
            PostBlockOrderInput(block_list=block_list)
        except ValidationError:
            logger.exception(f"Input validation failed for block_list: {block_list}")
            return None

        # Request preparation
        url = f"{self.base_url}{ENDPOINTS['block_orders'].format(version=self.version)}"

        # Request
        code, result = self._make_request("POST", url, json=block_list.model_dump(by_alias=True))

        # Output validation
        if code != HTTPStatus.CREATED:
            self.log_http_error(code, result)
            return None
        try:
            blr = BlockListResponse.model_validate(result)
        except ValidationError:
            logger.exception(f"Not a BlockListResponse: {result}")
            return None
        return blr

    # Curve Order
    def get_curve_order(
        self,
        order_id: UUID,
    ) -> CurveOrderResponse | None:
        """Retrieve a curve order by its order ID.

        Args:
            order_id: The ID of the curve order.

        Returns:
            CurveOrderResponse | None: A CurveOrderResponse object containing curve order data,
            or None if an error occurs.
        """
        # Input validation
        try:
            GetOrderInput(order_id=order_id)
        except ValidationError:
            logger.exception(f"Input validation failed for order_id: {order_id}")
            return None

        # Request preparation
        url = f"{self.base_url}{ENDPOINTS['curve_order'].format(version=self.version, orderId=order_id)}"

        # Request
        code, result = self._make_request("GET", url)

        # Output validation
        if code != HTTPStatus.OK:
            self.log_http_error(code, result)
            return None
        try:
            cor = CurveOrderResponse.model_validate(result)
        except ValidationError:
            logger.exception(f"Not a CurveOrderResponse: {result}")
            return None
        return cor.sorted()

    def patch_curve_order(
        self,
        order_id: UUID,
        patch_data: CurveOrderPatch,
    ) -> CurveOrderResponse | None:
        """Update an existing curve order with the provided patch data.

        Args:
            order_id: The ID of the curve order to update.
            patch_data: The patch data to apply to the curve order.

        Returns:
            CurveOrderResponse | None: A CurveOrderResponse object containing updated curve order data,
            or None if an error occurs.
        """
        # Input validation
        try:
            PatchCurveOrderInput(order_id=order_id, patch_data=patch_data)
        except ValidationError:
            logger.exception(f"Input validation failed for order_id: {order_id}, patch_data: {patch_data}")
            return None

        # Request preparation
        url = f"{self.base_url}{ENDPOINTS['curve_order'].format(version=self.version, orderId=order_id)}"

        # Request
        code, result = self._make_request("PATCH", url, json=patch_data.model_dump(by_alias=True))

        # Output validation
        if code != HTTPStatus.OK:
            self.log_http_error(code, result)
            return None
        try:
            cor = CurveOrderResponse.model_validate(result)
        except ValidationError:
            logger.exception(f"Not a CurveOrderResponse: {result}")
            return None
        return cor.sorted()

    def post_curve_order(
        self,
        curve_order: CurveOrder,
    ) -> CurveOrderResponse | None:
        """Create a new curve order.

        Args:
            curve_order: The curve order data to create.

        Returns:
            CurveOrderResponse | None: A CurveOrderResponse object containing created curve order data,
            or None if an error occurs.
        """
        # Input validation
        try:
            PostCurveOrderInput(curve_order=curve_order)
        except ValidationError:
            logger.exception(f"Input validation failed for curve_order: {curve_order}")
            return None

        # Request preparation
        url = f"{self.base_url}{ENDPOINTS['curve_orders'].format(version=self.version)}"

        # Request
        code, result = self._make_request("POST", url, json=curve_order.model_dump(by_alias=True))

        # Output validation
        if code != HTTPStatus.CREATED:
            self.log_http_error(code, result)
            return None
        try:
            cor = CurveOrderResponse.model_validate(result)
        except ValidationError:
            logger.exception(f"Not a CurveOrderResponse: {result}")
            return None
        return cor.sorted()

    # Reasonability
    def get_reasonability_result_for_order(
        self,
        external_auction_id: str,
        order_id: UUID,
    ) -> ReasonabilityResultsInfo | None:
        """Retrieve reasonability analysis for a specific order in an auction.

        Args:
            external_auction_id: The external ID of the auction (e.g., "CWE_H_DA_1-20250519").
            order_id: The ID of the order.

        Returns:
            ReasonabilityResultsInfo | None: A ReasonabilityResultsInfo object containing reasonability results,
            or None if an error occurs.
        """
        # Input validation
        try:
            GetReasonabilityResultInput(external_auction_id=external_auction_id, order_id=order_id)
        except ValidationError:
            logger.exception(
                f"Input validation failed for external_auction_id: {external_auction_id}, order_id: {order_id}",
            )
            return None

        # Request preparation
        url = self.base_url + ENDPOINTS["reasonability_result"].format(
            version=self.version,
            externalAuctionId=external_auction_id,
            orderId=order_id,
        )

        # Request
        code, result = self._make_request("GET", url)

        # Output validation
        if code != HTTPStatus.OK:
            self.log_http_error(code, result)
            return None
        try:
            rri = ReasonabilityResultsInfo.model_validate(result)
        except ValidationError:
            logger.exception(f"Not a ReasonabilityResultsInfo: {result}")
            return None
        return rri

    # State
    def get_state(self) -> bool:
        """Check the operational state of the Nordpool API.

        Returns:
            True if HTTPStatus.OK. False otherwise
        """
        # Input validation
        # No inputs to validate for this method

        # Request preparation
        url = f"{self.base_url}{ENDPOINTS['state']}"

        # Request
        code, result = self._make_request("GET", url)

        # Output validation
        if code != HTTPStatus.OK:
            self.log_http_error(code, result)
            return False
        try:
            return True
        except ValidationError:
            logger.exception(f"Not a valid state response: {result}")
            return False

    @staticmethod
    def log_http_error(code: int, problem_details: ProblemDetails) -> None:
        """Logs HTTP error details using the provided code and response.

        Args:
            code: The HTTP status code of the error.
            problem_details: The ProblemDetails object with details on error.
        """
        detail: str | None = getattr(problem_details, "detail", None)
        msg = f"Failed request. Code: {code} Detail: {detail}."
        logger.error(msg)
