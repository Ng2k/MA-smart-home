"""
Unit tests for GRPCCommunicationLayer and GRPCSensorService classes.

@author: Nicola Guerra
"""

from unittest.mock import AsyncMock, Mock, patch

import pytest

# -----------------------
# Fixtures
# -----------------------


@pytest.fixture
def mock_grpc():
    with patch("core.communication.grpc_server.grpc") as grpc_mock:
        server = AsyncMock()
        server.start = AsyncMock()
        server.stop = AsyncMock()
        server.wait_for_termination = AsyncMock()
        server.add_insecure_port = Mock()
        channel = AsyncMock()
        channel.__aenter__ = AsyncMock(return_value=channel)
        channel.__aexit__ = AsyncMock(return_value=None)
        grpc_mock.aio.server.return_value = server
        grpc_mock.aio.insecure_channel.return_value = channel
        yield {"module": grpc_mock, "server": server, "channel": channel}


@pytest.fixture
def mock_protobuf():
    with patch("core.communication.grpc_server.sensor_pb2") as pb2, patch(
        "core.communication.grpc_server.sensor_pb2_grpc"
    ) as pb2_grpc:

        response = Mock(success=True, message="Reading received")
        request = Mock(reading="test_data")
        pb2.SensorResponse.return_value = response
        pb2.SensorRequest.return_value = request

        pb2_grpc.SensorServiceServicer = type("Servicer", (), {})
        pb2_grpc.add_SensorServiceServicer_to_server = Mock()
        stub = AsyncMock()
        stub.SendReading = AsyncMock(return_value=response)
        pb2_grpc.SensorServiceStub.return_value = stub

        yield {
            "sensor_pb2": pb2,
            "sensor_pb2_grpc": pb2_grpc,
            "response": response,
            "request": request,
            "stub": stub,
        }


# -----------------------
# GRPCSensorService Tests
# -----------------------


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "reading_data", ["string", {"complex": [1, 2]}, ["list"], 42, None, ""]
)
async def test_send_reading_calls_callback(mock_protobuf, reading_data):
    from core.communication.grpc_server import GRPCSensorService

    on_receive = AsyncMock()
    service = GRPCSensorService(on_receive)
    mock_request = Mock(reading=reading_data)
    mock_context = Mock()

    result = await service.SendReading(mock_request, mock_context)

    on_receive.assert_called_once_with(reading_data)
    mock_protobuf["sensor_pb2"].SensorResponse.assert_called_once_with(
        success=True, message="Reading received"
    )
    assert result == mock_protobuf["response"]


@pytest.mark.asyncio
async def test_send_reading_callback_exceptions(mock_protobuf):
    from core.communication.grpc_server import GRPCSensorService

    on_receive = AsyncMock(side_effect=ValueError("Callback error"))
    service = GRPCSensorService(on_receive)
    mock_request = Mock(reading="test")
    mock_context = Mock()

    with pytest.raises(ValueError, match="Callback error"):
        await service.SendReading(mock_request, mock_context)


# -----------------------
# GRPCCommunicationLayer Tests
# -----------------------


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "host,port", [("localhost", 50051), ("0.0.0.0", 8080), ("grpc.example.com", 443)]
)
async def test_layer_lifecycle_and_send(mock_grpc, mock_protobuf, host, port):
    from core.communication.grpc_server import GRPCCommunicationLayer

    callback = AsyncMock()
    layer = GRPCCommunicationLayer(host=host, port=port, on_receive=callback)

    with patch("builtins.print"):
        await layer.start()
        result = await layer.send(f"{host}:{port}", "message")
        await layer.stop()

    assert result == mock_protobuf["response"]
    mock_grpc["server"].start.assert_called_once()
    mock_grpc["server"].wait_for_termination.assert_called_once()
    mock_grpc["server"].stop.assert_called_once_with(0)
    mock_grpc["module"].aio.insecure_channel.assert_called_once_with(f"{host}:{port}")


@pytest.mark.asyncio
async def test_send_various_messages(mock_grpc, mock_protobuf):
    from core.communication.grpc_server import GRPCCommunicationLayer

    layer = GRPCCommunicationLayer()
    messages = ["string", {"dict": 1}, ["list"], None]

    for msg in messages:
        result = await layer.send("target:50051", msg)
        assert result == mock_protobuf["response"]


@pytest.mark.asyncio
async def test_receive_noop(mock_grpc, mock_protobuf):
    from core.communication.grpc_server import GRPCCommunicationLayer

    layer = GRPCCommunicationLayer()
    result = await layer.receive()
    assert result is None


def test_layer_inheritance():
    from core.communication.base import CommunicationLayer
    from core.communication.grpc_server import GRPCCommunicationLayer

    layer = GRPCCommunicationLayer()
    assert isinstance(layer, CommunicationLayer)
    assert hasattr(layer, "send") and hasattr(layer, "receive")


@pytest.mark.asyncio
async def test_integration_service_layer(mock_grpc, mock_protobuf):
    from core.communication.grpc_server import GRPCCommunicationLayer

    callback = AsyncMock()
    GRPCCommunicationLayer(on_receive=callback)

    # Access registered service
    service_call = mock_protobuf[
        "sensor_pb2_grpc"
    ].add_SensorServiceServicer_to_server.call_args
    service_instance = service_call[0][0]

    mock_request = Mock(reading="integration_test")
    mock_context = Mock()
    response = await service_instance.SendReading(mock_request, mock_context)

    callback.assert_called_once_with("integration_test")
    assert response == mock_protobuf["response"]
