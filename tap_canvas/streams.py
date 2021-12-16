# with changes
"""Stream type classes for tap-canvas."""

from pathlib import Path
from typing import Any, Dict, Optional, Union, List, Iterable

from singer_sdk import typing as th  # JSON Schema typing helpers

from tap_canvas.client import CanvasStream


class EnrollmentTermStream(CanvasStream):
    records_jsonpath = "$.enrollment_terms[*]"

    name = "terms"
    path = "/accounts/1/terms"  # TODO: add account id to the config
    primary_keys = ["id"]
    replication_key = None
    # Optionally, you may also use `schema_filepath` in place of `schema`:
    # schema_filepath = SCHEMAS_DIR / "users.json"
    schema = th.PropertiesList(
        th.Property("name", th.StringType),
        th.Property("id", th.IntegerType, description="Enrollment Term ID"),
        th.Property("sis_term_id", th.StringType, description="Placeholder"),
        th.Property("sis_import_id", th.StringType, description="Placeholder"),
        th.Property("name", th.StringType, description="Placeholder"),
        th.Property("start_at", th.DateTimeType, description="Placeholder"),
        th.Property("end_at", th.DateTimeType, description="Placeholder"),
        th.Property("workflow_state", th.StringType, description="Placeholder"),
    ).to_dict()


class CourseStream(CanvasStream):
    records_jsonpath = "$.[*]"

    name = "courses"
    path = "/accounts/1/courses"  # TODO: add account id to the config
    primary_keys = ["id"]
    replication_key = None
    # Optionally, you may also use `schema_filepath` in place of `schema`:
    # schema_filepath = SCHEMAS_DIR / "users.json"
    schema = th.PropertiesList(
        th.Property("id", th.IntegerType),
        th.Property("sis_course_id", th.StringType),
        th.Property("enrollment_term_id", th.IntegerType),
    ).to_dict()

    def get_child_context(self, record: dict, context: Optional[dict]) -> dict:
        """Return a context dictionary for child streams."""
        return {
            "course_id": record["id"],
        }

    # Maybe roll back into the other class? Or somehow use inheritance to not rewrite everything?
    def get_url_params(
        self, context: Optional[dict], next_page_token: Optional[Any]
    ) -> Dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization."""
        params: dict = {}
        if next_page_token:
            params["page"] = next_page_token
        if self.replication_key:
            params["sort"] = "asc"
            params["order_by"] = self.replication_key
        params["per_page"] = 100

        params["ends_after"] = self.config.get("course_ends_after")

        return params


class OutcomeResultStream(CanvasStream):
    records_jsonpath = "$.outcome_results[*]"

    name = "outcome_results"
    parent_stream_type = CourseStream

    path = "/courses/{course_id}/outcome_results"  # TODO: needs to access all courses (prob. parent and child problem)
    primary_keys = ["id"]
    replication_key = None
    # Optionally, you may also use `schema_filepath` in place of `schema`:
    # schema_filepath = SCHEMAS_DIR / "users.json"
    schema = th.PropertiesList(
        th.Property("id", th.IntegerType),
        th.Property("score", th.IntegerType),
        th.Property("submitted_or_assessed_at", th.DateTimeType),
        th.Property("links", th.StringType),
        th.Property("percent", th.NumberType),
    ).to_dict()
