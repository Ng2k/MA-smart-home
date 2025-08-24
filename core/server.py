"""
@description: This module provides the gRPC server implementation for the smart home system.
@author: Nicola Guerra
"""
import asyncio
from core.communication.grpc_server import GRPCCommunicationLayer
from proto import sensor_pb2
from logger.factory import get_logger

logger = get_logger("ServerGRPC")

async def handle_reading(reading: sensor_pb2.SensorReading):
    logger.info(f"Received from sensor {reading.sensor_id}: {reading.value:.2f} {reading.sensor_type}")

async def main():
    grpc_layer = GRPCCommunicationLayer(host="localhost", port=50051, on_receive=handle_reading)
    await grpc_layer.start()  # rimane in ascolto

if __name__ == "__main__":
    asyncio.run(main())