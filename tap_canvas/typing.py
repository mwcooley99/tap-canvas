from singer_sdk import typing as th
from singer_sdk.helpers._classproperty import classproperty


class IntegerTypeCustom(th.JSONTypeHelper):
    """Integer type with max and min"""

    @classproperty
    def type_dict(cls) -> dict:
        """
        Get type dictionary

        returns:
            A dictionary describing the type.
        """
        dict = {
            "type": ["integer"],
            "minimum": -2147483648,
            "maximum": 2147483647,
        }

        return dict