"""
@description: This module provides a gRPC client implementation for the smart home system.
@author: Nicola Guerra
"""
import grpc
from proto import sensor_pb2, sensor_pb2_grpc

class GRPCClient:
    def __init__(self, server_address: str):
        self.server_address = server_address

    async def send(self, message):
        """Send a gRPC message to the server.

        :param message: The message to send.
        """
        async with grpc.aio.insecure_channel(self.server_address) as channel:
            stub = sensor_pb2_grpc.SensorServiceStub(channel)
            request = sensor_pb2.SensorRequest(reading=message)  # type: ignore
            return await stub.SendReading(request)