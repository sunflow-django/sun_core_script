import pytest

from app.core.config import settings
from app.nordpool.api import CLIENT_AUTHORISATION_STRING
from app.nordpool.api import AuctionAPI


@pytest.fixture
def api() -> AuctionAPI:
    return AuctionAPI(username=settings.NORDPOOL_USERNAME, password=settings.NORDPOOL_PASSWORD, prod=False)


@pytest.mark.live
def test_api_get_auctions(api: AuctionAPI) -> None:
    auctions = api.get_auctions(close_bidding_from="2025-05-19T10:00:00Z", close_bidding_to="2025-05-19T10:00:00Z")

    assert len(auctions) == 2

    # Check first auction
    auction0 = auctions[0]
    assert auction0["id"] == "CWE_QH_DA_1-20250519"
    assert auction0["name"] == "CWE QH Day Ahead 19.05.2025"
    assert auction0["state"] == "Open"
    assert auction0["closeForBidding"] == "2025-05-19T10:00:00.000Z"
    assert auction0["deliveryStart"] == "2025-05-19T22:00:00.000Z"
    assert auction0["deliveryEnd"] == "2025-05-20T22:00:00.000Z"

    # Check second auction
    auction1 = auctions[1]
    assert auction1["id"] == "CWE_H_DA_1-20250519"
    assert auction1["name"] == "CWE Hour Day Ahead 19.05.2025"
    assert auction1["state"] == "Open"
    assert auction1["closeForBidding"] == "2025-05-19T10:00:00.000Z"
    assert auction1["deliveryStart"] == "2025-05-19T22:00:00.000Z"
    assert auction1["deliveryEnd"] == "2025-05-20T22:00:00.000Z"


def test_client_authorisation_string() -> None:
    assert CLIENT_AUTHORISATION_STRING == "Y2xpZW50X2F1Y3Rpb25fYXBpOmNsaWVudF9hdWN0aW9uX2FwaQ=="
