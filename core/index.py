"""
@description: This is the main entry point for the smart home system.
@author: Nicola Guerra
"""

import asyncio
from core.sensors.temperature_sensor import TemperatureSensor

async def main():
    sensor1 = TemperatureSensor("sensor_1", interval=2)
    sensor2 = TemperatureSensor("sensor_2", interval=3)

    await asyncio.gather(sensor1.run(), sensor2.run())

if __name__ == "__main__":
    asyncio.run(main())
