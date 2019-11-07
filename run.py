import json


def run():
    print('Hello World')

def import_file(file):
    interop_data = json.load(file)
    print(interop_data)

if __name__ == "__main__":
    run()