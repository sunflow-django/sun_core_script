from datetime import datetime


def transform_curve(
    volume_data: list(dict[str, float]),
    auction_id: str = "CWE_QH_DA_1",
    area_code: str = "FR",
    portfolio: str = "TestAuctions FR",
) -> dict:
    """
    Transform input data into NPS.Auction.API.CurveOrder format.
    - Divide by 1000 (input is in kWh, output is in MWh).
    - Round to one decimal (trade lot = 0,1 MWh)
    - Add one hour (input uses zero-based numbering, output has a first index of one).

    Args:
        volume_data: list of dictionaries with 'date' (ISO 8601 strings) and 'data' (float) representing an energy
            volume in kWh. Ex.:
            [
                {"date": "2025-05-20T10:00:00+02:00", "data": 1463.9},
                {"date": "2025-05-20T11:00:00+02:00", "data": 1500.0},
            ]
        auction_id: Auction ID for the output, as specified from Nordpool.
        area_code: Area code for the output, as specified from Nordpool.
        portfolio: Portfolio name for the output (free text).

    Returns:
        Dictionary in NPS.Auction.API.CurveOrder format.
        Ex.:
        {'areaCode': 'FR',
        'auctionId': 'CWE_QH_DA_1',
        'comment': None,
        'curves': [{'contractId': 'CWE_QH_DA_1-20250520-11',
                    'curvePoints': [{'price': -500.0, 'volume': 0.0},
                                    {'price': -0.01, 'volume': 0.0},
                                    {'price': 0.0, 'volume': -1.5},
                                    {'price': 4000.0, 'volume': -1.5}]},
                    {'contractId': 'CWE_QH_DA_1-20250520-12',
                    'curvePoints': [{'price': -500.0, 'volume': 0.0},
                                    {'price': -0.01, 'volume': 0.0},
                                    {'price': 0.0, 'volume': -1.5},
                                    {'price': 4000.0, 'volume': -1.5}]}],
        'portfolio': 'TestAuctions FR'}

    """
    if not volume_data:
        return {"error": "Input data is empty"}

    curves: list[dict] = []
    for hour in volume_data:
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
        contract_date = date_obj.strftime("%Y%m%d")
        # TODO: make this work for daylight saving time (ie.: 3a and 3b hours)
        contract_hour = f"{date_obj.hour + 1:02d}"
        contract_id = f"{auction_id}-{contract_date}-{contract_hour}"

        # Create curvePoints with fixed prices and volumes
        curve_points = [
            {"price": -500.00, "volume": 0.00},
            {"price": -0.01, "volume": 0.00},
            {"price": 0.00, "volume": -volume},
            {"price": 4000.00, "volume": -volume},
        ]

        curves.append({"contractId": contract_id, "curvePoints": curve_points})

    return {"auctionId": auction_id, "portfolio": portfolio, "areaCode": area_code, "comment": None, "curves": curves}


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
