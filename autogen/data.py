from math import cos, pi, sin
from typing import NamedTuple

from shapely.geometry import LineString, Point


class Waypoint(NamedTuple):
    """Data for a Waypoint Object.

    A Waypoint is a point in which we need to travel to at the start of the mission
    
    Args:
        point (Point): The point to travel to given as x, y, z
        order (int): the order number in which to travel to
    
    Example:
        Waypoint(Point(x, y, z), 0)
    """

    point: Point
    order: int


class Obstacle(NamedTuple):
    """Class for an obstacle object.

    An obstacle is define by a point given in x y, a height, and a radius
    
    Args:
        point (Point): the center of the circle
        radius (float): the radius of the circle
        height (int): the height of the obstacle
    """

    point: Point
    radius: float
    height: int

    def equation(self):
        """Returns the equation of the obstacle cylinder.
        
        This is used to check for intersections during edge generation

        Returns:
            LineString: A LineString in through the center with a radius buffer
        """
        return (
            LineString([self.point, (self.point.x, self.point.y, self.height)])
            .buffer(feet_to_meters(self.radius))
            .boundary
        )

    def points(self):
        """Estimates the cylinder to an octogon.
        
        Used to add possible flypoints to the graph

        Returns:
            List[Tuple]: A List of point Tuples in (x, y, z) format
        """
        points = []
        divider = 8
        for i in range(int(self.point.z), int(self.height), 60):
            for j in range(divider):
                x = (feet_to_meters(self.radius) + 5) * cos(
                    pi / divider * j * 2
                ) + self.point.x
                y = (feet_to_meters(self.radius) + 5) * sin(
                    pi / divider * j * 2
                ) + self.point.y
                points.append((x, y, i))
        return points


def feet_to_meters(feet):
    return feet * 0.3048
