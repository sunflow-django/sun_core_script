from datetime import datetime
from datetime import timedelta
from zoneinfo import ZoneInfo

import pytest

from app.constants.time_zones import PARIS_TZ
from app.core.config import settings
from app.services.streem.api import StreemAPI
from app.services.streem.schema import AlertList
from app.services.streem.schema import ForecastType
from app.services.streem.schema import Installation
from app.services.streem.schema import InstallationList
from app.services.streem.schema import LoadCurve
from app.services.streem.schema import Resolution


VGP_ROUEN = "VGP Rouen"


@pytest.fixture
def api() -> StreemAPI:
    return StreemAPI(
        username=settings.STREEM_USERNAME,
        password=settings.STREEM_PASSWORD,
    )


@pytest.mark.live
def test_api_get_installations(api: StreemAPI) -> None:
    installations = api.get_installations()
    # root=[Installation(client_id=None, energy=<EnergyType.SOLAR: 'solar'>, external_ref=None, latitude=49.3817, longitude=1.0178, name='VGP Rouen')]  # noqa: E501
    assert isinstance(installations, InstallationList) or installations is None, (
        "Response should be InstallationList or None"
    )
    assert installations is not None  # For a real live test
    if installations is not None:
        assert isinstance(installations.root, list), "Root should be a list of installations"
        if installations.root:
            installation = installations.root[0]
            assert installation.name is not None, "Installation should have 'name'"
            assert installation.energy is not None, "Installation should have 'energy'"


@pytest.mark.live
def test_api_get_installation_detail(api: StreemAPI) -> None:
    installation_name = VGP_ROUEN
    installation = api.get_installation_detail(installation_name)
    # client_id=None energy=<EnergyType.SOLAR: 'solar'> external_ref=None latitude=49.3817 longitude=1.0178 name='VGP Rouen'  # noqa: E501
    assert isinstance(installation, Installation) or installation is None, "Response should be Installation or None"
    assert installation is not None  # For a real live test
    if installation is not None:
        assert installation.name is not None, "Installation should have 'name'"
        assert installation.energy is not None, "Installation should have 'energy'"
        assert installation.name == installation_name, "Installation name should match input"


@pytest.mark.live
def test_api_get_installation_alerts(api: StreemAPI) -> None:
    installation_name = VGP_ROUEN

    one_week_ago = datetime.now(tz=PARIS_TZ) + timedelta(days=-7)
    start_date = one_week_ago.replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = datetime.now(tz=PARIS_TZ)
    alerts = api.get_installation_alerts(
        name=installation_name,
        start_date=start_date,
        end_date=end_date,
        all_alerts=True,
    )
    # ex root=[Alert(type='alarmCrititalPR', installation_name='VGP Rouen', created_at=datetime.datetime(2025, 5, 12, 0, 0), closed_at=None), Alert(type='noCom', installation_name='VGP Rouen', created_at=datetime.datetime(2025, 5, 18, 0, 0), closed_at=None), Alert(type='solarProdZero', installation_name='VGP Rouen', created_at=datetime.datetime(2025, 5, 18, 0, 0), closed_at=None)]  # noqa: E501
    assert isinstance(alerts, AlertList) or alerts is None, "Response should be AlertList or None"
    assert alerts is not None  # For a real live test
    if alerts is not None:
        assert isinstance(alerts.root, list), "Root should be a list of alerts"
        if alerts.root:
            alert = alerts.root[0]
            assert alert.installation_name is not None, "Alert should have 'installation_name'"
            assert alert.type is not None, "Alert should have 'type'"
            assert alert.created_at is not None, "Alert should have 'created_at'"


@pytest.mark.live
def test_api_get_forecast(api: StreemAPI) -> None:
    installation_name = VGP_ROUEN
    tomorrow = datetime.now(tz=PARIS_TZ) + timedelta(days=1)
    start_date = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = tomorrow.replace(hour=23, minute=59, second=59, microsecond=0)

    forecast = api.get_installation_forecast(
        forecast_type=ForecastType.GENERATION,
        start_date=start_date,
        end_date=end_date,
        resolution=Resolution.H1,
        name=installation_name,
    )
    # root=[LoadCurvePoint(data=0.0, date=datetime.datetime(2025, 5, 29, 0, 0, tzinfo=TzInfo(+02:00))), LoadCurvePoint(data=0.0, date=datetime.datetime(2025, 5, 29, 1, 0, tzinfo=TzInfo(+02:00))), LoadCurvePoint(data=0.0, date=datetime.datetime(2025, 5, 29, 2, 0, tzinfo=TzInfo(+02:00))), LoadCurvePoint(data=0.0, date=datetime.datetime(2025, 5, 29, 3, 0, tzinfo=TzInfo(+02:00))), LoadCurvePoint(data=0.0, date=datetime.datetime(2025, 5, 29, 4, 0, tzinfo=TzInfo(+02:00))), LoadCurvePoint(data=0.0, date=datetime.datetime(2025, 5, 29, 5, 0, tzinfo=TzInfo(+02:00))), LoadCurvePoint(data=16.9, date=datetime.datetime(2025, 5, 29, 6, 0, tzinfo=TzInfo(+02:00))), LoadCurvePoint(data=169.1, date=datetime.datetime(2025, 5, 29, 7, 0, tzinfo=TzInfo(+02:00))), LoadCurvePoint(data=425.6, date=datetime.datetime(2025, 5, 29, 8, 0, tzinfo=TzInfo(+02:00))), LoadCurvePoint(data=580.8, date=datetime.datetime(2025, 5, 29, 9, 0, tzinfo=TzInfo(+02:00))), LoadCurvePoint(data=601.9, date=datetime.datetime(2025, 5, 29, 10, 0, tzinfo=TzInfo(+02:00))), LoadCurvePoint(data=552.0, date=datetime.datetime(2025, 5, 29, 11, 0, tzinfo=TzInfo(+02:00))), LoadCurvePoint(data=672.6, date=datetime.datetime(2025, 5, 29, 12, 0, tzinfo=TzInfo(+02:00))), LoadCurvePoint(data=766.1, date=datetime.datetime(2025, 5, 29, 13, 0, tzinfo=TzInfo(+02:00))), LoadCurvePoint(data=674.8, date=datetime.datetime(2025, 5, 29, 14, 0, tzinfo=TzInfo(+02:00))), LoadCurvePoint(data=722.3, date=datetime.datetime(2025, 5, 29, 15, 0, tzinfo=TzInfo(+02:00))), LoadCurvePoint(data=820.3, date=datetime.datetime(2025, 5, 29, 16, 0, tzinfo=TzInfo(+02:00))), LoadCurvePoint(data=1009.8, date=datetime.datetime(2025, 5, 29, 17, 0, tzinfo=TzInfo(+02:00))), LoadCurvePoint(data=692.5, date=datetime.datetime(2025, 5, 29, 18, 0, tzinfo=TzInfo(+02:00))), LoadCurvePoint(data=348.0, date=datetime.datetime(2025, 5, 29, 19, 0, tzinfo=TzInfo(+02:00))), LoadCurvePoint(data=147.4, date=datetime.datetime(2025, 5, 29, 20, 0, tzinfo=TzInfo(+02:00))), LoadCurvePoint(data=27.1, date=datetime.datetime(2025, 5, 29, 21, 0, tzinfo=TzInfo(+02:00))), LoadCurvePoint(data=1.9, date=datetime.datetime(2025, 5, 29, 22, 0, tzinfo=TzInfo(+02:00))), LoadCurvePoint(data=0.0, date=datetime.datetime(2025, 5, 29, 23, 0, tzinfo=TzInfo(+02:00)))]  # noqa: E501

    assert isinstance(forecast, LoadCurve) or forecast is None, "Response should be LoadCurve or None"
    assert forecast is not None  # For a real live test
    if forecast is not None:
        assert isinstance(forecast.root, list), "Points should be a list"
        if forecast.root:
            point = forecast.root[0]
            assert point.date is not None, "Point should have 'date'"
            assert isinstance(point.data, float | type(None)), "Point data should be float or None"


@pytest.mark.live
def test_api_get_alerts(api: StreemAPI) -> None:
    start_date = datetime(2025, 5, 19, 10, 0, 0, tzinfo=ZoneInfo("Europe/Paris"))
    end_date = datetime(2025, 5, 20, 10, 0, 0, tzinfo=ZoneInfo("Europe/Paris"))
    alerts = api.get_alerts(
        start_date=start_date,
        end_date=end_date,
        all_alerts=True,
    )
    # ex root=[Alert(type='alarmCrititalPR', installation_name='VGP Rouen', created_at=datetime.datetime(2025, 5, 12, 0, 0), closed_at=None), Alert(type='noCom', installation_name='VGP Rouen', created_at=datetime.datetime(2025, 5, 18, 0, 0), closed_at=None), Alert(type='solarProdZero', installation_name='VGP Rouen', created_at=datetime.datetime(2025, 5, 18, 0, 0), closed_at=None)]  # noqa: E501
    assert isinstance(alerts, AlertList) or alerts is None, "Response should be AlertList or None"
    assert alerts is not None  # For a real live test
    if alerts is None:
        assert isinstance(alerts.root, list), "Root should be a list of alerts"
        if alerts.root:
            alert = alerts.root[0]
            assert alert.installation_name is not None, "Alert should have 'installation_name'"
            assert alert.type is not None, "Alert should have 'type'"
            assert alert.created_at is not None, "Alert should have 'created_at'"
