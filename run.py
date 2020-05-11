import argparse
import json
import sys
import time

from pymavlink import mavutil, mavwp

from autogen import suas_graph


def upload_waypoints(graph, ip):
    """Function to upload the waypoints to the plane.

    Uses pymavlink to upload the generated flight path from the NetworkX graph
    Must be run after construct_graph() if using the autogen generator. This adds
    all waypoints to the mavlink waypoint manager, establishes a connect with the plane
    and then sends each waypoint to the plane.

    Args:
        graph (SUASGraph): An instance of SUASGraph
        ip: the ip of the plane
    """
    # Construct Waypoint Manager
    manager = mavwp.MAVWPLoader()
    # Add inital point to manager, voided and not sent to plane
    manager.add_latlonalt(
        graph.starting_point["latitude"], graph.starting_point["longitude"], 150
    )
    # Adds each waypoint to the waypoint manager
    for p in graph.path_lat_lon_alt():
        manager.add_latlonalt(*p)

    # Establish connect to plane at ip
    master = mavutil.mavlink_connection("udp:" + ip)
    master.wait_heartbeat(blocking=True)
    master.waypoint_clear_all_send()
    master.waypoint_count_send(manager.count())

    # Send each point as requested
    for _ in range(manager.count()):
        msg = master.recv_match(type=["MISSION_REQUEST"], blocking=True)
        master.mav.send(manager.wp(msg.seq))


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
    # Adds waypoint boundaries to map
    g.add_boundaries(interop_data["flyZones"][0]["boundaryPoints"])
    # Adds waypoint to map
    g.add_waypoints(interop_data["waypoints"])
    # Adds obstacles to map
    if obstacles:
        g.add_obstacles(interop_data["stationaryObstacles"])
    # Adds drop point to map
    if drop:
        g.add_drop(interop_data["airDropPos"])
    # Adds off-axis point to map
    if off_axis:
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
        "-d", "--drop", help="Toggle to generate drop point", default=True,
    )
    parser.add_argument(
        "-o", "--off", help="Toggle to generate off axis point", default=True,
    )
    parser.add_argument(
        "--obstacles", help="Toggle for generating obstacles", default=True,
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

    # Upload Flight Path
    upload_waypoints(graph, parsed_args.ip)
