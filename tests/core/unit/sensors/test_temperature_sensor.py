"""
@description: Unit tests for the TemperatureSensor class.
@author: Nicola Guerra
"""

from core.sensors.temperature_sensor import TemperatureSensor
from core.sensors.types.sensor_reading import (SensorReading, SensorType,
                                               UnitOfMeasure)


def test_constructor_sets_id_and_type():
    ts = TemperatureSensor("t-1")
    assert ts.sensor_id == "t-1"
    assert ts.sensor_type == SensorType.TEMPERATURE


def test_get_metadata_returns_expected_dict():
    ts = TemperatureSensor("t-2")
    meta = ts.get_metadata()
    assert meta == {"id": "t-2", "type": SensorType.TEMPERATURE.value}


def test_read_data_returns_sensor_reading():
    ts = TemperatureSensor("t-3")
    reading = ts.read_data()
    assert isinstance(reading, SensorReading)
    assert reading.sensor_id == "t-3"
    assert reading.sensor_type == SensorType.TEMPERATURE
    assert reading.value == 25.0
    assert reading.unit == UnitOfMeasure.CELSIUS
    assert hasattr(reading, "timestamp")


def test_calibrate_logs_info(caplog):
    from unittest.mock import patch

    ts = TemperatureSensor("t-4")
    with patch.object(ts.logger, "info") as mock_info:
        ts.calibrate()
        mock_info.assert_called_once_with("Calibrating temperature sensor t-4")


def test_read_data_edge_case_sensor_id_empty():
    ts = TemperatureSensor("")
    import pytest
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        ts.read_data()


def test_read_data_edge_case_sensor_id_special():
    ts = TemperatureSensor("!@#$_sensor")
    reading = ts.read_data()
    assert reading.sensor_id == "!@#$_sensor"


def test_logger_is_initialized():
    ts = TemperatureSensor("t-5")
    assert hasattr(ts, "logger")
    assert callable(getattr(ts.logger, "info", None))
