# SDA
This is the repo for the for the Path Planning Autogeneration Service (Name Pending).

## Usage
`python3 run.py`

### Arguments
- `--file, -f`: file path of the JSON file with interop info (./test-files/suas_2019_missions.json)
- `--ip, -i`: IP of the Pixhawk to transmit data to (129.168.1.21:14550)
- `--drop, -d`: Toggle to generate drop point (True by default, False is off)
- `--off, -o`: Toggle to generate off axis location (True by default, False is off)
- `--obstacles`: Toggle to generate obstacles (True by default, False is off)