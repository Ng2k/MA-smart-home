"""
@description: Enumeration of sensor types.
@author: Nicola Guerra
"""

from enum import Enum


class SensorType(Enum):
    """Enumeration of sensor types."""

    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    LIGHT = "light"
    MOTION = "motion"
