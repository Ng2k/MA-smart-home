"""
@author: Nicola Guerra
@describe: This file contains the code for the abstract class for sensor nodes.
"""

from abc import ABC, abstractmethod
from typing import Dict

from core.sensors.types.sensor_reading import SensorReading, SensorType
from logger.factory import get_logger
from proto import sensor_pb2_grpc


class SensorNode(ABC):
    """
    Abstract class for a generic sensor node.
    Defines the common contract for all sensors.
    """

    def __init__(
        self,
        sensor_id: str,
        sensor_type: SensorType,
        stub: sensor_pb2_grpc.SensorServiceStub,
        interval: float = 2.0,
        logger_name: str = __name__,
    ):
        self.sensor_id = sensor_id
        self.sensor_type = sensor_type
        self.interval = interval
        self.running = False
        self.stub = stub
        self.logger = get_logger(logger_name)

    @abstractmethod
    def read_data(self) -> SensorReading:
        """
        Reads data from the sensor and returns a dictionary
        with standard keys (e.g., 'value', 'timestamp').
        """

    @abstractmethod
    def calibrate(self) -> None:
        """Executes any calibration operations for the sensor."""

    @abstractmethod
    def run(self) -> None:
        """Main loop for the sensor."""

    @abstractmethod
    def stop(self) -> None:
        """Stops the sensor."""

    def get_metadata(self) -> Dict[str, str]:
        """
        Returns common metadata for the sensor.
        """
        return {"id": self.sensor_id, "type": self.sensor_type.value}
