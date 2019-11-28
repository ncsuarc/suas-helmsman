from collections import namedtuple


class Waypoint(
    namedtuple("Waypoint", ["latitude", "longitude", "altitude"])
):
    """
    This is a class to manage the course waypoints of the interop file.
    """
