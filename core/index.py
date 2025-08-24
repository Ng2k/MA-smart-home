"""
@description: This is the main entry point for the smart home system.
@author: Nicola Guerra
"""

import os

from dotenv import load_dotenv

from core.sensors import TemperatureSensor
from logger.factory import get_logger

load_dotenv(dotenv_path=os.getenv("PYTHON_APP", ".development.env"), override=True)
logger = get_logger(__name__)


def setup_sensors() -> None:
    """Set up the sensors for the smart home system."""
    temperature_sensor = TemperatureSensor(sensor_id="living_room_temp")
    temperature_sensor.calibrate()


if __name__ == "__main__":
    setup_sensors()
