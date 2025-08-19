"""
@author: Nicola Guerra
@description: This module defines the pydantic model for sensor readings.
"""

import math
from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field, field_validator

SensorType = Literal["temperature", "humidity", "motion_ir", "position"]
UnitOfMeasure = Literal["°C", "%", "lux", "boolean", "integer", "float"]


class SensorReading(BaseModel):
    """Model for sensor readings."""

    sensor_id: str = Field(..., min_length=1)
    sensor_type: SensorType = Field(..., description="Type of sensor")
    value: float = Field(..., description="Value measured from the sensor")
    unit: UnitOfMeasure = Field(..., description="Unit of measure")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp of the reading",
    )

    @field_validator("value")
    def check_value(cls, v):
        if v is None:
            raise ValueError("The value cannot be None")
        if isinstance(v, str):
            raise ValueError("The value cannot be a string")
        if isinstance(v, float) and math.isnan(v):
            raise ValueError("The value cannot be NaN")
        return v
