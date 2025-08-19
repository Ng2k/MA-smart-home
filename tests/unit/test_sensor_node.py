"""
Unit tests for the abstract SensorNode class.

This module provides comprehensive test coverage for the SensorNode abstract class,
including constructor behavior, abstract method enforcement, metadata functionality,
and edge cases.

Best practices applied:
- Fixture factory for creating concrete instances
- Parametrized tests for multiple cases
- Full coverage of methods and edge cases
- Abstract class enforcement testing
- Clear test function names describing what is being tested
- No pytest collection warnings

@author: Nicola Guerra
"""

from abc import ABC, abstractmethod
from typing import Any, Dict

import pytest

from core.sensor_node import SensorNode

# -----------------------
# Fixture factory
# -----------------------


@pytest.fixture
def concrete_sensor_factory():
    """
    Fixture returning a factory function for creating concrete SensorNode instances.
    The concrete class is local to avoid pytest collection warnings.
    """

    class ConcreteSensorNode(SensorNode):
        """Concrete implementation for testing purposes."""

        def __init__(
            self,
            sensor_id: str,
            sensor_type: str,
            read_data_return=None,
            calibrate_return=None,
        ):
            super().__init__(sensor_id, sensor_type)
            self._read_data_return = read_data_return or {
                "value": 42,
                "timestamp": "2025-08-19T12:00:00Z",
            }
            self._calibrate_return = calibrate_return

        def read_data(self) -> Dict[str, Any]:
            """Test implementation of read_data."""
            return self._read_data_return

        def calibrate(self) -> None:
            """Test implementation of calibrate."""
            return self._calibrate_return

    def _factory(sensor_id: str, sensor_type: str, **kwargs):
        return ConcreteSensorNode(sensor_id, sensor_type, **kwargs)

    return _factory


@pytest.fixture
def partial_implementation_factory():
    """
    Fixture for creating classes that only implement one abstract method.
    Used to test abstract method enforcement.
    """

    def _factory(implement_read_data=True, implement_calibrate=True):
        class PartialSensorNode(SensorNode):
            """Partially implemented class for testing abstract enforcement."""

            if implement_read_data:

                def read_data(self) -> Dict[str, Any]:
                    return {"value": 1}

            if implement_calibrate:

                def calibrate(self) -> None:
                    pass

        return PartialSensorNode

    return _factory


# -----------------------
# Constructor tests
# -----------------------


@pytest.mark.parametrize(
    "sensor_id, sensor_type",
    [
        ("sensor_001", "temperature"),
        ("hum_sensor_01", "humidity"),
        ("motion_detector", "motion_ir"),
        ("pos_tracker", "position"),
        ("", ""),  # Edge case: empty strings
        ("sensor with spaces", "type with spaces"),  # Spaces in parameters
        ("sensor-with-dashes", "type-with-dashes"),  # Dashes in parameters
    ],
)
def test_constructor_valid_parameters(concrete_sensor_factory, sensor_id, sensor_type):
    """Test constructor with various valid parameter combinations."""
    sensor = concrete_sensor_factory(sensor_id, sensor_type)

    assert sensor.sensor_id == sensor_id
    assert sensor.sensor_type == sensor_type
    assert isinstance(sensor, SensorNode)


def test_constructor_attribute_assignment(concrete_sensor_factory):
    """Test that constructor properly assigns attributes."""
    sensor_id = "test_sensor_123"
    sensor_type = "test_type"

    sensor = concrete_sensor_factory(sensor_id, sensor_type)

    # Verify attributes are assigned correctly
    assert hasattr(sensor, "sensor_id")
    assert hasattr(sensor, "sensor_type")
    assert sensor.sensor_id == sensor_id
    assert sensor.sensor_type == sensor_type


def test_constructor_with_unicode_characters(concrete_sensor_factory):
    """Test constructor with unicode characters in parameters."""
    sensor_id = "sensor_测试_🌡️"
    sensor_type = "温度传感器"

    sensor = concrete_sensor_factory(sensor_id, sensor_type)

    assert sensor.sensor_id == sensor_id
    assert sensor.sensor_type == sensor_type


def test_constructor_with_very_long_strings(concrete_sensor_factory):
    """Test constructor with very long string parameters."""
    long_sensor_id = "sensor_" + "a" * 1000
    long_sensor_type = "type_" + "b" * 1000

    sensor = concrete_sensor_factory(long_sensor_id, long_sensor_type)

    assert sensor.sensor_id == long_sensor_id
    assert sensor.sensor_type == long_sensor_type
    assert len(sensor.sensor_id) == 1007
    assert len(sensor.sensor_type) == 1005


# -----------------------
# Abstract class behavior tests
# -----------------------


def test_cannot_instantiate_abstract_class():
    """Test that SensorNode cannot be instantiated directly."""
    with pytest.raises(TypeError) as exc_info:
        SensorNode("test_id", "test_type")

    error_message = str(exc_info.value)
    assert "Can't instantiate abstract class SensorNode" in error_message
    assert "abstract method" in error_message


def test_must_implement_all_abstract_methods(partial_implementation_factory):
    """Test that all abstract methods must be implemented."""
    # Test class missing read_data method
    PartialClass1 = partial_implementation_factory(
        implement_read_data=False, implement_calibrate=True
    )
    with pytest.raises(TypeError) as exc_info:
        PartialClass1("test", "test")
    assert "read_data" in str(exc_info.value)

    # Test class missing calibrate method
    PartialClass2 = partial_implementation_factory(
        implement_read_data=True, implement_calibrate=False
    )
    with pytest.raises(TypeError) as exc_info:
        PartialClass2("test", "test")
    assert "calibrate" in str(exc_info.value)

    # Test class missing both methods
    PartialClass3 = partial_implementation_factory(
        implement_read_data=False, implement_calibrate=False
    )
    with pytest.raises(TypeError) as exc_info:
        PartialClass3("test", "test")
    error_message = str(exc_info.value)
    assert "read_data" in error_message or "calibrate" in error_message


def test_is_abstract_base_class():
    """Test that SensorNode is properly configured as an abstract base class."""
    assert issubclass(SensorNode, ABC)
    assert hasattr(SensorNode, "__abstractmethods__")
    assert len(SensorNode.__abstractmethods__) == 2
    assert "read_data" in SensorNode.__abstractmethods__
    assert "calibrate" in SensorNode.__abstractmethods__


# -----------------------
# get_metadata method tests
# -----------------------


@pytest.mark.parametrize(
    "sensor_id, sensor_type, expected",
    [
        ("sensor_01", "temperature", {"id": "sensor_01", "type": "temperature"}),
        ("sensor_02", "humidity", {"id": "sensor_02", "type": "humidity"}),
        ("motion_01", "motion_ir", {"id": "motion_01", "type": "motion_ir"}),
        ("pos_01", "position", {"id": "pos_01", "type": "position"}),
        ("", "", {"id": "", "type": ""}),  # Edge case: empty strings
        (
            "sensor with spaces",
            "type with spaces",
            {"id": "sensor with spaces", "type": "type with spaces"},
        ),
        (
            "sensor-123_test",
            "type-456_test",
            {"id": "sensor-123_test", "type": "type-456_test"},
        ),
    ],
)
def test_get_metadata_returns_correct_dict(
    concrete_sensor_factory, sensor_id, sensor_type, expected
):
    """Test that get_metadata returns correct dictionary for various inputs."""
    sensor = concrete_sensor_factory(sensor_id, sensor_type)
    metadata = sensor.get_metadata()

    assert metadata == expected
    assert isinstance(metadata, dict)
    assert len(metadata) == 2
    assert "id" in metadata
    assert "type" in metadata


def test_get_metadata_return_type(concrete_sensor_factory):
    """Test that get_metadata returns Dict[str, str] as specified in type annotation."""
    sensor = concrete_sensor_factory("test_sensor", "test_type")
    metadata = sensor.get_metadata()

    # Verify return type
    assert isinstance(metadata, dict)

    # Verify all keys and values are strings
    for key, value in metadata.items():
        assert isinstance(key, str)
        assert isinstance(value, str)


def test_get_metadata_immutability(concrete_sensor_factory):
    """Test that get_metadata returns a new dict each time (not a reference)."""
    sensor = concrete_sensor_factory("test_sensor", "test_type")

    metadata1 = sensor.get_metadata()
    metadata2 = sensor.get_metadata()

    # Should be equal but not the same object
    assert metadata1 == metadata2
    assert metadata1 is not metadata2

    # Modifying one should not affect the other
    metadata1["new_key"] = "new_value"
    assert "new_key" not in metadata2


def test_get_metadata_with_special_characters(concrete_sensor_factory):
    """Test get_metadata with special characters and unicode."""
    sensor_id = "sensor_!@#$%^&*()_+=[]{}|;':\",./<>?"
    sensor_type = "type_測試_🔥"

    sensor = concrete_sensor_factory(sensor_id, sensor_type)
    metadata = sensor.get_metadata()

    assert metadata["id"] == sensor_id
    assert metadata["type"] == sensor_type


# -----------------------
# Abstract method implementation tests
# -----------------------


def test_concrete_implementation_read_data(concrete_sensor_factory):
    """Test that concrete implementation of read_data works correctly."""
    custom_data = {"value": 25.5, "timestamp": "2023-10-15T14:30:00Z", "unit": "°C"}
    sensor = concrete_sensor_factory(
        "temp_01", "temperature", read_data_return=custom_data
    )

    result = sensor.read_data()
    assert result == custom_data
    assert isinstance(result, dict)


def test_concrete_implementation_calibrate(concrete_sensor_factory):
    """Test that concrete implementation of calibrate works correctly."""
    calibrate_result = "calibration_complete"
    sensor = concrete_sensor_factory(
        "sensor_01", "test", calibrate_return=calibrate_result
    )

    result = sensor.calibrate()
    assert result == calibrate_result


def test_read_data_return_type_annotation(concrete_sensor_factory):
    """Test that read_data returns Dict[str, Any] as per type annotation."""
    sensor = concrete_sensor_factory("test_sensor", "test_type")
    result = sensor.read_data()

    assert isinstance(result, dict)
    # Verify it can contain various types (Any)
    assert "value" in result
    assert "timestamp" in result


# -----------------------
# Inheritance behavior tests
# -----------------------


def test_inheritance_chain(concrete_sensor_factory):
    """Test that concrete implementations maintain proper inheritance."""
    sensor = concrete_sensor_factory("test_sensor", "test_type")

    assert isinstance(sensor, SensorNode)
    assert isinstance(sensor, ABC)
    assert hasattr(sensor, "sensor_id")
    assert hasattr(sensor, "sensor_type")
    assert hasattr(sensor, "get_metadata")
    assert hasattr(sensor, "read_data")
    assert hasattr(sensor, "calibrate")


def test_method_resolution_order(concrete_sensor_factory):
    """Test that method resolution order is correct."""
    sensor = concrete_sensor_factory("test_sensor", "test_type")

    # get_metadata should be inherited from SensorNode
    assert sensor.get_metadata.__qualname__.startswith("SensorNode.get_metadata")

    # read_data and calibrate should be from the concrete class
    assert "ConcreteSensorNode" in sensor.read_data.__qualname__
    assert "ConcreteSensorNode" in sensor.calibrate.__qualname__


# -----------------------
# Edge cases and boundary tests
# -----------------------


def test_sensor_attributes_are_modifiable(concrete_sensor_factory):
    """Test that sensor attributes can be modified after construction."""
    sensor = concrete_sensor_factory("initial_id", "initial_type")

    # Modify attributes
    sensor.sensor_id = "modified_id"
    sensor.sensor_type = "modified_type"

    # Verify changes are reflected in get_metadata
    metadata = sensor.get_metadata()
    assert metadata["id"] == "modified_id"
    assert metadata["type"] == "modified_type"


def test_numeric_string_parameters(concrete_sensor_factory):
    """Test constructor with numeric strings."""
    sensor = concrete_sensor_factory("12345", "67890")

    assert sensor.sensor_id == "12345"
    assert sensor.sensor_type == "67890"
    assert isinstance(sensor.sensor_id, str)
    assert isinstance(sensor.sensor_type, str)


def test_newline_and_tab_characters(concrete_sensor_factory):
    """Test constructor with newline and tab characters."""
    sensor_id = "sensor\nwith\nnewlines"
    sensor_type = "type\twith\ttabs"

    sensor = concrete_sensor_factory(sensor_id, sensor_type)
    metadata = sensor.get_metadata()

    assert metadata["id"] == sensor_id
    assert metadata["type"] == sensor_type


def test_multiple_inheritance_scenario():
    """Test SensorNode in multiple inheritance scenarios."""

    class Mixin:
        def mixin_method(self):
            return "mixin"

    class MultipleMixin(SensorNode, Mixin):
        def read_data(self):
            return {"mixed": True}

        def calibrate(self):
            return "mixed_calibrated"

    sensor = MultipleMixin("multi_sensor", "multi_type")

    assert isinstance(sensor, SensorNode)
    assert isinstance(sensor, Mixin)
    assert sensor.mixin_method() == "mixin"
    assert sensor.get_metadata() == {"id": "multi_sensor", "type": "multi_type"}


# -----------------------
# Performance and stress tests
# -----------------------


def test_many_instances_creation(concrete_sensor_factory):
    """Test creating many instances to verify no memory leaks or issues."""
    sensors = []

    for i in range(100):
        sensor = concrete_sensor_factory(f"sensor_{i}", f"type_{i}")
        sensors.append(sensor)

    # Verify all instances are properly created
    assert len(sensors) == 100
    for i, sensor in enumerate(sensors):
        assert sensor.sensor_id == f"sensor_{i}"
        assert sensor.sensor_type == f"type_{i}"


def test_metadata_consistency_across_calls(concrete_sensor_factory):
    """Test that get_metadata returns consistent results across multiple calls."""
    sensor = concrete_sensor_factory("consistent_sensor", "consistent_type")

    # Call get_metadata multiple times
    results = [sensor.get_metadata() for _ in range(10)]

    # All results should be identical
    first_result = results[0]
    for result in results[1:]:
        assert result == first_result


# -----------------------
# Type checking and validation tests
# -----------------------


def test_abstract_methods_signature():
    """Test that abstract methods have correct signatures."""
    # Check read_data signature
    read_data_annotations = SensorNode.read_data.__annotations__
    assert read_data_annotations.get("return") == Dict[str, Any]

    # Check calibrate signature
    calibrate_annotations = SensorNode.calibrate.__annotations__
    assert calibrate_annotations.get("return") is None or calibrate_annotations.get(
        "return"
    ) == type(None)


def test_get_metadata_signature():
    """Test that get_metadata has correct type signature."""
    annotations = SensorNode.get_metadata.__annotations__
    assert annotations.get("return") == Dict[str, str]


def test_constructor_parameter_handling(concrete_sensor_factory):
    """Test constructor handles different parameter scenarios."""
    # Test with keyword arguments
    sensor1 = concrete_sensor_factory(sensor_id="kwarg_id", sensor_type="kwarg_type")
    assert sensor1.sensor_id == "kwarg_id"
    assert sensor1.sensor_type == "kwarg_type"

    # Test with positional arguments
    sensor2 = concrete_sensor_factory("pos_id", "pos_type")
    assert sensor2.sensor_id == "pos_id"
    assert sensor2.sensor_type == "pos_type"


# -----------------------
# Abstract method pass statement coverage
# -----------------------


def test_abstract_method_pass_statements():
    """Test to achieve 100% coverage by calling abstract methods via super()."""

    class CoverageTestNode(SensorNode):
        """Test class that calls abstract methods via super() to cover pass statements."""

        def read_data(self) -> Dict[str, Any]:
            # Call the abstract method to cover the pass statement
            try:
                super().read_data()
            except Exception:
                pass
            return {"test": "data"}

        def calibrate(self) -> None:
            # Call the abstract method to cover the pass statement
            try:
                super().calibrate()
            except Exception:
                pass
            return None

    # Create instance and call methods to trigger coverage
    sensor = CoverageTestNode("coverage_test", "test_type")

    # These calls will execute the abstract methods and cover the pass statements
    result = sensor.read_data()
    assert result == {"test": "data"}

    calibrate_result = sensor.calibrate()
    assert calibrate_result is None


def test_direct_abstract_method_access():
    """Test direct access to abstract methods for complete coverage."""

    # Create a concrete implementation
    class DirectTestNode(SensorNode):
        def read_data(self) -> Dict[str, Any]:
            return {"direct": True}

        def calibrate(self) -> None:
            return None

    sensor = DirectTestNode("direct_test", "test_type")

    # Access the abstract methods directly from the class
    # This ensures the abstract method definitions are covered
    assert hasattr(SensorNode, "read_data")
    assert hasattr(SensorNode, "calibrate")

    # Verify the methods exist and are callable
    assert callable(SensorNode.read_data)
    assert callable(SensorNode.calibrate)

    # Call the implemented versions
    assert sensor.read_data() == {"direct": True}
    assert sensor.calibrate() is None


# -----------------------
# Final edge case tests for completeness
# -----------------------


def test_sensor_node_with_none_attributes():
    """Test handling when attributes are set to None after construction."""

    class NullTestNode(SensorNode):
        def read_data(self) -> Dict[str, Any]:
            return {"null_test": True}

        def calibrate(self) -> None:
            pass

    sensor = NullTestNode("test", "test")

    # Set attributes to None and test get_metadata
    sensor.sensor_id = None
    sensor.sensor_type = None

    metadata = sensor.get_metadata()
    assert metadata["id"] is None
    assert metadata["type"] is None


def test_class_attributes_and_methods():
    """Test class-level attributes and method existence."""
    # Test that SensorNode has the expected class structure
    assert hasattr(SensorNode, "__init__")
    assert hasattr(SensorNode, "read_data")
    assert hasattr(SensorNode, "calibrate")
    assert hasattr(SensorNode, "get_metadata")

    # Test abstract method properties
    assert getattr(SensorNode.read_data, "__isabstractmethod__", False)
    assert getattr(SensorNode.calibrate, "__isabstractmethod__", False)
    assert not getattr(SensorNode.get_metadata, "__isabstractmethod__", False)


def test_docstring_presence():
    """Test that all methods have proper docstrings."""
    assert SensorNode.__doc__ is not None
    assert "Abstract class" in SensorNode.__doc__

    assert SensorNode.read_data.__doc__ is not None
    assert "Reads data" in SensorNode.read_data.__doc__

    assert SensorNode.calibrate.__doc__ is not None
    assert "calibration" in SensorNode.calibrate.__doc__

    assert SensorNode.get_metadata.__doc__ is not None
    assert "metadata" in SensorNode.get_metadata.__doc__


@pytest.mark.parametrize(
    "attribute_value", [None, 0, 1, -1, 3.14, [], {}, set(), True, False]
)
def test_non_string_attribute_assignment(concrete_sensor_factory, attribute_value):
    """Test behavior when non-string values are assigned to string attributes."""
    sensor = concrete_sensor_factory("test", "test")

    # Assign non-string value
    sensor.sensor_id = attribute_value
    sensor.sensor_type = attribute_value

    # get_metadata should still work (Python is dynamically typed)
    metadata = sensor.get_metadata()
    assert metadata["id"] == attribute_value
    assert metadata["type"] == attribute_value


def test_subclass_method_override_behavior(concrete_sensor_factory):
    """Test that subclasses can properly override methods."""

    class CustomSensorNode(SensorNode):
        def read_data(self) -> Dict[str, Any]:
            return {"custom": "data", "id": self.sensor_id}

        def calibrate(self) -> None:
            return f"calibrated_{self.sensor_type}"

        def get_metadata(self) -> Dict[str, str]:
            # Override get_metadata with custom behavior
            base_metadata = super().get_metadata()
            base_metadata["custom"] = "override"
            return base_metadata

    sensor = CustomSensorNode("custom_id", "custom_type")

    # Test overridden read_data
    data = sensor.read_data()
    assert data == {"custom": "data", "id": "custom_id"}

    # Test overridden calibrate
    result = sensor.calibrate()
    assert result == "calibrated_custom_type"

    # Test overridden get_metadata
    metadata = sensor.get_metadata()
    assert metadata == {"id": "custom_id", "type": "custom_type", "custom": "override"}


def test_complex_inheritance_with_abstract_intermediate():
    """Test complex inheritance scenarios with intermediate abstract classes."""

    class IntermediateNode(SensorNode):
        """Intermediate abstract class that adds more functionality."""

        def __init__(self, sensor_id: str, sensor_type: str, location: str):
            super().__init__(sensor_id, sensor_type)
            self.location = location

        @abstractmethod
        def get_location_data(self) -> Dict[str, Any]:
            """Abstract method in intermediate class."""
            pass

        def get_full_metadata(self) -> Dict[str, str]:
            """Concrete method in intermediate class."""
            metadata = self.get_metadata()
            metadata["location"] = self.location
            return metadata

    # This should fail - intermediate class has abstract methods
    with pytest.raises(TypeError):
        IntermediateNode("test", "test", "test_location")

    # Concrete implementation
    class ConcreteIntermediateNode(IntermediateNode):
        def read_data(self) -> Dict[str, Any]:
            return {"value": 1, "location": self.location}

        def calibrate(self) -> None:
            pass

        def get_location_data(self) -> Dict[str, Any]:
            return {"location": self.location, "coordinates": [0, 0]}

    # This should work
    sensor = ConcreteIntermediateNode("complex", "temperature", "room_1")
    assert sensor.sensor_id == "complex"
    assert sensor.sensor_type == "temperature"
    assert sensor.location == "room_1"

    metadata = sensor.get_full_metadata()
    assert metadata == {"id": "complex", "type": "temperature", "location": "room_1"}

    location_data = sensor.get_location_data()
    assert location_data == {"location": "room_1", "coordinates": [0, 0]}
