"""
@description: Unit tests for the TemperatureSensor class.
@author: Nicola Guerra
"""

import logging
from datetime import datetime

import pytest

from core.sensors.temperature_sensor import TemperatureSensor
from core.sensors.types.sensor_reading import (SensorReading, SensorType,
                                               UnitOfMeasure)


def test_constructor_and_metadata():
    ts = TemperatureSensor("sensor-1")
    assert ts.sensor_id == "sensor-1"
    assert ts.sensor_type == SensorType.TEMPERATURE
    meta = ts.get_metadata()
    assert meta["id"] == "sensor-1"
    assert meta["type"] == SensorType.TEMPERATURE.value


def test_read_data_returns_sensor_reading():
    ts = TemperatureSensor("t-2")
    reading = ts.read_data()
    assert isinstance(reading, SensorReading)
    assert reading.sensor_id == "t-2"
    assert reading.sensor_type == SensorType.TEMPERATURE
    assert reading.value == pytest.approx(25.0)
    assert reading.unit == UnitOfMeasure.CELSIUS
    # timestamp is present and timezone-aware
    assert isinstance(reading.timestamp, datetime)
    assert (
        reading.timestamp.tzinfo is not None
        and reading.timestamp.tzinfo.utcoffset(reading.timestamp) is not None
    )


def test_calibrate_logs_info(caplog):
    ts = TemperatureSensor("cal-1")
    caplog.set_level(logging.INFO)
    ts.calibrate()
    # Ensure an info-level message was logged and contains the sensor id
    msgs = [r.getMessage() for r in caplog.records if r.levelno == logging.INFO]
    assert any("Calibrating temperature sensor" in m and "cal-1" in m for m in msgs)
