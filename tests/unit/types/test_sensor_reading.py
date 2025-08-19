"""
Unit tests for the SensorReading pydantic model.

This module provides comprehensive test coverage for the SensorReading class,
including field validation, custom validators, edge cases, and Pydantic model features.

Best practices applied:
- Parametrized tests for multiple cases
- Clear test function names describing what is being tested
- Comprehensive edge case coverage
- Testing both valid and invalid scenarios
- Full coverage of custom validators
- Testing Pydantic model serialization/deserialization

@author: Nicola Guerra
"""

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from core.types.sensor_reading import SensorReading

# -----------------------
# Valid instantiation tests
# -----------------------


def test_valid_sensor_reading_creation():
    """Test creating a valid SensorReading with all required fields."""
    reading = SensorReading(
        sensor_id="temp_001", sensor_type="temperature", value=25.5, unit="°C"
    )

    assert reading.sensor_id == "temp_001"
    assert reading.sensor_type == "temperature"
    assert reading.value == 25.5
    assert reading.unit == "°C"
    assert isinstance(reading.timestamp, datetime)
    assert reading.timestamp.tzinfo == timezone.utc


def test_sensor_reading_with_explicit_timestamp():
    """Test creating SensorReading with explicit timestamp."""
    custom_time = datetime(2023, 10, 15, 14, 30, 0, tzinfo=timezone.utc)
    reading = SensorReading(
        sensor_id="hum_001",
        sensor_type="humidity",
        value=65.0,
        unit="%",
        timestamp=custom_time,
    )

    assert reading.timestamp == custom_time


def test_timestamp_auto_generation():
    """Test that timestamp is automatically generated when not provided."""
    before_creation = datetime.now(timezone.utc)
    reading = SensorReading(
        sensor_id="motion_001", sensor_type="motion_ir", value=1.0, unit="boolean"
    )
    after_creation = datetime.now(timezone.utc)

    assert before_creation <= reading.timestamp <= after_creation
    assert reading.timestamp.tzinfo == timezone.utc


@pytest.mark.parametrize(
    "sensor_type, unit, value",
    [
        ("temperature", "°C", 25.5),
        ("humidity", "%", 60.0),
        ("motion_ir", "boolean", 1.0),
        ("motion_ir", "lux", 100.0),
        ("position", "integer", 42.0),
        ("position", "float", 3.14159),
    ],
)
def test_valid_sensor_type_unit_combinations(sensor_type, unit, value):
    """Test valid combinations of sensor types and units."""
    reading = SensorReading(
        sensor_id="test_001", sensor_type=sensor_type, value=value, unit=unit
    )

    assert reading.sensor_type == sensor_type
    assert reading.unit == unit
    assert reading.value == value


# -----------------------
# Field validation tests
# -----------------------


def test_empty_sensor_id_validation():
    """Test that empty sensor_id raises ValidationError due to min_length constraint."""
    with pytest.raises(ValidationError) as exc_info:
        SensorReading(sensor_id="", sensor_type="temperature", value=25.0, unit="°C")

    assert "String should have at least 1 character" in str(exc_info.value)


@pytest.mark.parametrize(
    "invalid_sensor_type",
    ["invalid_type", "temp", "TEMPERATURE", "Temperature", "", None],
)
def test_invalid_sensor_type_validation(invalid_sensor_type):
    """Test that invalid sensor types raise ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        SensorReading(
            sensor_id="test_001", sensor_type=invalid_sensor_type, value=25.0, unit="°C"
        )

    error_msg = str(exc_info.value)
    assert "Input should be" in error_msg or "none is not an allowed value" in error_msg


@pytest.mark.parametrize(
    "invalid_unit", ["celsius", "percent", "C", "degrees", "", None]
)
def test_invalid_unit_validation(invalid_unit):
    """Test that invalid units raise ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        SensorReading(
            sensor_id="test_001",
            sensor_type="temperature",
            value=25.0,
            unit=invalid_unit,
        )

    error_msg = str(exc_info.value)
    assert "Input should be" in error_msg or "none is not an allowed value" in error_msg


# -----------------------
# Custom value validator tests
# -----------------------


def test_value_cannot_be_none():
    """Test that None value raises ValidationError from type validation."""
    with pytest.raises(ValidationError) as exc_info:
        SensorReading(
            sensor_id="test_001", sensor_type="temperature", value=None, unit="°C"
        )

    assert "Input should be a valid number" in str(exc_info.value)


def test_value_cannot_be_string():
    """Test that non-numeric string value raises ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        SensorReading(
            sensor_id="test_001", sensor_type="temperature", value="invalid", unit="°C"
        )

    assert "Input should be a valid number" in str(exc_info.value)


def test_custom_validator_with_string():
    """Test custom validator string check using model_validate."""
    data = {
        "sensor_id": "test_001",
        "sensor_type": "temperature",
        "value": "25.0",  # This will be a string in the validator
        "unit": "°C",
    }

    # Using model_validate with a dict that bypasses initial type coercion
    # We'll create a mock scenario where string reaches the validator
    from core.types.sensor_reading import SensorReading

    # Test that numeric strings are coerced properly
    reading = SensorReading.model_validate(data)
    assert reading.value == 25.0
    assert isinstance(reading.value, float)


def test_value_cannot_be_nan():
    """Test that NaN value raises ValueError from custom validator."""
    with pytest.raises(ValidationError) as exc_info:
        SensorReading(
            sensor_id="test_001",
            sensor_type="temperature",
            value=float("nan"),
            unit="°C",
        )

    assert "The value cannot be NaN" in str(exc_info.value)


@pytest.mark.parametrize(
    "valid_value",
    [
        0.0,
        1.0,
        -1.0,
        25.5,
        -40.0,
        100.0,
        0.001,
        1000000.0,
        -1000000.0,
        float("inf"),
        float("-inf"),
        42,  # int should be coerced to float
    ],
)
def test_valid_numeric_values(valid_value):
    """Test that various valid numeric values pass validation."""
    reading = SensorReading(
        sensor_id="test_001", sensor_type="temperature", value=valid_value, unit="°C"
    )

    assert reading.value == float(valid_value)
    assert isinstance(reading.value, float)


# -----------------------
# Edge cases and type coercion tests
# -----------------------


def test_integer_value_coerced_to_float():
    """Test that integer values are coerced to float."""
    reading = SensorReading(
        sensor_id="test_001",
        sensor_type="motion_ir",
        value=1,  # integer
        unit="boolean",
    )

    assert reading.value == 1.0
    assert isinstance(reading.value, float)


def test_whitespace_in_sensor_id():
    """Test that sensor_id with whitespace is preserved."""
    reading = SensorReading(
        sensor_id=" sensor 001 ", sensor_type="temperature", value=25.0, unit="°C"
    )

    assert reading.sensor_id == " sensor 001 "


def test_extreme_timestamp_values():
    """Test SensorReading with extreme timestamp values."""
    # Far future
    future_time = datetime(2099, 12, 31, 23, 59, 59, tzinfo=timezone.utc)
    reading_future = SensorReading(
        sensor_id="future_001",
        sensor_type="temperature",
        value=25.0,
        unit="°C",
        timestamp=future_time,
    )
    assert reading_future.timestamp == future_time

    # Far past
    past_time = datetime(1900, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    reading_past = SensorReading(
        sensor_id="past_001",
        sensor_type="temperature",
        value=25.0,
        unit="°C",
        timestamp=past_time,
    )
    assert reading_past.timestamp == past_time


# -----------------------
# Pydantic model feature tests
# -----------------------


def test_model_serialization_to_dict():
    """Test serializing SensorReading model to dictionary."""
    reading = SensorReading(
        sensor_id="test_001", sensor_type="temperature", value=25.5, unit="°C"
    )

    data = reading.model_dump()

    assert isinstance(data, dict)
    assert data["sensor_id"] == "test_001"
    assert data["sensor_type"] == "temperature"
    assert data["value"] == 25.5
    assert data["unit"] == "°C"
    assert isinstance(data["timestamp"], datetime)


def test_model_serialization_to_json():
    """Test serializing SensorReading model to JSON-compatible format."""
    reading = SensorReading(
        sensor_id="test_001", sensor_type="humidity", value=65.0, unit="%"
    )

    json_data = reading.model_dump(mode="json")

    assert isinstance(json_data, dict)
    assert json_data["sensor_id"] == "test_001"
    assert json_data["sensor_type"] == "humidity"
    assert json_data["value"] == 65.0
    assert json_data["unit"] == "%"
    assert isinstance(
        json_data["timestamp"], str
    )  # datetime becomes string in JSON mode


def test_model_deserialization_from_dict():
    """Test creating SensorReading from dictionary data."""
    timestamp = datetime.now(timezone.utc)
    data = {
        "sensor_id": "test_001",
        "sensor_type": "motion_ir",
        "value": 0.0,
        "unit": "boolean",
        "timestamp": timestamp,
    }

    reading = SensorReading.model_validate(data)

    assert reading.sensor_id == "test_001"
    assert reading.sensor_type == "motion_ir"
    assert reading.value == 0.0
    assert reading.unit == "boolean"
    assert reading.timestamp == timestamp


def test_model_fields_info():
    """Test that model provides correct field information."""
    fields = SensorReading.model_fields

    assert "sensor_id" in fields
    assert "sensor_type" in fields
    assert "value" in fields
    assert "unit" in fields
    assert "timestamp" in fields

    # Check field metadata
    sensor_id_field = fields["sensor_id"]
    assert sensor_id_field.annotation == str


# -----------------------
# Complete workflow tests
# -----------------------


def test_complete_sensor_reading_workflow():
    """Test a complete workflow: create, serialize, deserialize, and verify."""
    # Create original reading
    original = SensorReading(
        sensor_id="workflow_test_001", sensor_type="position", value=42.5, unit="float"
    )

    # Serialize to dict
    data = original.model_dump()

    # Deserialize back to model
    restored = SensorReading.model_validate(data)

    # Verify all fields match
    assert restored.sensor_id == original.sensor_id
    assert restored.sensor_type == original.sensor_type
    assert restored.value == original.value
    assert restored.unit == original.unit
    assert restored.timestamp == original.timestamp


def test_model_equality():
    """Test that two identical SensorReading instances are equal."""
    timestamp = datetime(2023, 10, 15, 12, 0, 0, tzinfo=timezone.utc)

    reading1 = SensorReading(
        sensor_id="equal_test",
        sensor_type="temperature",
        value=25.0,
        unit="°C",
        timestamp=timestamp,
    )

    reading2 = SensorReading(
        sensor_id="equal_test",
        sensor_type="temperature",
        value=25.0,
        unit="°C",
        timestamp=timestamp,
    )

    assert reading1 == reading2


def test_model_inequality():
    """Test that different SensorReading instances are not equal."""
    timestamp = datetime(2023, 10, 15, 12, 0, 0, tzinfo=timezone.utc)

    reading1 = SensorReading(
        sensor_id="diff_test",
        sensor_type="temperature",
        value=25.0,
        unit="°C",
        timestamp=timestamp,
    )

    reading2 = SensorReading(
        sensor_id="diff_test",
        sensor_type="temperature",
        value=26.0,  # Different value
        unit="°C",
        timestamp=timestamp,
    )

    assert reading1 != reading2


# -----------------------
# Boundary condition tests
# -----------------------


def test_very_long_sensor_id():
    """Test SensorReading with very long sensor_id."""
    long_id = "a" * 1000
    reading = SensorReading(
        sensor_id=long_id, sensor_type="temperature", value=25.0, unit="°C"
    )

    assert reading.sensor_id == long_id
    assert len(reading.sensor_id) == 1000


def test_unicode_sensor_id():
    """Test SensorReading with unicode characters in sensor_id."""
    unicode_id = "sensor_测试_001_🌡️"
    reading = SensorReading(
        sensor_id=unicode_id, sensor_type="temperature", value=25.0, unit="°C"
    )

    assert reading.sensor_id == unicode_id


@pytest.mark.parametrize(
    "extreme_value",
    [
        1e-10,  # Very small positive
        -1e-10,  # Very small negative
        1e10,  # Very large positive
        -1e10,  # Very large negative
        1.7976931348623157e308,  # Close to float max
        -1.7976931348623157e308,  # Close to float min
    ],
)
def test_extreme_numeric_values(extreme_value):
    """Test SensorReading with extreme but valid numeric values."""
    reading = SensorReading(
        sensor_id="extreme_test",
        sensor_type="position",
        value=extreme_value,
        unit="float",
    )

    assert reading.value == extreme_value


# -----------------------
# Direct validator testing
# -----------------------


def test_check_value_validator_directly():
    """Test the check_value validator function directly to ensure 100% coverage."""
    from core.types.sensor_reading import SensorReading

    # Direct access to the validator method
    validator_func = SensorReading.check_value

    # Test None case
    with pytest.raises(ValueError, match="The value cannot be None"):
        validator_func(None)

    # Test string case
    with pytest.raises(ValueError, match="The value cannot be a string"):
        validator_func("test_string")

    # Test NaN case
    with pytest.raises(ValueError, match="The value cannot be NaN"):
        validator_func(float("nan"))

    # Test valid value
    assert validator_func(25.0) == 25.0
    assert validator_func(42) == 42


# -----------------------
# Additional edge case tests
# -----------------------


def test_sensor_reading_with_different_timezone():
    """Test SensorReading with different timezone timestamps."""
    from datetime import timedelta

    # Test with different timezone offset
    custom_tz = timezone(timedelta(hours=5))
    timestamp_with_tz = datetime(2023, 10, 15, 14, 30, 0, tzinfo=custom_tz)

    reading = SensorReading(
        sensor_id="tz_test",
        sensor_type="temperature",
        value=22.5,
        unit="°C",
        timestamp=timestamp_with_tz,
    )

    assert reading.timestamp == timestamp_with_tz
    assert reading.timestamp.tzinfo == custom_tz


def test_sensor_reading_repr():
    """Test string representation of SensorReading."""
    reading = SensorReading(
        sensor_id="repr_test", sensor_type="humidity", value=45.5, unit="%"
    )

    repr_str = repr(reading)
    assert "SensorReading" in repr_str
    assert "sensor_id='repr_test'" in repr_str
    assert "sensor_type='humidity'" in repr_str
    assert "value=45.5" in repr_str
    assert "unit='%'" in repr_str


def test_all_sensor_types_coverage():
    """Test all possible sensor types are valid."""
    sensor_types = ["temperature", "humidity", "motion_ir", "position"]

    for sensor_type in sensor_types:
        reading = SensorReading(
            sensor_id=f"test_{sensor_type}",
            sensor_type=sensor_type,
            value=1.0,
            unit="float",
        )
        assert reading.sensor_type == sensor_type


def test_all_units_coverage():
    """Test all possible units are valid."""
    units = ["°C", "%", "lux", "boolean", "integer", "float"]

    for unit in units:
        reading = SensorReading(
            sensor_id=f"test_unit", sensor_type="position", value=1.0, unit=unit
        )
        assert reading.unit == unit


def test_model_copy():
    """Test creating a copy of SensorReading with modifications."""
    original = SensorReading(
        sensor_id="original", sensor_type="temperature", value=25.0, unit="°C"
    )

    # Create a copy with modified value
    copied = original.model_copy(update={"value": 30.0})

    assert copied.sensor_id == original.sensor_id
    assert copied.sensor_type == original.sensor_type
    assert copied.value == 30.0  # Modified
    assert copied.unit == original.unit
    assert copied.timestamp == original.timestamp


def test_model_json_schema():
    """Test that model generates valid JSON schema."""
    schema = SensorReading.model_json_schema()

    assert isinstance(schema, dict)
    assert "properties" in schema
    assert "sensor_id" in schema["properties"]
    assert "sensor_type" in schema["properties"]
    assert "value" in schema["properties"]
    assert "unit" in schema["properties"]
    assert "timestamp" in schema["properties"]


def test_zero_and_negative_edge_cases():
    """Test zero and negative values in edge scenarios."""
    test_cases = [
        (0, "Zero integer"),
        (0.0, "Zero float"),
        (-0.0, "Negative zero"),
        (-1e-323, "Smallest negative subnormal"),
        (1e-323, "Smallest positive subnormal"),
    ]

    for value, description in test_cases:
        reading = SensorReading(
            sensor_id="edge_case", sensor_type="position", value=value, unit="float"
        )
        assert reading.value == float(value), f"Failed for {description}"
