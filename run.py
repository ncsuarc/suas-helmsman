import json
import sys, argparse
from pymavlink import mavwp, mavutil
from src.waypoint import Waypoint

manager = mavwp.MAVWPLoader()

def get_waypoints(interop_data):
    return [
        Waypoint(w["latitude"], w["longitude"], w["altitude"])
        for w in interop_data["waypoints"]
    ]


def add_waypoints(way):
    for w in way:
        manager.add_latlonalt(w.latitude, w.longitude, w.altitude)


def send_waypoints():
    master = mavutil.mavlink_connection("udp:localhost:14551")
    master.wait_heartbeat(blocking=True)
    master.waypoint_clear_all_send()
    master.waypoint_count_send(manager.count())

    for _ in range(manager.count()):
        msg = master.recv_match(type=["MISSION_REQUEST"], blocking=True)
        master.mav.send(manager.wp(msg.seq))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", help="Path of interop file", required=True)
    parsed_args = parser.parse_args()
    file = parsed_args.file

    interop_data = json.load(file)
    way = get_waypoints(interop_data)
    add_waypoints(way)
    send_waypoints()
