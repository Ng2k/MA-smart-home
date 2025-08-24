"""
@description: Sensor manager class
@author: Nicola Guerra
"""

import threading
from typing import List

import grpc

from core.sensors import SensorNode, TemperatureSensor
from core.sensors.sensor_enum import SensorType
from logger.factory import get_logger
from proto import sensor_pb2_grpc

SENSOR_TYPE_MAPPING = {
    SensorType.TEMPERATURE.value: TemperatureSensor,
}


class SensorManager:
    """Manager for handling sensor nodes.

    Attributes:
        sensors (List[SensorNode]): List of managed sensors.
        threads (List[threading.Thread]): Threads associated with the sensors.
    """

    def __init__(self, server_address: str) -> None:
        self.server_address = server_address
        self.sensors: List[SensorNode] = []
        self.threads: List[threading.Thread] = []
        self.logger = get_logger(self.__class__.__name__)

        channel = grpc.insecure_channel(server_address)
        self.stub = sensor_pb2_grpc.SensorServiceStub(channel)

    def add_sensor(self, sensor_type: SensorType, interval: float = 2.0) -> None:
        """Add a sensor to the manager.

        :param sensor_type (SensorType): type of the sensor to add
        :param interval (float): interval for the sensor
        :return: None
        """
        sensor: SensorNode = SENSOR_TYPE_MAPPING[sensor_type.value](
            sensor_id=f"sensor_{len(self.sensors) + 1}",
            stub=self.stub,
            interval=interval,
        )

        self.logger.info(f"Adding sensor: {sensor.sensor_id}")
        self.sensors.append(sensor)

    def start_all(self) -> None:
        """Start all sensors in separate threads."""
        for sensor in self.sensors:
            thread = threading.Thread(target=sensor.run, daemon=True)
            self.threads.append(thread)
            thread.start()
        self.logger.info("✅ All sensors have been started.")

    def stop_all(self) -> None:
        """Stop all sensors and wait for threads to finish."""
        for sensor in self.sensors:
            sensor.stop()
        for thread in self.threads:
            thread.join()
        self.logger.info("🛑 All sensors have been stopped.")
