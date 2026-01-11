#!/bin/bash
# ArduPilot SITL Simulation Launcher
# This script starts the simulation environment for testing

echo "Starting ArduPilot SITL Simulation..."

# Activate virtual environment if it exists
if [ -d "$HOME/drone_project/drone_env" ]; then
    source "$HOME/drone_project/drone_env/bin/activate"
fi

# Set the ArduPilot directory
ARDUPILOT_DIR="$HOME/ardupilot"

# Change to ArduPilot directory
cd "$ARDUPILOT_DIR/ArduCopter" || { echo "ArduPilot directory not found!"; exit 1; }

# Launch SITL with default parameters
# -v ArduCopter: Vehicle type
# --console: Open MAVProxy console
# --map: Open map window
# -L: Location (RATCLab is a default location)
# --out: Output connection for MAVSDK (UDP port 14540)

sim_vehicle.py -v ArduCopter \
    --console \
    --map \
    -L CMAC \
    --out=udp:127.0.0.1:14540

# Alternative locations you can use:
# -L CMAC (California)
# -L AVC (AVC Sparkfun)
# -L KSFO (San Francisco Airport)
# 
# To specify custom location:
# -L 37.4029,-122.0796,20,0 (lat,lon,alt,heading)
