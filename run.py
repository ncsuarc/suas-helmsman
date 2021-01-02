import argparse
import json
import time

from autogen import suas_graph


def upload_json(graph, json_file):
    json_file["autogenPoints"] = []

    for lat, lon, alt in graph.path_lat_lon_alt():
        json_file["autogenPoints"].append(
            {"latitude": lat, "longitude": lon, "altitude": alt}
        )

    with open("./autogen_output.json", "w") as output:
        output.write(json.dumps(json_file, indent=2))


def construct_graph(interop_data, drop, off_axis, obstacles):
    """Constructs an Instance of SUASGraph.

    This generates a SUASGraph from the interop data provided.
    This generates all the points of interest and possible paths
    while accounting for obstacles.

    Args:
        interop_data (Dictionary): JSON file of the interop data
        parsed_args (argparse.ArgumentParser): The argument parser,
        used to determine whether of not to generate features.

    Returns:
        SUASGraph: The constructed graph
    """
    # Initial graph constructor
    g = suas_graph.SUASGraph(
        interop_data["lostCommsPos"],
        (
            int(interop_data["flyZones"][0]["altitudeMin"]),
            int(interop_data["flyZones"][0]["altitudeMax"]),
        ),
    )
    print("Adding Boundaries to Graph")
    # Adds waypoint boundaries to map
    g.add_boundaries(interop_data["flyZones"][0]["boundaryPoints"])
    # Adds waypoint to map
    print("Adding Waypoints to Graph")
    g.add_waypoints(interop_data["waypoints"])
    # Adds obstacles to map
    if obstacles:
        print("Adding Obstacles to Graph")
        g.add_obstacles(interop_data["stationaryObstacles"])
    # Adds drop point to map
    if drop:
        print("Adding Drop to Graph")
        g.add_drop(interop_data["airDropPos"])
    # Adds off-axis point to map
    if off_axis:
        print("Adding Off Axis to Graph")
        g.add_off_axis(interop_data["offAxisOdlcPos"])
    # Constructs possible flight paths
    g.add_edges()
    # Constructs the flight path using A* Algorithm
    g.construct_path()
    return g


if __name__ == "__main__":
    """Main function for the program.

    Example:
        python3 run.py -f ~/file/path.json -i 192.168.1.51 -o=False -d=False
    """
    # Add command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-f",
        "--file",
        help="Path of interop file",
        default="./test-files/suas_2019_missions.json",
    )
    parser.add_argument(
        "-i",
        "--ip",
        help="IP of the pixhawk to transmit data to",
        default="localhost:14550",
    )
    parser.add_argument(
        "-d",
        "--drop",
        help="Toggle to generate drop point",
        action="store_false",
    )
    parser.add_argument(
        "-o",
        "--off",
        help="Toggle to generate off axis point",
        action="store_false",
    )
    parser.add_argument(
        "--obstacles",
        help="Toggle for generating obstacles",
        action="store_false",
    )
    parsed_args = parser.parse_args()

    # Open Interop File
    with open(parsed_args.file, "r") as json_file:
        interop_data = json.load(json_file)

    # Construct Graph
    time1 = time.process_time()
    graph = construct_graph(
        interop_data, parsed_args.drop, parsed_args.off, parsed_args.obstacles
    )
    time2 = time.process_time()
    print("Graph: ", (time2 - time1))
    # print(graph.path)
    # Upload Flight Path

    upload_json(graph, interop_data)
