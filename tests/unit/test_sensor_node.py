"""
Unit tests for the abstract SensorNode class.

Optimized test suite for 100% code coverage with minimal redundancy.
Focuses on essential functionality and edge cases.

@author: Nicola Guerra
"""

from abc import ABC
from typing import Dict

import pytest

from core.sensor_node import SensorNode
from core.types.sensor_reading import SensorType, SensorReading


# -----------------------
# Test Fixtures
# -----------------------


@pytest.fixture
def concrete_sensor():
    """Factory for creating a concrete SensorNode implementation."""
    
    class ConcreteSensorNode(SensorNode):
        def __init__(self, sensor_id: str, sensor_type: SensorType):
            super().__init__(sensor_id, sensor_type)
            self._read_data_called = False
            self._calibrate_called = False
        
        def read_data(self) -> SensorReading:
            self._read_data_called = True
            return {"value": 42, "timestamp": "2025-08-19T12:00:00Z"}
        
        def calibrate(self) -> None:
            self._calibrate_called = True
    
    return ConcreteSensorNode


# -----------------------
# Constructor Tests
# -----------------------


@pytest.mark.parametrize(
    "sensor_id, sensor_type", [
        ("sensor_001", "temperature"),
        ("", ""),  # Empty strings
        ("sensor with spaces", "type with spaces"),
        ("sensor_测试_🌡️", "温度传感器"),  # Unicode
        ("sensor_" + "x" * 100, "type_" + "y" * 100),  # Long strings
    ]
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
        SensorNode("test_id", "test_type")


def test_must_implement_read_data():
    """Test that concrete classes must implement read_data method."""
    
    class MissingReadDataNode(SensorNode):
        def calibrate(self) -> None:
            pass
        # read_data method is missing
    
    with pytest.raises(TypeError) as exc_info:
        MissingReadDataNode("test", "test")
    
    assert "read_data" in str(exc_info.value)


def test_must_implement_calibrate():
    """Test that concrete classes must implement calibrate method."""
    
    class MissingCalibrateNode(SensorNode):
        def read_data(self) -> SensorReading:
            return {"value": 1}
        # calibrate method is missing
    
    with pytest.raises(TypeError) as exc_info:
        MissingCalibrateNode("test", "test")
    
    assert "calibrate" in str(exc_info.value)


def test_must_implement_both_methods():
    """Test that concrete classes must implement both abstract methods."""
    
    class MissingBothNode(SensorNode):
        pass  # No methods implemented
    
    with pytest.raises(TypeError) as exc_info:
        MissingBothNode("test", "test")
    
    error_message = str(exc_info.value)
    # Should mention at least one of the missing methods
    assert "read_data" in error_message or "calibrate" in error_message


def test_abstract_methods_properties():
    """Test that abstract methods are properly configured."""
    assert issubclass(SensorNode, ABC)
    assert len(SensorNode.__abstractmethods__) == 2
    assert "read_data" in SensorNode.__abstractmethods__
    assert "calibrate" in SensorNode.__abstractmethods__
    
    # Check abstract method markers
    assert getattr(SensorNode.read_data, "__isabstractmethod__", False)
    assert getattr(SensorNode.calibrate, "__isabstractmethod__", False)
    assert not getattr(SensorNode.get_metadata, "__isabstractmethod__", False)


# -----------------------
# get_metadata Method Tests
# -----------------------


@pytest.mark.parametrize(
    "sensor_id, sensor_type", [
        ("sensor_01", "temperature"),
        ("", ""),
        ("special_!@#$%", "type_測試_🔥"),
    ]
)
def test_get_metadata_returns_correct_dict(concrete_sensor, sensor_id, sensor_type):
    """Test get_metadata returns correct dictionary structure."""
    sensor = concrete_sensor(sensor_id, sensor_type)
    metadata = sensor.get_metadata()
    
    expected = {"id": sensor_id, "type": sensor_type}
    assert metadata == expected
    assert isinstance(metadata, dict)
    assert len(metadata) == 2


def test_get_metadata_independence(concrete_sensor):
    """Test get_metadata returns independent dict instances."""
    sensor = concrete_sensor("test", "test")
    
    metadata1 = sensor.get_metadata()
    metadata2 = sensor.get_metadata()
    
    # Should be equal but different objects
    assert metadata1 == metadata2
    assert metadata1 is not metadata2
    
    # Modification should not affect other instances
    metadata1["extra"] = "value"
    assert "extra" not in metadata2


def test_get_metadata_reflects_attribute_changes(concrete_sensor):
    """Test get_metadata reflects runtime attribute changes."""
    sensor = concrete_sensor("original", "original")
    
    # Change attributes after construction
    sensor.sensor_id = "modified"
    sensor.sensor_type = "modified"
    
    metadata = sensor.get_metadata()
    assert metadata == {"id": "modified", "type": "modified"}


# -----------------------
# Abstract Method Coverage Tests
# -----------------------


def test_abstract_method_pass_statements_coverage():
    """Test to achieve 100% coverage of abstract method pass statements (lines 28, 35)."""
    
    class PassCoverageNode(SensorNode):
        def read_data(self) -> SensorReading:
            # Execute the abstract method to cover pass statement on line 28
            try:
                super().read_data()
            except Exception:
                pass
            return {"covered": True}
        
        def calibrate(self) -> None:
            # Execute the abstract method to cover pass statement on line 35
            try:
                super().calibrate()
            except Exception:
                pass
    
    sensor = PassCoverageNode("coverage", "test")
    
    # Execute methods to trigger abstract method pass statements
    result = sensor.read_data()
    assert result == {"covered": True}
    
    sensor.calibrate()  # Should not raise exception


# -----------------------
# Concrete Implementation Tests
# -----------------------


def test_concrete_methods_work(concrete_sensor):
    """Test that concrete implementations function correctly."""
    sensor = concrete_sensor("test", "test")
    
    # Test read_data implementation
    data = sensor.read_data()
    assert isinstance(data, dict)
    assert "value" in data
    assert sensor._read_data_called
    
    # Test calibrate implementation
    sensor.calibrate()
    assert sensor._calibrate_called


# -----------------------
# Edge Cases and Type Tests
# -----------------------


@pytest.mark.parametrize(
    "attribute_value", [None, 123, [], {}, True]
)
def test_non_string_attributes(concrete_sensor, attribute_value):
    """Test behavior with non-string attribute values."""
    sensor = concrete_sensor("test", "test")
    
    sensor.sensor_id = attribute_value
    sensor.sensor_type = attribute_value
    
    metadata = sensor.get_metadata()
    assert metadata["id"] == attribute_value
    assert metadata["type"] == attribute_value


def test_inheritance_and_polymorphism(concrete_sensor):
    """Test inheritance chain and polymorphic behavior."""
    sensor = concrete_sensor("poly", "test")
    
    # Test isinstance relationships
    assert isinstance(sensor, SensorNode)
    assert isinstance(sensor, ABC)
    
    # Test polymorphic method access
    assert callable(sensor.get_metadata)
    assert callable(sensor.read_data)
    assert callable(sensor.calibrate)


def test_method_override():
    """Test method overriding in inheritance."""
    
    class CustomSensorNode(SensorNode):
        def read_data(self) -> SensorReading:
            return {"custom": self.sensor_id}
        
        def calibrate(self) -> None:
            pass
        
        def get_metadata(self) -> Dict[str, str]:
            base = super().get_metadata()
            base["custom"] = "true"
            return base
    
    sensor = CustomSensorNode("custom", "type")
    
    # Test overridden methods
    assert sensor.read_data() == {"custom": "custom"}
    assert sensor.get_metadata() == {"id": "custom", "type": "type", "custom": "true"}


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
    
    sensor = MultiSensor("multi", "test")
    
    assert isinstance(sensor, SensorNode)
    assert isinstance(sensor, Mixin)
    assert sensor.extra_method() == "extra"
    assert sensor.get_metadata() == {"id": "multi", "type": "test"}


# -----------------------
# Type Annotations Test
# -----------------------


def test_type_annotations():
    """Test that type annotations are correctly defined."""
    # Check get_metadata return type annotation
    annotations = SensorNode.get_metadata.__annotations__
    assert annotations.get("return") == Dict[str, str]
    
    # Check that annotations exist for abstract methods
    assert hasattr(SensorNode.read_data, "__annotations__")
    assert hasattr(SensorNode.calibrate, "__annotations__")