import pendulum
import pytest

from app.constants.time_zones import PARIS_TZ
from app.core.config import settings
from app.services.streem.api import ForecastType
from app.services.streem.api import Resolution
from app.services.streem.api import StreemAPI


@pytest.fixture
def api() -> StreemAPI:
    """Provide an authenticated StreemAPI instance using settings credentials."""
    return StreemAPI(
        username=settings.STREEM_USERNAME,
        password=settings.STREEM_PASSWORD,
    )


@pytest.fixture
def name(api: StreemAPI) -> str:
    """Retrieve a valid installation name for testing."""
    installations = api.get_installations()
    if not installations:
        pytest.skip("No installations available")
    return installations[0]["name"]


@pytest.mark.live
def test_get_installations(api: StreemAPI) -> None:
    """Test fetching installation list."""
    response = api.get_installations()
    assert isinstance(response, list)
    if response:
        for item in response:
            assert isinstance(item, dict)
            assert "name" in item
            assert "external_ref" in item
            assert "client_id" in item
            assert "latitude" in item
            assert "longitude" in item
            assert "energy" in item


@pytest.mark.live
def test_get_installation_detail(api: StreemAPI, name: str) -> None:
    """Test fetching detail for one installation."""
    response = api.get_installation_detail(name)
    assert isinstance(response, dict)
    assert isinstance(response, dict)
    assert "name" in response
    assert "external_ref" in response
    assert "client_id" in response
    assert "latitude" in response
    assert "longitude" in response
    assert "energy" in response


@pytest.mark.live
def test_get_installation_alerts(api: StreemAPI, name: str) -> None:
    """Test fetching alets for one installation."""
    now = pendulum.now(PARIS_TZ)
    past_week_start = now.subtract(weeks=2).start_of("week")
    past_week_end = past_week_start.end_of("week")

    response = api.get_installation_alerts(
        name=name,
        start_date=past_week_start,
        end_date=past_week_end,
    )
    assert isinstance(response, list)
    if response:
        for item in response:
            assert "installation_name" in item
            assert "type" in item
            assert "created_at" in item
            assert "closed_at" in item


@pytest.mark.live
def test_get_forecast(api: StreemAPI, name: str) -> None:
    """Test fetching forecast data for an installation."""
    now = pendulum.now(PARIS_TZ)
    tomorrow_start = now.add(days=1).start_of("day")
    tomorrow_end = tomorrow_start.end_of("day")

    response = api.get_forecast(
        name=name,
        forecast_type=ForecastType.GENERATION,
        start_date=tomorrow_start,
        end_date=tomorrow_end,
        resolution=Resolution.H1,
    )
    assert isinstance(response, list)
    if response:
        for item in response:
            assert "date" in item
            assert "data" in item


@pytest.mark.live
def test_get_alerts(api: StreemAPI) -> None:
    """Test fetching all alerts."""
    now = pendulum.now(PARIS_TZ)
    past_week_start = now.subtract(weeks=2).start_of("week")
    past_week_end = past_week_start.end_of("week")

    response = api.get_alerts(
        start_date=past_week_start,
        end_date=past_week_end,
        all_alerts=True,
    )
    assert isinstance(response, list)
    if response:
        for item in response:
            assert "installation_name" in item
            assert "type" in item
            assert "created_at" in item
            assert "closed_at" in item


