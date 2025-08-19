"""
@author: Nicola Guerra
@description: This module provides the communication layer for the smart home system.
"""

from abc import ABC, abstractmethod
from typing import Any


class CommunicationLayer(ABC):
    @abstractmethod
    async def send(self, target: str, message: Any) -> None:
        """Invia un messaggio a un target identificato (es. un altro nodo)."""
        pass

    @abstractmethod
    async def receive(self) -> Any:
        """Riceve un messaggio da un altro nodo."""
        pass

    @abstractmethod
    async def start(self) -> None:
        """Avvia il layer di comunicazione (server)."""
        pass

    @abstractmethod
    async def stop(self) -> None:
        """Ferma il layer di comunicazione (server)."""
        pass
