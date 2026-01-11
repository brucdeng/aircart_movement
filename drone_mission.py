#!/usr/bin/env python3
"""
Autonomous Drone Mission Script (FINAL)
ArduPilot + MAVSDK Python
Headless / No UI required
"""

import asyncio
import sys
from mavsdk import System
from mavsdk.mission import MissionItem, MissionPlan


class MissionParser:
    MAV_CMD_NAV_WAYPOINT = 16
    MAV_CMD_NAV_TAKEOFF = 22

    @staticmethod
    def parse_waypoints_file(filepath):
        takeoff_item = None
        waypoint_items = []

        with open(filepath, "r") as f:
            lines = f.readlines()

        for line in lines[1:]:
            parts = line.strip().split("\t")
            if len(parts) < 12:
                continue

            command = int(parts[3])
            if command not in (16, 22):
                continue

            lat = float(parts[8])
            lon = float(parts[9])
            alt = float(parts[10])

            item = MissionItem(
                latitude_deg=lat,
                longitude_deg=lon,
                relative_altitude_m=alt,
                speed_m_s=float("nan"),
                is_fly_through=True,
                gimbal_pitch_deg=float("nan"),
                gimbal_yaw_deg=float("nan"),
                camera_action=MissionItem.CameraAction.NONE,
                loiter_time_s=float("nan"),
                camera_photo_interval_s=float("nan"),
                acceptance_radius_m=float("nan"),
                yaw_deg=float("nan"),
                camera_photo_distance_m=float("nan"),
                vehicle_action=MissionItem.VehicleAction.NONE,
            )

            if command == 22:
                takeoff_item = item
            else:
                waypoint_items.append(item)

        if takeoff_item is None:
            raise RuntimeError("Mission file missing TAKEOFF command")

        return takeoff_item, [takeoff_item] + waypoint_items


class DroneController:
    def __init__(self, connection="udpin://0.0.0.0:14540"):
        self.drone = System()
        self.connection = connection
        self.takeoff_altitude = None

    async def connect(self):
        print(f"Connecting to drone on {self.connection}...")
        await self.drone.connect(system_address=self.connection)

        async for state in self.drone.core.connection_state():
            if state.is_connected:
                print("Drone connected")
                break

    async def wait_for_gps(self):
        print("Waiting for GPS fix...")
        async for health in self.drone.telemetry.health():
            if health.is_global_position_ok:
                print("GPS fix acquired")
                break

    async def upload_mission(self, mission_file):
        print(f"Loading mission: {mission_file}")
        takeoff_item, items = MissionParser.parse_waypoints_file(mission_file)
        self.takeoff_altitude = takeoff_item.relative_altitude_m

        print(f"Uploading {len(items)} mission items...")
        await self.drone.mission.upload_mission(MissionPlan(items))

        await self.drone.mission.set_current_mission_item(0)
        await self.drone.mission.set_return_to_launch_after_mission(True)

        print("Mission uploaded successfully")

    async def arm(self):
        print("Arming...")
        await self.drone.action.arm()

        async for armed in self.drone.telemetry.armed():
            if armed:
                print("Drone armed")
                break

    async def execute_mission(self):
        print(f"Setting takeoff altitude: {self.takeoff_altitude} m")
        await self.drone.action.set_takeoff_altitude(self.takeoff_altitude)

        print("Taking off...")
        await self.drone.action.takeoff()

        async for in_air in self.drone.telemetry.in_air():
            if in_air:
                print("Drone is airborne")
                break
            await asyncio.sleep(0.5)

        await asyncio.sleep(2)

        print("Starting mission...")
        await self.drone.mission.start_mission()

        async for progress in self.drone.mission.mission_progress():
            print(f"Mission progress: {progress.current}/{progress.total}")
            if progress.current == progress.total:
                print("Mission completed")
                break
            await asyncio.sleep(1)

    async def land(self):
        print("Landing...")
        await self.drone.action.land()

        async for in_air in self.drone.telemetry.in_air():
            if not in_air:
                print("Landed")
                break

    async def run(self, mission_file):
        await self.connect()
        await self.wait_for_gps()
        await self.upload_mission(mission_file)
        await self.arm()
        await self.execute_mission()
        await self.land()
        await self.drone.action.disarm()
        print("Mission finished successfully")


async def main():
    if len(sys.argv) < 2:
        print("Usage: python3 drone_mission.py mission.waypoints [connection]")
        sys.exit(1)

    mission_file = sys.argv[1]
    conn = sys.argv[2] if len(sys.argv) > 2 else "udpin://0.0.0.0:14540"

    controller = DroneController(conn)
    await controller.run(mission_file)


if __name__ == "__main__":
    asyncio.run(main())
