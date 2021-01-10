from autogen.data import Obstacle, feet_to_meters
from autogen.suas_graph import solve_intersection
from shapely.geometry import LinearRing, LineString, Point
from pygeodesy.ecef import EcefCartesian
import json

if __name__ == "__main__":
    with open("autogen_output.json", "r") as json_file:
        interop_data = json.load(json_file)

    cartesian = EcefCartesian(
        interop_data["lostCommsPos"]["latitude"],
        interop_data["lostCommsPos"]["longitude"],
    )

    p1 = {"latitude": 38.14535, "longitude": -76.428675, "altitude": 300.0}
    p2 = {
        "latitude": 38.1508972222222,
        "longitude": -76.4292972222222,
        "altitude": 300.0,
    }
    x1, y1, *_ = cartesian.forward(
        p1["latitude"],
        p1["longitude"],
    )
    x2, y2, *_ = cartesian.forward(
        p2["latitude"],
        p2["longitude"],
    )
    po = {
        "latitude": 38.148711,
        "longitude": -76.429061,
        "radius": 300.0,
        "height": 750.0,
    }
    xo1, yo1, *_ = cartesian.forward(
        po["latitude"],
        po["longitude"],
    )

    seg = LineString([Point(x1, y1, p1["altitude"]), Point(x2, y2, p2["altitude"])])
    obi = Obstacle(Point(xo1, yo1, 0), feet_to_meters(po["radius"]), po["height"])
    print(solve_intersection(obi, seg))
