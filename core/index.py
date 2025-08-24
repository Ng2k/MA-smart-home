"""
@description: This is the main entry point for the smart home system.
@author: Nicola Guerra
"""

import os
import time

from dotenv import load_dotenv

from core.sensors import SensorManager, SensorNode, SensorType
from logger.factory import get_logger

load_dotenv(dotenv_path=os.getenv("PYTHON_APP", ".development.env"), override=True)
logger = get_logger(__name__)

manager = SensorManager(os.getenv("GRPC_SERVER_ADDRESS", "localhost:50051"))


def setup_sensors() -> None:
    """Set up the sensors for the smart home system."""
    manager.add_sensor(sensor_type=SensorType.TEMPERATURE, interval=2.0)
    manager.add_sensor(sensor_type=SensorType.TEMPERATURE, interval=3.0)
    manager.add_sensor(sensor_type=SensorType.TEMPERATURE, interval=5.0)


if __name__ == "__main__":
    setup_sensors()

    try:
        manager.start_all()
        time.sleep(20)  # Simuliamo 20 secondi di esecuzione
    finally:
        manager.stop_all()
