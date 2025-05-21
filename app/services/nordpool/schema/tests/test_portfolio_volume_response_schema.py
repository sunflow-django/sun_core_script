

from app.services.nordpool.schema.portfolio_volume_response_schema import PortfolioVolumeResponse


# Constants to avoid magic value used in comparison
VOLUME=100.0

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
