"""
@description: Unit tests for the TemperatureSensor class.
@author: Nicola Guerra
"""

from unittest.mock import Mock


import grpc
import asyncio

from core.sensors.temperature_sensor import TemperatureSensor
from core.sensors.types.sensor_reading import SensorReading, SensorType, UnitOfMeasure


def test_constructor_sets_id_and_type():
    ts = TemperatureSensor("t-1", Mock())
    assert ts.sensor_id == "t-1"
    assert ts.sensor_type == SensorType.TEMPERATURE


def test_get_metadata_returns_expected_dict():
    ts = TemperatureSensor("t-2", Mock())
    meta = ts.get_metadata()
    assert meta == {"id": "t-2", "type": SensorType.TEMPERATURE.value}


def test_read_data_returns_sensor_reading():
    ts = TemperatureSensor("t-3", Mock())
    reading = ts.read_data()
    assert isinstance(reading, SensorReading)
    assert reading.sensor_id == "t-3"
    assert reading.sensor_type == SensorType.TEMPERATURE
    assert 18.0 <= reading.value <= 30.0
    assert reading.unit == UnitOfMeasure.CELSIUS
    assert hasattr(reading, "timestamp")


def test_calibrate_logs_info(caplog):
    from unittest.mock import Mock, patch

    ts = TemperatureSensor("t-4", Mock())
    with patch.object(ts.logger, "info") as mock_info:
        ts.calibrate()
        mock_info.assert_called_once_with("Calibrating temperature sensor t-4")


def test_read_data_edge_case_sensor_id_empty():
    from unittest.mock import Mock

    ts = TemperatureSensor("", Mock())
    import pytest
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        ts.read_data()


def test_read_data_edge_case_sensor_id_special():
    from unittest.mock import Mock

    ts = TemperatureSensor("!@#$_sensor", Mock())
    reading = ts.read_data()
    assert reading.sensor_id == "!@#$_sensor"


def test_logger_is_initialized():
    from unittest.mock import Mock

    ts = TemperatureSensor("t-5", Mock())
    assert hasattr(ts, "logger")
    assert callable(getattr(ts.logger, "info", None))


def test_stop_sets_running_false():
    ts = TemperatureSensor("t-stop", Mock())
    ts.running = True
    ts.stop()
    assert ts.running is False


def test_run_sends_reading_and_logs(monkeypatch):
    ts = TemperatureSensor("t-run", Mock())
    ts.running = True
    monkeypatch.setattr(
        ts,
        "read_data",
        lambda: SensorReading(
            sensor_id="t-run",
            sensor_type=SensorType.TEMPERATURE,
            value=20.0,
            unit=UnitOfMeasure.CELSIUS,
        ),
    )
    called = {}
    class Resp:
        message = "ok"
    async def fake_send(reading):
        called["sent"] = True
        ts.running = False
        return Resp()
    ts.grpc_layer = Mock()
    ts.grpc_layer.send = fake_send
    infos = []
    monkeypatch.setattr(ts.logger, "info", lambda msg: infos.append(msg))
    async def fake_sleep(x): return None
    monkeypatch.setattr(asyncio, "sleep", fake_sleep)
    asyncio.run(ts.run())
    assert called.get("sent")
    assert any("Inviato" in str(msg) for msg in infos)


def test_run_handles_grpc_error(monkeypatch):
    ts = TemperatureSensor("t-grpc", Mock())
    ts.running = True
    monkeypatch.setattr(
        ts,
        "read_data",
        lambda: SensorReading(
            sensor_id="t-grpc",
            sensor_type=SensorType.TEMPERATURE,
            value=21.0,
            unit=UnitOfMeasure.CELSIUS,
        ),
    )
    class FakeRpcError(grpc.RpcError):
        def details(self):
            return "errore finto"
    async def fake_send(reading):
        ts.running = False
        raise FakeRpcError()
    ts.grpc_layer = Mock()
    ts.grpc_layer.send = fake_send
    errors = []
    monkeypatch.setattr(ts.logger, "error", lambda msg: errors.append(msg))
    async def fake_sleep(x): return None
    monkeypatch.setattr(asyncio, "sleep", fake_sleep)
    asyncio.run(ts.run())
    assert any("Errore gRPC" in str(msg) for msg in errors)
