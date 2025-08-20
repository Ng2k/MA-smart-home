"""
@description: Temperature sensor class
@author: Nicola Guerra
"""

from core.sensors.sensor_node import SensorNode
from core.sensors.types.sensor_reading import SensorReading, UnitOfMeasure, SensorType

class TemperatureSensor(SensorNode):
    """Temperature sensor class"""
    def __init__(self, sensor_id: str):
        super().__init__(sensor_id, SensorType.TEMPERATURE)

    def read_data(self) -> SensorReading:
        return SensorReading(
            sensor_id=self.sensor_id,
            sensor_type=self.sensor_type,
            value=25.0,
            unit=UnitOfMeasure.CELSIUS
        )
