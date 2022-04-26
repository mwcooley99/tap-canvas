"""canvas tap class."""

from typing import List

from singer_sdk import Tap, Stream
from singer_sdk import typing as th  # JSON schema typing helpers

from tap_canvas.streams import (
    EnrollmentTermStream,
    CourseStream,
    OutcomeResultStream,
    EnrollmentsStream,
    UsersStream,
    SectionsStream,
    AssignmentsStream

)
STREAM_TYPES = [
    EnrollmentTermStream,
    CourseStream,
    OutcomeResultStream,
    EnrollmentsStream,
    UsersStream,
    SectionsStream,
    AssignmentsStream
]


class Tapcanvas(Tap):
    """canvas tap class."""
    name = "tap-canvas"

    # This might be when the #auth type is called. Maybe add oauth here? With a refresh token. Like tap-pardot 
    config_jsonschema = th.PropertiesList(
        th.Property(
            "api_key",
            th.StringType,
            required=True,
            description="The token to authenticate against the API service"
        ),
        th.Property(
            "course_ends_after",
            th.DateTimeType,
            description="Limit courses queried to courses that end after this date."
        )
    ).to_dict()

    def discover_streams(self) -> List[Stream]:
        """Return a list of discovered streams."""
        return [stream_class(tap=self) for stream_class in STREAM_TYPES]
