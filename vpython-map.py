from pygeodesy.ecef import EcefCartesian
from suas_helmsman.data import feet_to_meters
import json
import argparse
from vpython import *

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-f",
        "--file",
        help="Path of interop file",
        default="./test-files/suas_2019_missions.json",
    )
    parser.add_argument(
        "--lost_comms", "-l", help="Show lost comms point", action="store_true"
    )
    parser.add_argument(
        "--boundaries", "-b", help="Show boundary polygon", action="store_true"
    )
    parser.add_argument("--waypoints", "-w", help="Show waypoints", action="store_true")
    parser.add_argument(
        "--search_grid", "-s", help="Show search grid polygon", action="store_true"
    )
    parser.add_argument(
        "--off_axis", "-oa", help="Show off axis point", action="store_true"
    )
    parser.add_argument(
        "--emergentLKP",
        "-e",
        help="Show emergent last known position",
        action="store_true",
    )
    parser.add_argument("--drop", "-d", help="Show drop point", action="store_true")
    parser.add_argument(
        "--obstacles", "-ob", help="Show obstacle polygons", action="store_true"
    )
    parser.add_argument(
        "--autogen", "-a", help="Show autogen path", action="store_true"
    )
    parsed_args = parser.parse_args()

    with open(parsed_args.file, "r") as json_file:
        interop_data = json.load(json_file)

    cartesian = EcefCartesian(
        interop_data["lostCommsPos"]["latitude"],
        interop_data["lostCommsPos"]["longitude"],
    )

    if not parsed_args.lost_comms:
        lcp_x, lcp_y, *_ = cartesian.forward(
            interop_data["lostCommsPos"]["latitude"],
            interop_data["lostCommsPos"]["longitude"],
        )
        sphere(pos=vector(lcp_x, lcp_y, 0), radius=25, color=color.red)

    if not parsed_args.boundaries:
        bounds = []
        for b in interop_data["flyZones"][0]["boundaryPoints"]:
            x, y, *_ = cartesian.forward(b["latitude"], b["longitude"])
            bounds.append((x, y, 0))
        pb = shapes.points(pos=bounds)
        extrusion(
            path=[vec(0, 0, interop_data["flyZones"][0]["altitudeMax"]), vec(0, 0, 0)],
            shape=pb,
            color=color.red,
            opacity=0.4,
        )

    if not parsed_args.waypoints:
        for w in interop_data["waypoints"]:
            way_x, way_y, *_ = cartesian.forward(w["latitude"], w["longitude"])
            sphere(
                pos=vector(way_x, way_y, w["altitude"]), radius=25, color=color.green
            )

    if not parsed_args.search_grid:
        sg = []
        for s in interop_data["searchGridPoints"]:
            x, y, *_ = cartesian.forward(s["latitude"], s["longitude"])
            sg.append((x, y, 0))
        psg = shapes.points(pos=sg)
        extrusion(
            path=[vec(0, 0, 0), vec(0, 0, -1)], shape=psg, color=color.blue, opacity=0.4
        )

    if not parsed_args.off_axis:
        oa_x, oa_y, *_ = cartesian.forward(
            interop_data["offAxisOdlcPos"]["latitude"],
            interop_data["offAxisOdlcPos"]["longitude"],
        )
        sphere(pos=vector(oa_x, oa_y, 0), radius=25, color=color.purple)

    if not parsed_args.emergentLKP:
        elkp_x, elkp_y, *_ = cartesian.forward(
            interop_data["emergentLastKnownPos"]["latitude"],
            interop_data["emergentLastKnownPos"]["longitude"],
        )
        sphere(pos=vector(elkp_x, elkp_y, 0), radius=25, color=color.cyan)

    if not parsed_args.drop:
        drop_x, drop_y, *_ = cartesian.forward(
            interop_data["airDropPos"]["latitude"],
            interop_data["airDropPos"]["longitude"],
        )
        sphere(pos=vector(drop_x, drop_y, 0), radius=25, color=color.black)

    if not parsed_args.obstacles:
        for o in interop_data["stationaryObstacles"]:
            x, y, *_ = cartesian.forward(o["latitude"], o["longitude"])
            cylinder(
                pos=vector(x, y, 0),
                axis=vector(0, 0, o["height"]),
                radius=feet_to_meters(o["radius"]),
                color=color.yellow,
                opacity=0.4,
            )

    if not parsed_args.autogen:
        circ = shapes.circle(radius=10)
        for i in range(len(interop_data["autogenPoints"]) - 1):
            x1, y1, *_ = cartesian.forward(
                interop_data["autogenPoints"][i]["latitude"],
                interop_data["autogenPoints"][i]["longitude"],
            )
            x2, y2, *_ = cartesian.forward(
                interop_data["autogenPoints"][i + 1]["latitude"],
                interop_data["autogenPoints"][i + 1]["longitude"],
            )
            extrusion(
                path=[
                    vec(x1, y1, interop_data["autogenPoints"][i]["altitude"]),
                    vec(x2, y2, interop_data["autogenPoints"][i + 1]["altitude"]),
                ],
                shape=circ,
                color=color.white,
            )
