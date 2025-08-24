"""
@description: This module provides the communication layer for the smart home system.
@author: Nicola Guerra
"""

from abc import ABC, abstractmethod
from typing import Any


class CommunicationLayer(ABC):
    @abstractmethod
    async def send(self, target: str, message: Any) -> None:
        """Send a message to a targeted node."""
        pass

    @abstractmethod
    async def receive(self) -> Any:
        """Receive a message from another node."""
        pass

    @abstractmethod
    async def start(self) -> None:
        """Start the communication layer (server)."""
        pass

    @abstractmethod
    async def stop(self) -> None:
        """Stop the communication layer (server)."""
        pass
