# Autonomous Drone Mission System

This project enables autonomous drone flight using ArduPilot firmware, MAVLink/MAVSDK for communication, and supports both simulation (SITL) and real hardware deployment on Jetson Nano.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Project Setup](#project-setup)
- [Running Simulations](#running-simulations)
- [Creating Mission Files](#creating-mission-files)
- [Deploying to Jetson Nano](#deploying-to-jetson-nano)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

- **Operating System**: Ubuntu 20.04+ or Debian-based Linux
- **Python**: 3.8 or higher
- **Hardware** (for real deployment): 
  - Jetson Nano
  - ArduPilot-compatible flight controller (Pixhawk, Cube, etc.)
  - Drone frame with motors/ESCs

---

## Installation

### Step 1: Update System and Install Base Packages

```bash
# Update package lists
sudo apt update && sudo apt upgrade -y

# Install essential tools
sudo apt install -y \
    python3-full \
    python3-venv \
    git \
    pipx \
    build-essential
```

### Step 2: Set Up pipx

```bash
# Configure pipx path
pipx ensurepath

# Reload bash configuration
source ~/.bashrc
```

### Step 3: Install MAVProxy

```bash
# Install MAVProxy in isolated environment
pipx install MAVProxy

# Verify installation
mavproxy.py --help
```

### Step 4: Install ArduPilot SITL Build Dependencies

```bash
# Install system-level Python packages for building ArduPilot
sudo apt install -y \
    python3-empy \
    python3-serial \
    python3-setuptools

# Install additional build dependencies
pip install --break-system-packages dronecan pexpect
```

### Step 5: Clone and Build ArduPilot SITL

```bash
# Clone ArduPilot repository
cd ~
git clone https://github.com/ArduPilot/ardupilot.git
cd ardupilot

# Initialize submodules
git submodule update --init --recursive

# Configure for SITL (Software In The Loop)
./waf configure --board sitl

# Build ArduCopter
./waf copter
```

**Expected output**: Build should complete with `'copter' finished successfully`

### Step 6: Add ArduPilot Tools to PATH

```bash
# Add to PATH permanently
echo 'export PATH=$PATH:$HOME/ardupilot/Tools/autotest' >> ~/.bashrc

# Reload configuration
source ~/.bashrc

# Verify sim_vehicle.py is accessible
which sim_vehicle.py
```

---

## Project Setup

### Step 1: Create Project Directory and Virtual Environment

```bash
# Create project directory
cd ~
mkdir -p drone_project
cd drone_project

# Create Python virtual environment
python3 -m venv drone_env

# Activate virtual environment
source drone_env/bin/activate
```

### Step 2: Install Python Dependencies

```bash
# With virtual environment activated
pip install --upgrade pip

# Install required packages
pip install \
    mavsdk \
    pymavlink \
    numpy \
    future
```

### Step 3: Create Project Files

#### Create `drone_mission.py`

Copy the Autonomous Drone Mission Script from the artifacts above and save it as `drone_mission.py`.

```bash
nano drone_mission.py
# Paste the script content, then Ctrl+X, Y, Enter to save
```

#### Create `mission.waypoints`

Copy the Sample Mission File and save it as `mission.waypoints`.

```bash
nano mission.waypoints
# Paste the mission content, then Ctrl+X, Y, Enter to save
```

#### Create `start_simulation.sh`

Copy the SITL Simulation Launcher script and save it.

```bash
nano start_simulation.sh
# Paste the launcher script, then Ctrl+X, Y, Enter to save
```

### Step 4: Make Scripts Executable

```bash
chmod +x drone_mission.py
chmod +x start_simulation.sh
```

---

## Running Simulations

### Terminal 1: Start ArduPilot SITL Simulator

```bash
cd ~/drone_project
./start_simulation.sh
```

**Expected output:**
```
Connect tcp:127.0.0.1:5760 source_system=255
Waiting for heartbeat from tcp:127.0.0.1:5760
MAV> Received 520 parameters
```

You should see:
- ArduCopter simulation running
- MAVProxy console
- Map window (if GUI available)

### Terminal 2: Run Mission Script

Open a new terminal:

```bash
cd ~/drone_project

# Activate virtual environment
source drone_env/bin/activate

# Run mission
python3 drone_mission.py mission.waypoints udp://:14540
```

**Expected output:**
```
Connecting to drone on udp://:14540...
Drone connected!
Waiting for GPS fix...
GPS fix acquired!
Parsing mission file: mission.waypoints
Uploading 6 mission items...
Mission uploaded successfully!
Arming drone...
Starting mission...
Mission progress: 1/6
Mission progress: 2/6
...
Mission completed!
Landing in progress...
Landed successfully!
Disarming...
Mission complete!
```

### Monitoring the Simulation

In the MAVProxy console, you can type commands:
- `mode GUIDED` - Switch to guided mode
- `arm throttle` - Arm motors
- `wp list` - List waypoints
- `status` - Show current status

---

## Creating Mission Files

### Using Mission Planner (Windows)

1. Open Mission Planner
2. Click "Flight Plan" tab
3. Right-click on map to add waypoints
4. Set altitude for each waypoint
5. File → Save WP File → Choose location
6. Transfer `.waypoints` file to Linux machine

### Manual Creation

Mission file format (QGC WPL 110):
```
QGC WPL 110
<index>	<current>	<coord_frame>	<command>	<param1>	<param2>	<param3>	<param4>	<lat>	<lon>	<alt>	<autocontinue>
```

**Important commands:**
- `16` = Waypoint
- `22` = Takeoff
- `21` = Land
- `20` = Return to Launch

**Example waypoint:**
```
2	0	3	16	0.0	0.0	0.0	0.0	37.403260	-122.077700	20.0	1
```

### Mission File Structure

1. **Line 0**: Home position (required)
2. **Line 1**: Takeoff command (command 22)
3. **Lines 2-N**: Waypoints (command 16)
4. **Last line**: Land command (command 21) - optional

---

## Deploying to Jetson Nano

### Hardware Setup

1. Connect flight controller to Jetson Nano via:
   - UART/TELEM port → `/dev/ttyTHS1`
   - USB cable → `/dev/ttyUSB0`

2. Configure ArduPilot parameters on flight controller:
   ```
   SERIAL2_PROTOCOL = 2 (MAVLink2)
   SERIAL2_BAUD = 921600
   ```

### Software Setup on Jetson Nano

```bash
# Install system packages
sudo apt update
sudo apt install -y python3-full python3-venv python3-pip

# Create project directory
mkdir -p ~/drone_project
cd ~/drone_project

# Create virtual environment
python3 -m venv drone_env
source drone_env/bin/activate

# Install dependencies
pip install mavsdk pymavlink numpy

# Copy your mission script and waypoint files
# (Transfer drone_mission.py and mission.waypoints from dev machine)
```

### Running on Real Hardware

```bash
cd ~/drone_project
source drone_env/bin/activate

# For UART connection (TELEM2 port)
python3 drone_mission.py mission.waypoints serial:///dev/ttyTHS1:921600

# For USB connection
python3 drone_mission.py mission.waypoints serial:///dev/ttyUSB0:57600
```

### Check Serial Permissions

```bash
# Add user to dialout group
sudo usermod -a -G dialout $USER

# Log out and back in, or reboot

# Verify port exists
ls -l /dev/ttyTHS1
ls -l /dev/ttyUSB0
```

---

## Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'future'`

**Solution:**
```bash
source ~/drone_project/drone_env/bin/activate
pip install future
```

### Issue: `externally-managed-environment` error

**Solution:** Always use virtual environment, not system pip:
```bash
cd ~/drone_project
source drone_env/bin/activate
pip install <package>
```

### Issue: ArduPilot build fails with `No module named 'dronecan'`

**Solution:**
```bash
pip install --break-system-packages dronecan pexpect
cd ~/ardupilot
./waf clean
./waf configure --board sitl
./waf copter
```

### Issue: Mission script can't connect to drone

**Solutions:**

1. Check SITL is running in another terminal
2. Verify connection string:
   - Simulation: `udp://:14540`
   - Serial: `serial:///dev/ttyTHS1:921600`
3. Check MAVProxy output in Terminal 1 for errors

### Issue: `MissionItem.__init__() missing required argument`

**Solution:** Make sure you're using the updated version of `drone_mission.py` that includes the `vehicle_action` parameter.

### Issue: No GPS fix in simulation

**Solution:** Wait 10-20 seconds. SITL needs time to initialize GPS. Check MAVProxy console for GPS status:
```
MAV> status
```

### Issue: Drone won't arm

**Possible causes:**
- No GPS fix (wait longer)
- Safety checks failing
- Simulation not ready

**Check in MAVProxy:**
```
MAV> arm throttle
```

### Issue: Permission denied on `/dev/ttyTHS1` or `/dev/ttyUSB0`

**Solution:**
```bash
sudo chmod 666 /dev/ttyTHS1
# Or add user to dialout group
sudo usermod -a -G dialout $USER
# Then log out and back in
```

---

## Command Reference

### Virtual Environment Commands

```bash
# Activate virtual environment
source ~/drone_project/drone_env/bin/activate

# Deactivate virtual environment
deactivate

# Check installed packages
pip list
```

### SITL Simulation Commands

```bash
# Start default simulation
./start_simulation.sh

# Start with custom location (lat,lon,alt,heading)
sim_vehicle.py -v ArduCopter -L 37.4029,-122.0796,20,0 --out=udp:127.0.0.1:14540

# Start without map/console
sim_vehicle.py -v ArduCopter --out=udp:127.0.0.1:14540
```

### Mission Script Commands

```bash
# Run with default connection
python3 drone_mission.py mission.waypoints

# Run with custom connection
python3 drone_mission.py mission.waypoints udp://:14540

# Run on real hardware
python3 drone_mission.py mission.waypoints serial:///dev/ttyTHS1:921600
```

---

## Project Structure

```
~/drone_project/
├── drone_env/              # Python virtual environment
├── drone_mission.py        # Main mission script
├── mission.waypoints       # Mission file
├── start_simulation.sh     # SITL launcher script
└── logs/                   # Flight logs (optional)
```

---

## Safety Reminders

⚠️ **Important Safety Notes:**

1. **Test in simulation first** - Always verify missions in SITL before real flight
2. **Check mission files** - Verify waypoints, altitudes, and coordinates
3. **Pre-flight checks** - Always perform standard pre-flight safety checks
4. **Emergency procedures** - Know how to take manual control and emergency land
5. **Legal compliance** - Follow local drone regulations and airspace rules
6. **Safe area** - Fly only in approved areas away from people and property

---

## Additional Resources

- [ArduPilot Documentation](https://ardupilot.org/copter/)
- [MAVSDK Documentation](https://mavsdk.mavlink.io/main/en/)
- [MAVLink Protocol](https://mavlink.io/en/)
- [Mission Planner](https://ardupilot.org/planner/)

---

## License

This project is for educational purposes. Follow all local regulations and safety guidelines when operating drones.
