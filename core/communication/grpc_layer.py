"""
@description: gRPC layer for communication with the smart home system.
@author: Nicola Guerra
"""

import grpc

from core.communication.base import CommunicationLayer
from proto import sensor_pb2, sensor_pb2_grpc


class GRPCSensorService(sensor_pb2_grpc.SensorServiceServicer):
    def __init__(self, on_receive):
        self.on_receive = on_receive

    async def SendReading(self, request, context):
        await self.on_receive(request.reading)
        return sensor_pb2.SensorResponse(success=True, message="Reading received")  # type: ignore


class GRPCCommunicationLayer(CommunicationLayer):
    def __init__(self, host="localhost", port=50051, on_receive=None):
        self.host = host
        self.port = port
        self.on_receive = on_receive
        self.server = grpc.aio.server()
        sensor_pb2_grpc.add_SensorServiceServicer_to_server(
            GRPCSensorService(on_receive), self.server
        )
        self.server.add_insecure_port(f"{self.host}:{self.port}")

    async def start(self):
        await self.server.start()
        print(f"[gRPC] Server started at {self.host}:{self.port}")
        await self.server.wait_for_termination()

    async def stop(self):
        await self.server.stop(0)

    async def send(self, target: str, message):
        async with grpc.aio.insecure_channel(target) as channel:
            stub = sensor_pb2_grpc.SensorServiceStub(channel)
            request = sensor_pb2.SensorRequest(reading=message)  # type: ignore
            return await stub.SendReading(request)

    async def receive(self):
        # Qui riceviamo tramite callback (on_receive), quindi opzionale
        pass
