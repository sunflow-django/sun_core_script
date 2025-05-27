import base64
from collections.abc import Iterator
from copy import deepcopy
from dataclasses import dataclass


# Urls
BASE_URL_TEST = "https://auctions-api.test.nordpoolgroup.com"
TOKEN_URL_TEST = "https://sts.test.nordpoolgroup.com/connect/token"

BASE_URL_PROD = "https://auctions-api.nordpoolgroup.com"
TOKEN_URL_PROD = "https://sts.nordpoolgroup.com/connect/token"

# End points
ENDPOINTS = {
    "auctions": "/api/v{version}/auctions",
    "orders": "/api/v{version}/auctions/{auctionId}/orders",
    "trades": "/api/v{version}/auctions/{auctionId}/trades",
    "prices": "/api/v{version}/auctions/{auctionId}/prices",
    "portfolio_volumes": "/api/v{version}/auctions/{auctionId}/portfoliovolumes",
    "auction": "/api/v{version}/auctions/{auctionId}",
    "block_order": "/api/v{version}/blockorders/{orderId}",
    "block_orders": "/api/v{version}/blockorders",
    "curve_order": "/api/v{version}/curveorders/{orderId}",
    "curve_orders": "/api/v{version}/curveorders",
    "reasonability_result": "/api/v{version}/auctions/{externalAuctionId}/orders/{orderId}/results",
    "state": "/api/state",
}

# Request
TIMEOUT = 3  # seconds

# Nordpool constants
# Refer to https://developers.nordpoolgroup.com/reference/clients-and-scopes
# Refer to https://developers.nordpoolgroup.com/reference/auth-introduction#section-request-header
AUCTION_API = "auction_api"
CLIENT_AUCTION_API = "client_auction_api"
CLIENT_AUTHORISATION_STRING = base64.b64encode(f"{CLIENT_AUCTION_API}:{CLIENT_AUCTION_API}".encode()).decode()
PRODUCT_ID = "CORE_IDA_1"


@dataclass(frozen=True)
class Area:
    name: str
    code: str
    eic_code: str


class Areas:
    def __init__(self) -> None:
        self._areas: dict[str, Area] = {
            "UK": Area(name="Great Britain", code="UK", eic_code="10Y1001A1001A57G"),
            "50Hz": Area(name="50Hertz Transmission GmbH", code="50Hz", eic_code="10YDE-VE-------2"),
            "TBW": Area(name="TransnetBW", code="TBW", eic_code="10YDE-ENBW-----N"),
            "AMP": Area(name="Amprion", code="AMP", eic_code="10YDE-RWENET---I"),
            "TTG": Area(name="TenneT Germany", code="TTG", eic_code="10YDE-EON------1"),
            "AT": Area(name="Austria", code="AT", eic_code="10YAT-APG------L"),
            "NL": Area(name="Netherlands", code="NL", eic_code="10YNL----------L"),
            "FR": Area(name="France", code="FR", eic_code="10YFR-RTE------C"),
            "NO1": Area(name="NO1 Norway", code="NO1", eic_code="10YNO-1--------2"),
            "NO2": Area(name="NO2 Norway", code="NO2", eic_code="10YNO-2--------T"),
            "NO3": Area(name="NO3 Norway", code="NO3", eic_code="10YNO-3--------J"),
            "NO4": Area(name="NO4 Norway", code="NO4", eic_code="10YNO-4--------9"),
            "NO5": Area(name="NO5 Norway", code="NO5", eic_code="10Y1001A1001A48H"),
            "FI": Area(name="Finland", code="FI", eic_code="10YFI-1--------U"),
            "BE": Area(name="Belgium", code="BE", eic_code="10YBE----------2"),
            "DK1": Area(name="DK1 Denmark", code="DK1", eic_code="10YDK-1--------W"),
            "DK2": Area(name="DK2 Denmark", code="DK2", eic_code="10YDK-2--------M"),
            "SE1": Area(name="SE1 Sweden", code="SE1", eic_code="10Y1001A1001A44P"),
            "SE2": Area(name="SE2 Sweden", code="SE2", eic_code="10Y1001A1001A45N"),
            "SE3": Area(name="SE3 Sweden", code="SE3", eic_code="10Y1001A1001A46L"),
            "SE4": Area(name="SE4 Sweden", code="SE4", eic_code="10Y1001A1001A47J"),
            "EE": Area(name="Estonia", code="EE", eic_code="10Y1001A1001A39I"),
            "LV": Area(name="Latvia", code="LV", eic_code="10YLV-1001A00074"),
            "LT": Area(name="Lithuania", code="LT", eic_code="10YLT-1001A0008Q"),
            "PL": Area(name="Poland", code="PL", eic_code="10YPL-AREA-----S"),
        }

    def get_area(self, key: str) -> Area | None:
        """Retrieve an Area by its key."""
        return self._areas.get(key)

    def all_areas(self) -> dict[str, Area]:
        """Return a copy of all areas as a dictionary."""
        return deepcopy(self._areas)

    def __getitem__(self, key: str) -> Area:
        """Allow dictionary-like access to areas."""
        area = self.get_area(key)
        if area is None:
            msg = f"Area with key '{key}' not found"
            raise KeyError(msg)
        return area

    def __iter__(self) -> Iterator[str]:
        """Make Areas iterable by yielding keys of the _areas dictionary."""
        return iter(self._areas)
