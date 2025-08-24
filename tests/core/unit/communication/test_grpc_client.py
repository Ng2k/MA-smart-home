"""
@description: Test suite for the gRPC client.
@author: Nicola Guerra
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from core.communication.grpc_client import GRPCClient

@pytest.mark.asyncio
async def test_init_sets_server_address():
	client = GRPCClient("localhost:1234")
	assert client.server_address == "localhost:1234"

@pytest.mark.asyncio
async def test_send_calls_grpc(monkeypatch):
	client = GRPCClient("localhost:1234")
	fake_channel = MagicMock()
	fake_stub = MagicMock()
	fake_response = MagicMock()
	# Patch grpc.aio.insecure_channel to return async context manager
	class FakeAsyncContext:
		async def __aenter__(self): return fake_channel
		async def __aexit__(self, exc_type, exc, tb): return None
	monkeypatch.setattr("grpc.aio.insecure_channel", lambda addr: FakeAsyncContext())
	# Patch stub and proto
	with patch("core.communication.grpc_client.sensor_pb2_grpc.SensorServiceStub", return_value=fake_stub) as stub_patch, \
		 patch("core.communication.grpc_client.sensor_pb2.SensorRequest", return_value="req") as req_patch:
		fake_stub.SendReading = AsyncMock(return_value=fake_response)
		msg = MagicMock()
		result = await client.send(msg)
		stub_patch.assert_called_once_with(fake_channel)
		req_patch.assert_called_once_with(reading=msg)
		fake_stub.SendReading.assert_awaited_once_with("req")
		assert result is fake_response

@pytest.mark.asyncio
async def test_send_handles_exception(monkeypatch):
	client = GRPCClient("localhost:1234")
	class FakeAsyncContext:
		async def __aenter__(self): return MagicMock()
		async def __aexit__(self, exc_type, exc, tb): return None
	monkeypatch.setattr("grpc.aio.insecure_channel", lambda addr: FakeAsyncContext())
	with patch("core.communication.grpc_client.sensor_pb2_grpc.SensorServiceStub") as stub_patch, \
		 patch("core.communication.grpc_client.sensor_pb2.SensorRequest", return_value="req"):
		stub = stub_patch.return_value
		stub.SendReading = AsyncMock(side_effect=Exception("fail"))
		with pytest.raises(Exception) as exc:
			await client.send(MagicMock())
		assert "fail" in str(exc.value)
