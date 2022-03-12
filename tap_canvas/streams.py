# with changes
"""Stream type classes for tap-canvas."""

from pathlib import Path
from typing import Any, Dict, Optional, Union, List, Iterable

from singer_sdk import typing as th  # JSON Schema typing helpers

from tap_canvas.client import CanvasStream
from tap_canvas.typing import IntegerTypeCustom
import requests

class EnrollmentTermStream(CanvasStream):
    records_jsonpath = "$.enrollment_terms[*]"

    name = "terms"
    path = "/accounts/1/terms"  # TODO: add account id to the config
    primary_keys = ["id"]
    replication_key = None
    # Optionally, you may also use `schema_filepath` in place of `schema`:
    # schema_filepath = SCHEMAS_DIR / "users.json"
    schema = th.PropertiesList(
        th.Property("id", th.IntegerType, description="Enrollment Term ID"),
        th.Property("name", th.StringType),
        th.Property("start_at", th.DateTimeType, description="Placeholder"),
        th.Property("end_at", th.DateTimeType, description="Placeholder"),
        th.Property("created_at", th.DateTimeType, description="Placeholder"),
        th.Property("workflow_state", th.StringType, description="Placeholder"),
        th.Property("grading_period_group_id", IntegerTypeCustom,
                    description="Placeholder"),
        th.Property("sis_term_id", th.StringType, description="Placeholder"),
        th.Property("sis_import_id", th.StringType, description="Placeholder"),
    ).to_dict()


class CourseStream(CanvasStream):
    records_jsonpath = "$[*]"

    name = "courses"
    path = "/accounts/1/courses"  # TODO: add account id to the config
    primary_keys = ["id"]
    replication_key = None
    # Optionally, you may also use `schema_filepath` in place of `schema`:
    # schema_filepath = SCHEMAS_DIR / "users.json"
    schema = th.PropertiesList(
        th.Property("root_account_id", IntegerTypeCustom, description="Placeholder"),
        th.Property("id", IntegerTypeCustom, description="Placeholder"),
        th.Property("account_id", IntegerTypeCustom, description="Placeholder"),
        th.Property("name", th.StringType, description="Placeholder"),
        th.Property("uuid", th.StringType, description="Placeholder"),
        th.Property("start_at", th.DateTimeType, description="Placeholder"),
        th.Property("created_at", th.DateTimeType, description="Placeholder"),
        th.Property("course_code", th.StringType, description="Placeholder"),
        th.Property("default_view", th.StringType, description="Placeholder"),
        th.Property("enrollment_term_id", IntegerTypeCustom, description="Placeholder"),
        th.Property("end_at", th.DateTimeType, description="Placeholder"),
        th.Property("homeroom_course", th.BooleanType, description="Placeholder"),
        th.Property("friendly_name", th.StringType, description="Placeholder"),
        th.Property("apply_assignment_group_weights",
                    th.BooleanType, description="Placeholder"),
        th.Property("time_zone", th.StringType, description="Placeholder"),
        th.Property("blueprint", th.BooleanType, description="Placeholder"),
        th.Property("template", th.BooleanType, description="Placeholder"),
        th.Property("sis_course_id", th.StringType, description="Placeholder"),
        th.Property("sis_import_id", IntegerTypeCustom, description="Placeholder"),
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

        if "course_ends_after" in self.config:
            params["ends_after"] = self.config.get("course_ends_after")
        if "with_enrollments" in self.config:
            params["with_enrollments"] = self.config.get("with_enrollments")

        return params


class OutcomeResultStream(CanvasStream):
    records_jsonpath = "$"

    name = "outcome_results"
    parent_stream_type = CourseStream

    path = "/courses/{course_id}/outcome_results"
    primary_keys = ["id"]
    replication_key = None
    # Optionally, you may also use `schema_filepath` in place of `schema`:
    # schema_filepath = SCHEMAS_DIR / "users.json"
    schema = th.PropertiesList(
        th.Property("id", IntegerTypeCustom),
        th.Property("mastery", th.BooleanType),
        th.Property("score", th.NumberType),
        th.Property("possible", th.NumberType),
        th.Property("percent", th.NumberType),
        th.Property("hide_points", th.BooleanType),
        th.Property("hidden", th.BooleanType),
        th.Property("submitted_or_assessed_at", th.DateTimeType),
        th.Property("links", th.ObjectType(
            th.Property("user", IntegerTypeCustom),
            th.Property("learning_outcome", IntegerTypeCustom),
            th.Property("assignment", th.StringType),
            th.Property("alignment", th.StringType)
        )),
        th.Property("percent", th.NumberType),
        th.Property("course_id", IntegerTypeCustom),
        th.Property("outcome_id", IntegerTypeCustom),
        th.Property("outcome_title", th.StringType),
        th.Property("outcome_display_name", th.StringType),
        th.Property("alignment_id", th.StringType),
        th.Property("alignment_name", th.StringType),
        th.Property("course_id", IntegerTypeCustom)
    ).to_dict()

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
        params["include[]"] = ["outcomes", "alignments"]

        return params


    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        response_json = response.json()
        self.logger.info(response_json.keys())
        outcome_results = response_json["outcome_results"]
        outcomes = response_json["linked"]["outcomes"]
        alignments = response_json["linked"]["alignments"]

        for outcome_result in outcome_results:
            # Add outcome metadata to outcome_result
            # TODO: add a config option
            outcome_result_outcome_id = int(outcome_result["links"]["learning_outcome"])
            try:
                current_outcome = next(outcome for outcome in outcomes if outcome_result_outcome_id == outcome["id"])
            except StopIteration as e:
                self.logger.error(f"Could not find outcome_id={outcome_result_outcome_id} in outcome metadata.")
            outcome_result["outcome_id"] = current_outcome["id"]
            outcome_result["outcome_title"] = current_outcome["title"]
            outcome_result["outcome_display_name"] = current_outcome["display_name"]

            # Add alignment metadata to outcome_result
            try:
                outcome_result_alignment_id = outcome_result["links"]["alignment"]
            except StopIteration as e:
                self.logger.error(f"Could not find alignment_id={outcome_result_alignment_id} in outcome metadata.")
            current_alignment = next(alignment for alignment in alignments if outcome_result_alignment_id == alignment["id"])
            outcome_result["alignment_id"] = current_alignment["id"]
            outcome_result["alignment_name"] = current_alignment["name"]

            yield outcome_result


class EnrollmentsStream(CanvasStream):
    records_jsonpath = "$.[*]"

    name = "enrollments"
    parent_stream_type = CourseStream

    path = "/courses/{course_id}/enrollments"
    primary_keys = ["id"]
    replication_key = None

    schema = th.PropertiesList(
        th.Property("course_id", IntegerTypeCustom, description="Placehold"),
        th.Property("id", IntegerTypeCustom, description="Placehold"),
        th.Property("user_id", IntegerTypeCustom, description="Placehold"),
        th.Property("course_section_id", IntegerTypeCustom, description="Placehold"),
        th.Property("root_account_id", IntegerTypeCustom, description="Placehold"),
        th.Property("type", th.StringType, description="Placehold"),
        th.Property("created_at", th.DateTimeType, description="Placehold"),
        th.Property("updated_at", th.DateTimeType, description="Placehold"),
        th.Property("start_at", th.DateTimeType, description="Placehold"),
        th.Property("end_at", th.DateTimeType, description="Placehold"),
        th.Property("enrollment_state", th.StringType, description="Placehold"),
        th.Property("role", th.StringType, description="Placehold"),
        th.Property("role_id", IntegerTypeCustom, description="Placehold"),
        th.Property("last_activity_at", th.DateTimeType, description="Placehold"),
        th.Property("total_activity_time", IntegerTypeCustom, description="Placehold"),
        th.Property("sis_import_id", IntegerTypeCustom, description="Placehold"),
        th.Property("sis_account_id", th.StringType, description="Placehold"),
        th.Property("sis_course_id", th.StringType, description="Placehold"),
        th.Property("sis_section_id", IntegerTypeCustom, description="Placehold"),
        th.Property("sis_user_id", th.StringType, description="Placehold"),
        th.Property("html_url", th.StringType, description="Placehold"),
    ).to_dict()


class SectionsStream(CanvasStream):
    records_jsonpath = "$.[*]"

    name = "sections"
    parent_stream_type = CourseStream

    path = "/courses/{course_id}/sections"
    primary_keys = ["id"]
    replication_key = None

    schema = th.PropertiesList(
        th.Property("course_id", IntegerTypeCustom),
        th.Property("id", IntegerTypeCustom),
        th.Property("name", th.StringType),
        th.Property("start_at", th.DateTimeType),
        th.Property("end_at", th.DateTimeType),
        th.Property("created_at", th.DateTimeType),
        th.Property("restrict_enrollments_to_section_dates", th.BooleanType),
        th.Property("sis_section_id", IntegerTypeCustom),
        th.Property("sis_course_id", th.StringType),
        th.Property("sis_import_id", th.IntegerType),
    ).to_dict()


class UsersStream(CanvasStream):
    records_jsonpath = "$.[*]"

    name = "users"

    path = "/accounts/1/users"
    primary_keys = ["id"]
    replication_key = None

    schema = th.PropertiesList(
        th.Property("id", th.IntegerType, description="Placeholder"),
        th.Property("name", th.StringType, description="Placeholder"),
        th.Property("created_at", th.DateTimeType, description="Placeholder"),
        th.Property("sortable_name", th.StringType, description="Placeholder"),
        th.Property("short_name", th.StringType, description="Placeholder"),
        th.Property("sis_user_id", th.StringType, description="Placeholder"),
        th.Property("sis_import_id", th.IntegerType, description="Placeholder"),
        th.Property("login_id", th.StringType, description="Placeholder"),
    ).to_dict()

class AssignmentsStream(CanvasStream):
    records_jsonpath = "$.[*]"

    name = "assignments"
    parent_stream_type = CourseStream

    path = "/courses/{course_id}/assignments"
    primary_keys = ["id"]
    replication_key = None

    schema = th.PropertiesList(
        th.Property("id", th.IntegerType),
        th.Property("description", th.StringType),
        th.Property("due_at", th.DateTimeType),
        th.Property("points_possible", th.NumberType),
        th.Property("grading_type", th.StringType),
        th.Property("assignment_group_id", th.IntegerType),
        th.Property("grading_standard_id", th.IntegerType),
        th.Property("created_at", th.DateTimeType),
        th.Property("updated_at", th.DateTimeType),
        th.Property("course_id", th.IntegerType),
        th.Property("name", th.StringType),
        th.Property("rubric", th.StringType),
        th.Property("published", th.BooleanType)
    ).to_dict()

class OutcomeStream(CanvasStream):
    records_path = "$[*]"

    name = "outcomes"
