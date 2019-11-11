import json
import sys, argparse
import pymavlink
from src.waypoint import Waypoint


def import_file(file):
    interop_data = json.load(file)
    return interop_data

def handle_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', help='Path of interop file')
    parsed_args = parser.parse_args(sys.argv[1:])
    return open(parsed_args.file)

def get_waypoints(interop_data):
    way = []
    for i in range(len(interop_data["waypoints"])):
        lat = interop_data['waypoints'][i]['latitude']
        lon = interop_data['waypoints'][i]['longitude']
        alt = interop_data['waypoints'][i]['altitude']
        way.append(Waypoint(lat, lon, alt))
    return way


if __name__ == "__main__":
    file = handle_args()
    interop_data = import_file(file)
    way = get_waypoints(interop_data)
    print(way)