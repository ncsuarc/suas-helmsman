# SUAS-Helmsman
SUAS-Helmsman is ARC's pre path planning library for use in its path generation system. With the now more limited set up time in the SUAS competition, we set out to speed up path generation while removing some human error in the process. SUAS-Helmsman is built upon `NetworkX` and uses the A* path planning algorithm to create its paths with `Shapely` checking for collision.

## Usage
SUAS-Helmsman can be used either as a library installed via the `setup.py` or as a stand alone cli tool

### Library
- First import and construct `SUASGraph`, taking in the lost comms point in the constructor.
- After, add waypoints, obstacles and other POIs
- Run the `construct_path` function to generate the path
- Get the path via `path_lat_lon_alt`

Please refer to `run.py` or `vpython-map.py` for example usage

### CLI
The cli tool can be run via the `run.py` file

#### Arguments
- `--file, -f`: file path of the JSON file with interop info (./test-files/suas_2019_missions.json)
- `--drop, -d`: Toggle to generate drop point (True by default, False is off)
- `--off, -o`: Toggle to generate off axis location (True by default, False is off)
- `--obstacles`: Toggle to generate obstacles (True by default, False is off)


### Visualization
SUAS-Helmsman has a viewing tool built off of VPython and supports similar arguments to `run.py`
