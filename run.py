import json
import sys, argparse

file = None

def import_file(file):
    interop_data = json.load(file)
    print(interop_data["waypoints"])

def handle_args():
    global file
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', help='Path of interop file')
    parsed_args = parser.parse_args(sys.argv[1:])
    file = open(parsed_args.file)

if __name__ == "__main__":
    handle_args()
    import_file(file)