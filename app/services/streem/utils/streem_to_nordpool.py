from dataclasses import dataclass
from datetime import datetime
from datetime import timedelta

from app.nomination.utils import tomorrow_str_no_dash


@dataclass
class OrderHeader:
    """Header for a Nordpool order"""

    product_id: str = "CWE_H_DA_1"
    area_code: str = "FR"
    portfolio: str | None = "FR-SUNFLOW"
    comment: str | None = None

    @property
    def auction_id(self) -> str:
        return f"{self.product_id}-{tomorrow_str_no_dash()}"


def streem_to_nordpool(
    json_data: list(dict[str, float]),
    oh: OrderHeader | None = None,
) -> dict:
    """
    Transform input data into NPS.Auction.API.CurveOrder format.
    - Divide by 1000 (input is in kWh, output is in MWh).
    - Round to one decimal (ouput requires trade lot of 0,1 MWh)
    - Add one hour to each timestamp (input uses zero-based numbering, output has a first index of one).
    - Add order header

    Args:
        json_data: list of dictionaries with 'date' (ISO 8601 strings) and 'data' (float) representing an energy
            volume in kWh. Ex.:
            [
                {"date": "2025-05-20T09:00:00+02:00", "data": 1110.7},
                {"date": "2025-05-20T10:00:00+02:00", "data": 1468.4},
            ]
        order_header: The order header

    Returns:
        Dictionary in NPS.Auction.API.CurveOrder format.
        Ex.:
        {"auctionId": "CWE_H_DA_1-20250520",
        "portfolio": "FR-SUNFLOW",
        "areaCode": "FR",
        "comment": None,
        "curves": [{"contractId": "CWE_H_DA_1-20250521-10",
                    "curvePoints": [{"price": -500.0, "volume": 0.0},
                                    {"price": -0.01, "volume": 0.0},
                                    {"price": 0.0, "volume": -1.1},
                                    {"price": 4000.0, "volume": -1.1}]},
                    {"contractId": "CWE_H_DA_1-20250521-11",
                    "curvePoints": [{"price": -500.0, "volume": 0.0},
                                    {"price": -0.01, "volume": 0.0},
                                    {"price": 0.0, "volume": -1.5},
                                    {"price": 4000.0, "volume": -1.5}]}],
        "portfolio": "FR-SUNFLOW"}


    """
    # Handle missing order_header
    if not oh:
        oh = OrderHeader()

    # Build auction_id based on first date in json_data
    if not json_data:
        return {"error": "Input data is empty"}
    first_date_str = json_data[0].get("date", None)
    if not first_date_str:
        return {"error": "First datapoint must has a 'date' attribute"}
    try:
        first_date_obj = parse_iso8601(first_date_str)
    except ValueError as e:
        return {"error": f"Invalid date or volume format in entry {first_date_str}: {e!s}"}

    auction_date = first_date_obj.strftime("%Y%m%d")
    auction_id = f"{oh.product_id}-{auction_date}"

    # build curves
    curves: list[dict] = []
    for hour in json_data:
        try:
            date_str = hour["date"]
            if not isinstance(date_str, str):
                msg = "Date must be a string"
                raise TypeError(msg)  # noqa: TRY301
            date_obj = parse_iso8601(date_str)
            volume = round(float(hour["data"]) / 1000, 1)
        except (KeyError, ValueError, TypeError) as e:
            return {"error": f"Invalid date or volume format in entry {hour}: {e!s}"}

        # Format contractId as CWE_QH_DA_1-YYYYMMDD-HH
        # contractId reflects delivery day and it is next day after auctionId
        # So for instance, auctionId CWE_H_DA_1-20190522 has contracts like CWE_H_DA_1-20190523-01
        contract_date = (date_obj + timedelta(days=1)).strftime("%Y%m%d")
        # TODO: make this work for daylight saving time (ie.: 3a and 3b hours)
        contract_hour = f"{date_obj.hour + 1:02d}"
        contract_id = f"{oh.product_id}-{contract_date}-{contract_hour}"

        # Create curvePoints with fixed prices and volumes
        curve_points = [
            {"price": -500.00, "volume": 0.00},
            {"price": -0.01, "volume": 0.00},
            {"price": 0.00, "volume": -volume},
            {"price": 4000.00, "volume": -volume},
        ]

        curves.append({"contractId": contract_id, "curvePoints": curve_points})

    return {
        "auctionId": auction_id,
        "portfolio": oh.portfolio,
        "areaCode": oh.area_code,
        "comment": None,
        "curves": curves,
    }


def parse_iso8601(timestamp: str) -> datetime:
    """
    Parse an ISO 8601 timestamp and raise an error if malformed.

    Args:
        timestamp: A string in ISO 8601 format (e.g., '2025-05-20T10:00:00+02:00').

    Returns:
        A datetime object representing the parsed timestamp.

    Raises:
        ValueError: If the timestamp is not in valid ISO 8601 format.
    """
    try:
        # Replace 'Z' with '+00:00' for consistency, as 'Z' means UTC
        if timestamp.endswith("Z"):
            timestamp = timestamp[:-1] + "+00:00"
        return datetime.fromisoformat(timestamp)
    except ValueError as e:
        msg = f"Invalid ISO 8601 format: {timestamp}. Error: {e!s}"
        raise ValueError(msg) from e
