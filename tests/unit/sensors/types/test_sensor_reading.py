"""
Additional test cases to achieve 100% code coverage for sensor_reading.py

The missing coverage is on lines 42 and 44 in the check_value validator:
- Line 42: raise ValueError("The value cannot be None") 
- Line 44: raise ValueError("The value cannot be a string")

These lines are not being reached because Pydantic's built-in validation
handles None and string conversion before our custom validator runs.
"""

import pytest
from unittest.mock import patch
from pydantic import ValidationError, field_validator
from core.sensors.types.sensor_reading import SensorReading, SensorType, UnitOfMeasure


def test_value_validator_none_direct_call():
    """Test the custom validator directly with None to cover line 42."""
    # Call the class method directly
    with pytest.raises(ValueError, match="The value cannot be None"):
        SensorReading.check_value(None)


def test_value_validator_string_direct_call():
    """Test the custom validator directly with string to cover line 44."""
    # Call the class method directly
    with pytest.raises(ValueError, match="The value cannot be a string"):
        SensorReading.check_value("not_a_number")


# Alternative approach using direct instantiation with mock
def test_value_validator_none_with_mock():
    """Test None value handling in validator."""
    # Test the validator method directly - this should cover line 42
    with pytest.raises(ValueError, match="The value cannot be None"):
        SensorReading.check_value(None)


def test_value_validator_string_with_mock():
    """Test string value handling in validator."""  
    # Test the validator method directly - this should cover line 44
    with pytest.raises(ValueError, match="The value cannot be a string"):
        SensorReading.check_value("invalid_string")


# Most reliable approach: Test the class method directly
def test_check_value_method_none():
    """Test check_value class method directly with None."""
    with pytest.raises(ValueError, match="The value cannot be None"):
        SensorReading.check_value(None)


def test_check_value_method_string():
    """Test check_value class method directly with string."""  
    with pytest.raises(ValueError, match="The value cannot be a string"):
        SensorReading.check_value("test_string")


def test_check_value_method_string_edge_cases():
    """Test check_value with various string edge cases."""
    test_strings = [
        "abc",
        "123abc", 
        "abc123",
        " ",
        "\n",
        "\t",
        "true",
        "false",
        "null",
        "undefined"
    ]
    
    for test_string in test_strings:
        with pytest.raises(ValueError, match="The value cannot be a string"):
            SensorReading.check_value(test_string)


# Test to ensure the validator works correctly for valid values
def test_check_value_method_valid_values():
    """Test check_value method with valid numeric values."""
    valid_values = [0, 1, -1, 3.14, -273.15, float('inf'), float('-inf')]
    
    for value in valid_values:
        # Should not raise any exception
        result = SensorReading.check_value(value)
        assert result == value


def test_check_value_method_nan():
    """Test check_value method with NaN (should already be covered but ensuring consistency)."""
    with pytest.raises(ValueError, match="The value cannot be NaN"):
        SensorReading.check_value(float('nan'))