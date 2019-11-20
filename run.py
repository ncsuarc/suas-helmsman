import json
import sys, argparse
from pymavlink import mavwp, mavutil
from src.waypoint import Waypoint

manager = mavwp.MAVWPLoader()


def import_file(file):
    interop_data = json.load(file)
    return interop_data


def handle_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", help="Path of interop file", required=True)
    parsed_args = parser.parse_args(sys.argv[1:])
    return open(parsed_args.file)


def get_waypoints(interop_data):
    way = []
    for i in range(len(interop_data["waypoints"])):
        lat = interop_data["waypoints"][i]["latitude"]
        lon = interop_data["waypoints"][i]["longitude"]
        alt = interop_data["waypoints"][i]["altitude"]
        way.append(Waypoint(lat, lon, alt))
    return way


def add_waypoints(way):
    for w in way:
        manager.add_latlonalt(w.latitude, w.longitude, w.altitude)


def send_waypoints():
    master = mavutil.mavlink_connection("udp:localhost:14551")
    master.wait_heartbeat(blocking=True)
    master.waypoint_clear_all_send()
    master.waypoint_count_send(manager.count())

    for i in range(manager.count()):
        msg = master.recv_match(type=["MISSION_REQUEST"], blocking=True)
        master.mav.send(manager.wp(msg.seq))


if __name__ == "__main__":
    file = handle_args()
    interop_data = import_file(file)
    way = get_waypoints(interop_data)
    add_waypoints(way)
    send_waypoints()
