import json
from collections.abc import Iterator
from dataclasses import dataclass

import jsonschema


@dataclass
class CurvePoint:
    """Represents a single curve point in a curve order."""

    price: float
    volume: float

    _schema = {
        "type": "object",
        "properties": {
            "price": {"type": "number"},
            "volume": {"type": "number"},
        },
        "required": ["price", "volume"],
        "additionalProperties": False,
    }


@dataclass
class Curve:
    """Represents a curve in a curve order, containing curve points."""

    contract_id: str
    curve_points: list[CurvePoint]

    _schema = {
        "type": "object",
        "properties": {
            "contractId": {"type": "string", "minLength": 1},
            "curvePoints": {
                "type": "array",
                "items": CurvePoint._schema,  # noqa: SLF001
            },
        },
        "required": ["contractId", "curvePoints"],
        "additionalProperties": False,
    }


@dataclass
class CurveOrder:
    """Represents a curve order for the Auction API."""

    auction_id: str
    portfolio: str
    area_code: str
    comment: str | None
    curves: list[Curve]

    _schema = {
        "type": "object",
        "properties": {
            "auctionId": {"type": "string", "minLength": 1},
            "portfolio": {"type": "string", "minLength": 1},
            "areaCode": {"type": "string", "minLength": 1},
            "comment": {"type": ["string", "null"], "maxLength": 255, "minLength": 0},
            "curves": {
                "type": "array",
                "items": Curve._schema,# noqa: SLF001
            },
        },
        "required": ["auctionId", "portfolio", "areaCode", "curves"],
        "additionalProperties": False,
    }

    @classmethod
    def from_json(cls, json_data: str) -> "CurveOrder":
        """Initialize a CurveOrder from a JSON string with schema validation.

        Args:
            json_data: A JSON string containing a curve order dictionary.

        Returns:
            A CurveOrder instance populated with the parsed data.

        Raises:
            json.JSONDecodeError: If the JSON string is invalid.
            jsonschema.exceptions.ValidationError: If the JSON data does not match the schema.
        """
        data = json.loads(json_data)
        jsonschema.validate(instance=data, schema=cls._schema)
        curves = [
            Curve(
                contract_id=curve["contractId"],
                curve_points=[
                    CurvePoint(
                        price=point["price"],
                        volume=point["volume"],
                    )
                    for point in curve["curvePoints"]
                ],
            )
            for curve in data["curves"]
        ]
        return cls(
            auction_id=data["auctionId"],
            portfolio=data["portfolio"],
            area_code=data["areaCode"],
            comment=data.get("comment"),
            curves=curves,
        )

    def iter_contract_ids(self) -> Iterator[str]:
        """Iterate over all contract IDs in the curves.

        Yields:
            A string representing each contract ID.
        """
        for curve in self.curves:
            yield curve.contract_id
