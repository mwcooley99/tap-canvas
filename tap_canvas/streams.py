"""Stream type classes for tap-canvas."""

from pathlib import Path
from typing import Any, Dict, Optional, Union, List, Iterable

from singer_sdk import typing as th  # JSON Schema typing helpers

from tap_canvas.client import CanvasStream

class EnrollmentTermStream(CanvasStream):
    """Define custom stream."""

    records_jsonpath = "$.enrollment_terms[*]"

    name = "terms"
    path = "/accounts/1/terms" # TODO: add account id to the config
    primary_keys = ["id"]
    replication_key = None
    # Optionally, you may also use `schema_filepath` in place of `schema`:
    # schema_filepath = SCHEMAS_DIR / "users.json"
    schema = th.PropertiesList(
        th.Property("name", th.StringType),
        th.Property(
            "id",
            th.IntegerType,
            description="Enrollment Term ID"
        ),
        th.Property(
            "name",
            th.StringType,
            description="Name of the Term"
        ),
    ).to_dict()