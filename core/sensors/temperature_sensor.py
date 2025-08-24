"""
@description: Temperature sensor class
@author: Nicola Guerra
"""

import random
import time

import grpc

from core.sensors import SensorNode
from core.sensors.types.sensor_reading import (SensorReading, SensorType,
                                               UnitOfMeasure)
from proto import sensor_pb2, sensor_pb2_grpc


class TemperatureSensor(SensorNode):
    """Temperature sensor class"""

    def __init__(
        self,
        sensor_id: str,
        stub: sensor_pb2_grpc.SensorServiceStub,
        interval: float = 2.0,
    ):
        super().__init__(
            sensor_id=sensor_id,
            sensor_type=SensorType.TEMPERATURE,
            stub=stub,
            interval=interval,
            logger_name=self.__class__.__name__,
        )

    def read_data(self) -> SensorReading:
        return SensorReading(
            sensor_id=self.sensor_id,
            sensor_type=self.sensor_type,
            value=random.uniform(18, 30),
            unit=UnitOfMeasure.CELSIUS,
        )

    def calibrate(self):
        self.logger.info(f"Calibrating temperature sensor {self.sensor_id}")

    def run(self) -> None:
        self.running = True
        while self.running:
            read = self.read_data()

            reading = sensor_pb2.SensorReading(
                sensor_id=self.sensor_id,
                sensor_type=self.sensor_type.value,
                value=read.value,
                timestamp=int(time.time() * 1000),
            )  # type: ignore[attr-defined]
            request = sensor_pb2.SensorRequest(reading=reading)  # type: ignore[attr-defined]

            try:
                response = self.stub.SendReading(request)
                self.logger.info(
                    (
                        f"[{self.sensor_id}] Inviato: "
                        f"{read.value:.2f} ({self.sensor_type}) → {response.message}"
                    )
                )
            except grpc.RpcError as e:
                self.logger.error(f"[{self.sensor_id}] Errore gRPC: {e.details()}")

            time.sleep(self.interval)

    def stop(self) -> None:
        self.running = False
