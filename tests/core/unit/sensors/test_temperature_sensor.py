"""
@description: Unit tests for the TemperatureSensor class.
@author: Nicola Guerra
"""

import grpc

from core.sensors.temperature_sensor import TemperatureSensor
from core.sensors.types.sensor_reading import SensorReading, SensorType, UnitOfMeasure


from unittest.mock import Mock

def test_constructor_sets_id_and_type():
    ts = TemperatureSensor("t-1", stub=Mock())
    assert ts.sensor_id == "t-1"
    assert ts.sensor_type == SensorType.TEMPERATURE


def test_get_metadata_returns_expected_dict():
    ts = TemperatureSensor("t-2", stub=Mock())
    meta = ts.get_metadata()
    assert meta == {"id": "t-2", "type": SensorType.TEMPERATURE.value}


def test_read_data_returns_sensor_reading():
    ts = TemperatureSensor("t-3", stub=Mock())
    reading = ts.read_data()
    assert isinstance(reading, SensorReading)
    assert reading.sensor_id == "t-3"
    assert reading.sensor_type == SensorType.TEMPERATURE
    assert 18.0 <= reading.value <= 30.0
    assert reading.unit == UnitOfMeasure.CELSIUS
    assert hasattr(reading, "timestamp")


def test_calibrate_logs_info(caplog):
    from unittest.mock import patch, Mock

    ts = TemperatureSensor("t-4", stub=Mock())
    with patch.object(ts.logger, "info") as mock_info:
        ts.calibrate()
        mock_info.assert_called_once_with("Calibrating temperature sensor t-4")


def test_read_data_edge_case_sensor_id_empty():
    from unittest.mock import Mock
    ts = TemperatureSensor("", stub=Mock())
    import pytest
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        ts.read_data()


def test_read_data_edge_case_sensor_id_special():
    from unittest.mock import Mock
    ts = TemperatureSensor("!@#$_sensor", stub=Mock())
    reading = ts.read_data()
    assert reading.sensor_id == "!@#$_sensor"


def test_logger_is_initialized():
    from unittest.mock import Mock
    ts = TemperatureSensor("t-5", stub=Mock())
    assert hasattr(ts, "logger")
    assert callable(getattr(ts.logger, "info", None))


def test_stop_sets_running_false():
    ts = TemperatureSensor("t-stop", stub=Mock())
    ts.running = True
    ts.stop()
    assert ts.running is False

def test_run_sends_reading_and_logs(monkeypatch):
    ts = TemperatureSensor("t-run", stub=Mock())
    ts.running = True
    # Patch read_data to return a predictable value
    monkeypatch.setattr(ts, "read_data", lambda: SensorReading(
        sensor_id="t-run",
        sensor_type=SensorType.TEMPERATURE,
        value=20.0,
        unit=UnitOfMeasure.CELSIUS,
    ))
    # Patch stub.SendReading to stop after one call
    called = {}
    def fake_send_reading(request):
        called['sent'] = True
        ts.running = False  # Stop after one iteration
        class Resp: message = "ok"
        return Resp()
    ts.stub.SendReading = fake_send_reading
    # Patch logger.info to track calls
    infos = []
    monkeypatch.setattr(ts.logger, "info", lambda msg: infos.append(msg))
    ts.run()
    assert called.get('sent')
    assert any("Inviato" in str(msg) for msg in infos)

def test_run_handles_grpc_error(monkeypatch):
    ts = TemperatureSensor("t-grpc", stub=Mock())
    ts.running = True
    monkeypatch.setattr(ts, "read_data", lambda: SensorReading(
        sensor_id="t-grpc",
        sensor_type=SensorType.TEMPERATURE,
        value=21.0,
        unit=UnitOfMeasure.CELSIUS,
    ))
    class FakeRpcError(grpc.RpcError):
        def details(self):
            return "errore finto"
    def fake_send_reading(request):
        ts.running = False
        raise FakeRpcError()
    ts.stub.SendReading = fake_send_reading
    errors = []
    monkeypatch.setattr(ts.logger, "error", lambda msg: errors.append(msg))
    ts.run()
    assert any("Errore gRPC" in str(msg) for msg in errors)