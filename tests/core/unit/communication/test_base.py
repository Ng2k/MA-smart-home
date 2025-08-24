"""
@description: Test suite for the Base class for communication layers
@author: Nicola Guerra
"""

import asyncio
from abc import ABC
from typing import Any

import pytest

from core.communication.base import CommunicationLayer


@pytest.fixture
def communication_factory():
    """Return a simple concrete CommunicationLayer for tests.

    The implementation is intentionally small; tests parametrize inputs and
    side-effects to exercise behavior.
    """

    class Concrete(CommunicationLayer):
        def __init__(
            self,
            receive_return="default",
            send_side_effect=None,
            receive_side_effect=None,
            start_side_effect=None,
            stop_side_effect=None,
        ):
            self.receive_return = receive_return
            self.send_side_effect = send_side_effect
            self.receive_side_effect = receive_side_effect
            self.start_side_effect = start_side_effect
            self.stop_side_effect = stop_side_effect
            self.sent = []
            self.received = []
            self.started = False
            self.stopped = False

        async def send(self, target: str, message: Any) -> None:
            if self.send_side_effect:
                raise self.send_side_effect
            self.sent.append((target, message))

        async def receive(self) -> Any:
            if self.receive_side_effect:
                raise self.receive_side_effect
            self.received.append(self.receive_return)
            return self.receive_return

        async def start(self) -> None:
            if self.start_side_effect:
                raise self.start_side_effect
            self.started = True

        async def stop(self) -> None:
            if self.stop_side_effect:
                raise self.stop_side_effect
            self.stopped = True

    def _factory(**kwargs):
        return Concrete(**kwargs)

    return _factory


@pytest.fixture
def partial_impl_factory():
    """Factory that can create classes missing one or more abstract methods."""

    def _factory(missing=()):
        attrs = {}

        if "send" not in missing:

            async def send(self, target: str, message: Any) -> None:  # type: ignore
                pass

            attrs["send"] = send

        if "receive" not in missing:

            async def receive(self) -> Any:  # type: ignore
                return "ok"

            attrs["receive"] = receive

        if "start" not in missing:

            async def start(self) -> None:  # type: ignore
                pass

            attrs["start"] = start

        if "stop" not in missing:

            async def stop(self) -> None:  # type: ignore
                pass

            attrs["stop"] = stop

        return type("Partial", (CommunicationLayer,), attrs)

    return _factory


def test_cannot_instantiate_abstract_class():
    with pytest.raises(TypeError):
        CommunicationLayer()


@pytest.mark.parametrize(
    "missing",
    [
        ("send",),
        ("receive",),
        ("start",),
        ("stop",),
        ("send", "receive"),
    ],
)
def test_partial_implementations_raise_typeerror(partial_impl_factory, missing):
    Partial = partial_impl_factory(missing=missing)
    with pytest.raises(TypeError):
        Partial()


def test_is_abstract_base_class_shape():
    assert issubclass(CommunicationLayer, ABC)
    assert hasattr(CommunicationLayer, "__abstractmethods__")
    assert set(CommunicationLayer.__abstractmethods__) == {
        "send",
        "receive",
        "start",
        "stop",
    }


@pytest.mark.asyncio
async def test_basic_send_receive_start_stop(communication_factory):
    comm = communication_factory()

    # start/stop
    await comm.start()
    assert comm.started
    await comm.stop()
    assert comm.stopped

    # send/receive
    await comm.send("t", "m")
    assert comm.sent == [("t", "m")]
    val = await comm.receive()
    assert val == "default"


@pytest.mark.parametrize(
    "target,message",
    [
        ("node", "s"),
        ("", "empty_target"),
        (123, {"k": "v"}),
        ("unicode_节点", "消息_🚀"),
    ],
)
@pytest.mark.asyncio
async def test_send_various_inputs(communication_factory, target, message):
    comm = communication_factory()
    await comm.send(target, message)
    assert comm.sent and comm.sent[-1] == (target, message)


@pytest.mark.parametrize("exc", [ValueError("x"), RuntimeError("y")])
@pytest.mark.asyncio
async def test_exceptions_propagate_on_methods(communication_factory, exc):
    # test send exception
    comm = communication_factory(send_side_effect=exc)
    with pytest.raises(type(exc)):
        await comm.send("t", "m")

    # test receive exception
    comm = communication_factory(receive_side_effect=exc)
    with pytest.raises(type(exc)):
        await comm.receive()

    # test start/stop exceptions
    comm = communication_factory(start_side_effect=exc)
    with pytest.raises(type(exc)):
        await comm.start()

    comm = communication_factory(stop_side_effect=exc)
    with pytest.raises(type(exc)):
        await comm.stop()


@pytest.mark.asyncio
async def test_methods_are_coroutines_and_can_be_awaited(communication_factory):
    comm = communication_factory()
    # class-level checks
    assert asyncio.iscoroutinefunction(CommunicationLayer.send)
    assert asyncio.iscoroutinefunction(CommunicationLayer.receive)
    assert asyncio.iscoroutinefunction(CommunicationLayer.start)
    assert asyncio.iscoroutinefunction(CommunicationLayer.stop)

    # calling returns coroutine objects; create and then await them to avoid warnings
    c_send = comm.send("t", "m")
    assert asyncio.iscoroutine(c_send)
    await c_send

    c_receive = comm.receive()
    assert asyncio.iscoroutine(c_receive)
    await c_receive

    c_start = comm.start()
    assert asyncio.iscoroutine(c_start)
    await c_start

    c_stop = comm.stop()
    assert asyncio.iscoroutine(c_stop)
    await c_stop


@pytest.mark.asyncio
async def test_concurrent_operations_compact(communication_factory):
    comm = communication_factory(receive_return="r")
    tasks = [comm.send(str(i), i) for i in range(10)] + [
        comm.receive() for _ in range(5)
    ]
    await asyncio.gather(*tasks)
    assert len(comm.sent) == 10
    assert len(comm.received) == 5


def test_docstrings_and_module_metadata():
    # method docstrings kept in Italian in the source; check presence
    assert CommunicationLayer.send.__doc__ is not None
    assert "Send a message to a targeted node." in CommunicationLayer.send.__doc__
    assert CommunicationLayer.start.__doc__ is not None
    assert "Start the communication layer (server)." in CommunicationLayer.start.__doc__


@pytest.mark.asyncio
async def test_abstract_pass_statements_are_reachable():
    # cover the abstract 'pass' bodies by calling super() implementations
    class Caller(CommunicationLayer):
        async def send(self, target: str, message: Any) -> None:
            await super().send(target, message)

        async def receive(self) -> Any:
            return await super().receive()

        async def start(self) -> None:
            await super().start()

        async def stop(self) -> None:
            await super().stop()

    c = Caller()
    await c.send("t", "m")
    res = await c.receive()
    assert res is None
    await c.start()
    await c.stop()
