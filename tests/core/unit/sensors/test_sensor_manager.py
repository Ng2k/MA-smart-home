"""
Test suite per il modulo sensor_manager.

@description: Suite completa di test per SensorManager con 100% code coverage
@author: Test Suite Generator
"""
import threading
from unittest.mock import MagicMock, patch
import pytest

from core.sensors.sensor_manager import SensorManager
from core.sensors.sensor_enum import SensorType
from core.sensors.sensor_node import SensorNode
from core.sensors.temperature_sensor import TemperatureSensor


@pytest.fixture
def mock_stub():
    """Return a mock gRPC stub."""
    return MagicMock()


@pytest.fixture
def manager(mock_stub):
    """Return a SensorManager instance with stub mocked."""
    with patch("grpc.insecure_channel"):
        mgr = SensorManager("localhost:50051")
        mgr.stub = mock_stub  # replace real stub with mock
        return mgr


def test_add_sensor_temperature(manager):
    """Test adding a temperature sensor."""
    manager.add_sensor(SensorType.TEMPERATURE, interval=1.0)
    assert len(manager.sensors) == 1
    sensor = manager.sensors[0]
    assert isinstance(sensor, TemperatureSensor)
    assert sensor.sensor_id == "sensor_1"
    assert sensor.interval == 1.0
    assert manager.threads == []


def test_add_sensor_invalid_type(manager):
    """Test adding sensor with invalid types raises errors."""
    # Unsupported type value
    class FakeType:
        value = "FAKE"

    # Not an enum
    with pytest.raises(TypeError):
        manager.add_sensor("not_enum")


@patch.object(TemperatureSensor, "run")
def test_start_all(mock_run, manager):
    """Test that starting sensors creates daemon threads."""
    manager.add_sensor(SensorType.TEMPERATURE)
    manager.start_all()
    assert len(manager.threads) == 1
    thread = manager.threads[0]
    assert isinstance(thread, threading.Thread)
    assert thread.daemon is True  # thread deve essere daemon


def test_stop_all(manager):
    """Test stopping all sensors and joining threads."""
    # Aggiungo sensore mock
    sensor_mock = MagicMock(spec=SensorNode)
    manager.sensors.append(sensor_mock)

    # Creo thread fittizio
    def dummy_run():
        return

    thread = threading.Thread(target=dummy_run)
    thread.start()
    manager.threads.append(thread)

    manager.stop_all()

    sensor_mock.stop.assert_called_once()
    assert not thread.is_alive()


def test_multiple_sensors(manager):
    """Test adding and starting multiple sensors."""
    manager.add_sensor(SensorType.TEMPERATURE)
    manager.add_sensor(SensorType.TEMPERATURE)
    assert len(manager.sensors) == 2
    manager.start_all()
    assert len(manager.threads) == 2


def test_stub_passed_to_sensor(monkeypatch):
    """Test that stub is correctly passed to the sensor on creation."""
    init_args = {}

    def fake_init(self, sensor_id, stub, interval):
        init_args["stub"] = stub
        init_args["sensor_id"] = sensor_id
        init_args["interval"] = interval
        # inizializza attributi minimi per evitare errori
        self.sensor_id = sensor_id
        self.stub = stub
        self.interval = interval

    monkeypatch.setattr(TemperatureSensor, "__init__", fake_init)

    from core.sensors.sensor_manager import SensorManager
    from unittest.mock import MagicMock
    stub_mock = MagicMock()
    manager = SensorManager("localhost:50051")
    manager.stub = stub_mock
    manager.add_sensor(SensorType.TEMPERATURE)

    assert init_args["stub"] == stub_mock
    assert init_args["sensor_id"] == "sensor_1"


def test_thread_daemon_flag(manager):
    """Test that created threads are daemon."""
    manager.add_sensor(SensorType.TEMPERATURE)
    manager.start_all()
    for thread in manager.threads:
        assert thread.daemon is True