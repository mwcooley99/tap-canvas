"""canvas tap class."""

from typing import List

from singer_sdk import Tap, Stream
from singer_sdk import typing as th  # JSON schema typing helpers

# TODO: Import your custom stream types here:
from tap_canvas.streams import (
    CanvasStream,
    EnrollmentTermStream,
    CourseStream,
    OutcomeResultStream

)
# TODO: Compile a list of custom stream types here
#       OR rewrite discover_streams() below with your custom logic.
STREAM_TYPES = [
    EnrollmentTermStream,
    CourseStream,
    OutcomeResultStream,
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
        # Will need to add anything the tap needs to know how to pull out the data
        # e.g. Start date or the enrollment term/terss
        # start_date? Use it limit the terms that are being synced. Can be based on airflow date! This would allow the date of the dagrun to determine what will be synced!!
    ).to_dict()

    def discover_streams(self) -> List[Stream]:
        """Return a list of discovered streams."""
        return [stream_class(tap=self) for stream_class in STREAM_TYPES]
