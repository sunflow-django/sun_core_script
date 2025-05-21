import json
from collections.abc import Iterator
from dataclasses import dataclass

import jsonschema


@dataclass
class Installation:
    """Represents a single Streem installation, with its attributes."""

    client_id: str | None
    energy: str
    external_ref: str | None  # ["solar", "wind", "hydro", "other"]
    latitude: float | None  # In degrees
    longitude: float | None  # In degrees
    name: str

    _schema = {
        "type": "object",
        "properties": {
            "client_id": {"type": ["string", "null"]},
            "energy": {"type": "string", "enum": ["solar", "wind", "hydro", "other"], "default": "other"},
            "external_ref": {"type": ["string", "null"]},
            "latitude": {"type": ["number", "null"]},
            "longitude": {"type": ["number", "null"]},
            "name": {"type": "string"},
        },
        "required": ["name"],
        "additionalProperties": False,
    }

    @classmethod
    def from_json(cls, json_data: str) -> "Installation":
        """Initialize an Installation from a JSON string with schema validation.

        Args:
            json_data: A JSON string containing a single installation dictionary.

        Returns:
            An Installation instance populated with the parsed data.

        Raises:
            json.JSONDecodeError: If the JSON string is invalid.
            jsonschema.exceptions.ValidationError: If the JSON data does not match the schema.
        """
        data = json.loads(json_data)
        jsonschema.validate(instance=data, schema=cls._schema)
        return cls(
            client_id=data.get("client_id"),
            energy=data.get("energy", "other"),
            external_ref=data.get("external_ref"),
            latitude=data.get("latitude"),
            longitude=data.get("longitude"),
            name=data["name"],
        )


@dataclass
class InstallationManager:
    """Manages a collection of installations with iteration and JSON initialization."""

    installations: list[Installation]

    _schema = {"type": "array", "items": Installation._schema, "minItems": 0}  # noqa: SLF001

    @classmethod
    def from_json(cls, json_data: str) -> "InstallationManager":
        """Initialize InstallationManager from a JSON string with schema validation.

        Args:
            json_data: A JSON string containing a list of installation dictionaries.

        Returns:
            An InstallationManager instance populated with the parsed installations.

        Raises:
            json.JSONDecodeError: If the JSON string is invalid.
            jsonschema.exceptions.ValidationError: If the JSON data does not match the schema.
        """
        data = json.loads(json_data)
        jsonschema.validate(instance=data, schema=cls._schema)
        installations = [
            Installation(
                client_id=item.get("client_id"),
                energy=item.get("energy", "other"),
                external_ref=item.get("external_ref"),
                latitude=item.get("latitude"),
                longitude=item.get("longitude"),
                name=item["name"],
            )
            for item in data
        ]
        return cls(installations=installations)

    def iter_client_ids(self) -> Iterator[str | None]:
        """Iterate over all client IDs in the installations.

        Yields:
            A string or None representing each client ID.
        """
        for installation in self.installations:
            yield installation.client_id

    def iter_names(self) -> Iterator[str]:
        """Iterate over all names in the installations.

        Yields:
            A string representing each installation name.
        """
        for installation in self.installations:
            yield installation.name
