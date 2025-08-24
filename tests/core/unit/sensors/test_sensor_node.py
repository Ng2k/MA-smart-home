"""
Unit tests for the abstract SensorNode class.

Optimized test suite for 100% code coverage with minimal redundancy.
Focuses on essential functionality and edge cases.

@author: Nicola Guerra
"""

from abc import ABC
from typing import Dict

import pytest

from core.sensors.sensor_node import SensorNode
from core.sensors.types.sensor_reading import SensorReading, SensorType

# -----------------------
# Test Fixtures
# -----------------------


@pytest.fixture
def mock_stub():
    # Mock object for stub, since it's not used in these tests
    return object()


@pytest.fixture
def concrete_sensor(mock_stub):
    """Factory for creating a concrete SensorNode implementation."""

    class ConcreteSensorNode(SensorNode):
        def __init__(
            self, sensor_id: str, sensor_type: SensorType, stub=mock_stub, interval=2.0
        ):
            super().__init__(sensor_id, sensor_type, stub, interval)
            self._read_data_called = False
            self._calibrate_called = False

        def read_data(self) -> SensorReading:
            self._read_data_called = True
            return {"value": 42, "timestamp": "2025-08-19T12:00:00Z"}

        def calibrate(self) -> None:
            self._calibrate_called = True

        def run(self) -> None:
            pass

        def stop(self) -> None:
            pass

    return ConcreteSensorNode


# -----------------------
# Constructor Tests
# -----------------------


@pytest.mark.parametrize(
    "sensor_id, sensor_type",
    [
        ("sensor_001", SensorType.TEMPERATURE),
        ("sensor_empty", SensorType.HUMIDITY),
        ("sensor_unicode_🌡️", SensorType.MOTION_IR),
        ("sensor_" + "x" * 50, SensorType.TEMPERATURE),
    ],
)
def test_constructor_assigns_attributes(concrete_sensor, sensor_id, sensor_type):
    """Test constructor properly assigns sensor_id and sensor_type."""
    sensor = concrete_sensor(sensor_id, sensor_type)

    assert sensor.sensor_id == sensor_id
    assert sensor.sensor_type == sensor_type
    assert isinstance(sensor, SensorNode)
    assert isinstance(sensor, ABC)


# -----------------------
# Abstract Class Tests
# -----------------------


def test_cannot_instantiate_abstract_class():
    """Test that SensorNode cannot be instantiated directly."""
    with pytest.raises(TypeError, match="Can't instantiate abstract class SensorNode"):
        SensorNode("test_id", SensorType.TEMPERATURE)


def test_must_implement_read_data():
    """Test that concrete classes must implement read_data method."""

    class MissingReadDataNode(SensorNode):
        def calibrate(self) -> None:
            pass

        # read_data method is missing

    with pytest.raises(TypeError) as exc_info:
        MissingReadDataNode("test", SensorType.TEMPERATURE)

    assert "read_data" in str(exc_info.value)


def test_must_implement_calibrate():
    """Test that concrete classes must implement calibrate method."""

    class MissingCalibrateNode(SensorNode):
        def read_data(self) -> SensorReading:
            return {"value": 1}

        # calibrate method is missing

    with pytest.raises(TypeError) as exc_info:
        MissingCalibrateNode("test", SensorType.HUMIDITY)

    assert "calibrate" in str(exc_info.value)


def test_must_implement_both_methods():
    """Test that concrete classes must implement both abstract methods."""

    class MissingBothNode(SensorNode):
        pass  # No methods implemented

    with pytest.raises(TypeError) as exc_info:
        MissingBothNode("test", SensorType.MOTION_IR)

    error_message = str(exc_info.value)
    assert "read_data" in error_message or "calibrate" in error_message


def test_abstract_methods_properties():
    """Test that abstract methods are properly configured."""
    assert issubclass(SensorNode, ABC)
    assert len(SensorNode.__abstractmethods__) == 4
    for method in ("read_data", "calibrate", "run", "stop"):
        assert method in SensorNode.__abstractmethods__
    assert getattr(SensorNode.read_data, "__isabstractmethod__", False)
    assert getattr(SensorNode.calibrate, "__isabstractmethod__", False)
    assert not getattr(SensorNode.get_metadata, "__isabstractmethod__", False)


# -----------------------
# get_metadata Method Tests
# -----------------------


@pytest.mark.parametrize(
    "sensor_id, sensor_type",
    [
        ("sensor_01", SensorType.TEMPERATURE),
        ("sensor_02", SensorType.HUMIDITY),
        ("special_unicode", SensorType.MOTION_IR),
    ],
)
def test_get_metadata_returns_correct_dict(concrete_sensor, sensor_id, sensor_type):
    """Test get_metadata returns correct dictionary structure."""
    sensor = concrete_sensor(sensor_id, sensor_type)
    metadata = sensor.get_metadata()

    expected = {"id": sensor_id, "type": sensor_type.value}
    assert metadata == expected
    assert isinstance(metadata, dict)
    assert len(metadata) == 2


def test_get_metadata_independence(concrete_sensor):
    """Test get_metadata returns independent dict instances."""
    sensor = concrete_sensor("test", SensorType.TEMPERATURE)

    metadata1 = sensor.get_metadata()
    metadata2 = sensor.get_metadata()

    assert metadata1 == metadata2
    assert metadata1 is not metadata2

    metadata1["extra"] = "value"
    assert "extra" not in metadata2


def test_get_metadata_reflects_attribute_changes(concrete_sensor):
    """Test get_metadata reflects runtime attribute changes."""
    sensor = concrete_sensor("original", SensorType.HUMIDITY)

    sensor.sensor_id = "modified"
    sensor.sensor_type = SensorType.MOTION_IR

    metadata = sensor.get_metadata()
    assert metadata == {"id": "modified", "type": SensorType.MOTION_IR.value}


# -----------------------
# Abstract Method Coverage Tests
# -----------------------


def test_abstract_method_pass_statements_coverage():
    """Test to achieve 100% coverage of abstract method pass statements."""

    class PassCoverageNode(SensorNode):
        def read_data(self) -> SensorReading:
            try:
                super().read_data()
            except Exception:
                pass
            return {"covered": True}

        def calibrate(self) -> None:
            try:
                super().calibrate()
            except Exception:
                pass

        def run(self) -> None:
            pass

        def stop(self) -> None:
            pass

    sensor = PassCoverageNode("coverage", SensorType.TEMPERATURE, object())
    result = sensor.read_data()
    assert result == {"covered": True}
    sensor.calibrate()


# -----------------------
# Concrete Implementation Tests
# -----------------------


def test_concrete_methods_work(concrete_sensor):
    """Test that concrete implementations function correctly."""
    sensor = concrete_sensor("test", SensorType.HUMIDITY)

    data = sensor.read_data()
    assert isinstance(data, dict)
    assert "value" in data
    assert sensor._read_data_called

    sensor.calibrate()
    assert sensor._calibrate_called


# -----------------------
# Inheritance / Override Tests
# -----------------------


def test_method_override():
    """Test method overriding in inheritance."""

    class CustomSensorNode(SensorNode):
        def read_data(self) -> SensorReading:
            return {"custom": self.sensor_id}

        def calibrate(self) -> None:
            pass

        def run(self) -> None:
            pass

        def stop(self) -> None:
            pass

        def get_metadata(self) -> Dict[str, str]:
            base = super().get_metadata()
            base["custom"] = "true"
            return base

    sensor = CustomSensorNode("custom", SensorType.TEMPERATURE, object())
    assert sensor.read_data() == {"custom": "custom"}
    assert sensor.get_metadata() == {
        "id": "custom",
        "type": SensorType.TEMPERATURE.value,
        "custom": "true",
    }


def test_multiple_inheritance():
    """Test SensorNode with multiple inheritance."""

    class Mixin:
        def extra_method(self):
            return "extra"

    class MultiSensor(SensorNode, Mixin):
        def read_data(self) -> SensorReading:
            return {"multi": True}

        def calibrate(self) -> None:
            pass

        def run(self) -> None:
            pass

        def stop(self) -> None:
            pass

    sensor = MultiSensor("multi", SensorType.MOTION_IR, object())
    assert isinstance(sensor, SensorNode)
    assert isinstance(sensor, Mixin)
    assert sensor.extra_method() == "extra"
    assert sensor.get_metadata() == {"id": "multi", "type": SensorType.MOTION_IR.value}


# -----------------------
# Type Annotations Test
# -----------------------


def test_type_annotations():
    """Test that type annotations are correctly defined."""
    annotations = SensorNode.get_metadata.__annotations__
    assert annotations.get("return") == Dict[str, str]
    assert hasattr(SensorNode.read_data, "__annotations__")
    assert hasattr(SensorNode.calibrate, "__annotations__")
