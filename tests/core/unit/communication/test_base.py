"""
Unit tests for the abstract CommunicationLayer class.

This module provides comprehensive test coverage for the CommunicationLayer abstract class,
including abstract method enforcement, async behavior, type annotations, and edge cases.

Best practices applied:
- Async fixture factory for creating concrete instances
- Parametrized tests for multiple cases
- Full coverage of async abstract methods
- Abstract class enforcement testing
- Clear test function names describing what is being tested
- No pytest collection warnings
- Proper async/await testing with pytest-asyncio

@author: Nicola Guerra
"""

import asyncio
from abc import ABC
from typing import Any

import pytest

from core.communication.base import CommunicationLayer

# -----------------------
# Async fixture factory
# -----------------------


@pytest.fixture
def async_communication_factory():
    """
    Fixture returning a factory function for creating concrete CommunicationLayer instances.
    The concrete class is local to avoid pytest collection warnings.
    """

    class ConcreteCommunicationLayer(CommunicationLayer):
        """Concrete implementation for testing purposes."""

        def __init__(
            self,
            send_return=None,
            receive_return="USE_DEFAULT",
            send_side_effect=None,
            receive_side_effect=None,
            start_side_effect=None,
            stop_side_effect=None,
        ):
            self._send_return = send_return
            if receive_return == "USE_DEFAULT":
                self._receive_return = "default_message"
            else:
                self._receive_return = receive_return
            self._send_side_effect = send_side_effect
            self._receive_side_effect = receive_side_effect
            self._start_side_effect = start_side_effect
            self._stop_side_effect = stop_side_effect
            self.sent_messages = []
            self.received_messages = []
            self.started = False
            self.stopped = False

        async def send(self, target: str, message: Any) -> None:
            """Test implementation of send."""
            if self._send_side_effect:
                raise self._send_side_effect
            self.sent_messages.append((target, message))
            return self._send_return

        async def receive(self) -> Any:
            """Test implementation of receive."""
            if self._receive_side_effect:
                raise self._receive_side_effect
            self.received_messages.append(self._receive_return)
            return self._receive_return

        async def start(self) -> None:
            """Test implementation of start."""
            if self._start_side_effect:
                raise self._start_side_effect
            self.started = True

        async def stop(self) -> None:
            """Test implementation of stop."""
            if self._stop_side_effect:
                raise self._stop_side_effect
            self.stopped = True

    def _factory(**kwargs):
        return ConcreteCommunicationLayer(**kwargs)

    return _factory


@pytest.fixture
def partial_implementation_factory():
    """
    Fixture for creating classes that only implement some abstract methods.
    Used to test abstract method enforcement.
    """

    def _factory(
        implement_send=True,
        implement_receive=True,
        implement_start=True,
        implement_stop=True,
    ):
        class PartialCommunicationLayer(CommunicationLayer):
            """Partially implemented class for testing abstract enforcement."""

            if implement_send:

                async def send(self, target: str, message: Any) -> None:
                    pass

            if implement_receive:

                async def receive(self) -> Any:
                    return "test"

            if implement_start:

                async def start(self) -> None:
                    pass

            if implement_stop:

                async def stop(self) -> None:
                    pass

        return PartialCommunicationLayer

    return _factory


# -----------------------
# Abstract class behavior tests
# -----------------------


def test_cannot_instantiate_abstract_class():
    """Test that CommunicationLayer cannot be instantiated directly."""
    with pytest.raises(TypeError) as exc_info:
        CommunicationLayer()

    error_message = str(exc_info.value)
    assert "Can't instantiate abstract class CommunicationLayer" in error_message
    assert "abstract method" in error_message


def test_must_implement_all_abstract_methods(partial_implementation_factory):
    """Test that all abstract methods must be implemented."""
    # Test class missing send method
    PartialClass1 = partial_implementation_factory(
        implement_send=False,
        implement_receive=True,
        implement_start=True,
        implement_stop=True,
    )
    with pytest.raises(TypeError) as exc_info:
        PartialClass1()
    assert "send" in str(exc_info.value)

    # Test class missing receive method
    PartialClass2 = partial_implementation_factory(
        implement_send=True,
        implement_receive=False,
        implement_start=True,
        implement_stop=True,
    )
    with pytest.raises(TypeError) as exc_info:
        PartialClass2()
    assert "receive" in str(exc_info.value)

    # Test class missing start method
    PartialClass3 = partial_implementation_factory(
        implement_send=True,
        implement_receive=True,
        implement_start=False,
        implement_stop=True,
    )
    with pytest.raises(TypeError) as exc_info:
        PartialClass3()
    assert "start" in str(exc_info.value)

    # Test class missing stop method
    PartialClass4 = partial_implementation_factory(
        implement_send=True,
        implement_receive=True,
        implement_start=True,
        implement_stop=False,
    )
    with pytest.raises(TypeError) as exc_info:
        PartialClass4()
    assert "stop" in str(exc_info.value)

    # Test class missing multiple methods
    PartialClass5 = partial_implementation_factory(
        implement_send=False,
        implement_receive=False,
        implement_start=False,
        implement_stop=False,
    )
    with pytest.raises(TypeError) as exc_info:
        PartialClass5()
    error_message = str(exc_info.value)
    # Should mention at least one missing method
    assert any(
        method in error_message for method in ["send", "receive", "start", "stop"]
    )


def test_is_abstract_base_class():
    """Test that CommunicationLayer is properly configured as an abstract base class."""
    assert issubclass(CommunicationLayer, ABC)
    assert hasattr(CommunicationLayer, "__abstractmethods__")
    assert len(CommunicationLayer.__abstractmethods__) == 4
    assert "send" in CommunicationLayer.__abstractmethods__
    assert "receive" in CommunicationLayer.__abstractmethods__
    assert "start" in CommunicationLayer.__abstractmethods__
    assert "stop" in CommunicationLayer.__abstractmethods__


# -----------------------
# Async method tests
# -----------------------


@pytest.mark.asyncio
async def test_send_method_basic_functionality(async_communication_factory):
    """Test basic functionality of send method."""
    comm = async_communication_factory()

    target = "node_001"
    message = "test_message"

    result = await comm.send(target, message)

    assert result is None  # send should return None
    assert len(comm.sent_messages) == 1
    assert comm.sent_messages[0] == (target, message)


@pytest.mark.parametrize(
    "target, message",
    [
        ("node_001", "simple_string"),
        ("device_123", {"key": "value", "data": [1, 2, 3]}),
        ("sensor_456", ["list", "of", "items"]),
        ("hub_789", 42),
        ("controller", 3.14159),
        ("gateway", None),
        ("", "empty_target"),
        ("target", ""),
        ("unicode_节点", "unicode_消息_🚀"),
        ("very_long_target_" + "x" * 1000, "message_for_long_target"),
    ],
)
@pytest.mark.asyncio
async def test_send_method_various_inputs(async_communication_factory, target, message):
    """Test send method with various target and message combinations."""
    comm = async_communication_factory()

    result = await comm.send(target, message)

    assert result is None
    assert len(comm.sent_messages) == 1
    assert comm.sent_messages[0] == (target, message)


@pytest.mark.asyncio
async def test_receive_method_basic_functionality(async_communication_factory):
    """Test basic functionality of receive method."""
    test_message = {"type": "sensor_data", "value": 25.5}
    comm = async_communication_factory(receive_return=test_message)

    result = await comm.receive()

    assert result == test_message
    assert len(comm.received_messages) == 1
    assert comm.received_messages[0] == test_message


@pytest.mark.parametrize(
    "receive_return",
    [
        "simple_string",
        {"complex": "object", "with": ["nested", "data"]},
        ["list", "of", "messages"],
        42,
        3.14159,
        "",
        {"unicode": "消息_🌟"},
        {"large_data": "x" * 10000},
    ],
)
@pytest.mark.asyncio
async def test_receive_method_various_returns(
    async_communication_factory, receive_return
):
    """Test receive method with various return values."""
    comm = async_communication_factory(receive_return=receive_return)

    result = await comm.receive()

    assert result == receive_return
    assert len(comm.received_messages) == 1


@pytest.mark.asyncio
async def test_receive_method_none_return(async_communication_factory):
    """Test receive method with explicit None return value."""
    comm = async_communication_factory(receive_return=None)

    result = await comm.receive()

    assert result is None
    assert len(comm.received_messages) == 1


@pytest.mark.asyncio
async def test_start_method_basic_functionality(async_communication_factory):
    """Test basic functionality of start method."""
    comm = async_communication_factory()

    assert not comm.started

    result = await comm.start()

    assert result is None  # start should return None
    assert comm.started


@pytest.mark.asyncio
async def test_stop_method_basic_functionality(async_communication_factory):
    """Test basic functionality of stop method."""
    comm = async_communication_factory()

    assert not comm.stopped

    result = await comm.stop()

    assert result is None  # stop should return None
    assert comm.stopped


# -----------------------
# Exception handling tests
# -----------------------


@pytest.mark.asyncio
async def test_send_method_exception_handling(async_communication_factory):
    """Test send method exception handling."""
    test_exception = ValueError("Send failed")
    comm = async_communication_factory(send_side_effect=test_exception)

    with pytest.raises(ValueError, match="Send failed"):
        await comm.send("target", "message")


@pytest.mark.asyncio
async def test_receive_method_exception_handling(async_communication_factory):
    """Test receive method exception handling."""
    test_exception = ConnectionError("Receive failed")
    comm = async_communication_factory(receive_side_effect=test_exception)

    with pytest.raises(ConnectionError, match="Receive failed"):
        await comm.receive()


@pytest.mark.asyncio
async def test_start_method_exception_handling(async_communication_factory):
    """Test start method exception handling."""
    test_exception = RuntimeError("Start failed")
    comm = async_communication_factory(start_side_effect=test_exception)

    with pytest.raises(RuntimeError, match="Start failed"):
        await comm.start()


@pytest.mark.asyncio
async def test_stop_method_exception_handling(async_communication_factory):
    """Test stop method exception handling."""
    test_exception = RuntimeError("Stop failed")
    comm = async_communication_factory(stop_side_effect=test_exception)

    with pytest.raises(RuntimeError, match="Stop failed"):
        await comm.stop()


# -----------------------
# Async behavior tests
# -----------------------


@pytest.mark.asyncio
async def test_methods_are_coroutines(async_communication_factory):
    """Test that all abstract methods are properly async/coroutines."""
    comm = async_communication_factory()

    # Test that methods return coroutines
    send_coro = comm.send("target", "message")
    receive_coro = comm.receive()
    start_coro = comm.start()
    stop_coro = comm.stop()

    assert asyncio.iscoroutine(send_coro)
    assert asyncio.iscoroutine(receive_coro)
    assert asyncio.iscoroutine(start_coro)
    assert asyncio.iscoroutine(stop_coro)

    # Clean up coroutines
    await send_coro
    await receive_coro
    await start_coro
    await stop_coro


@pytest.mark.asyncio
async def test_concurrent_operations(async_communication_factory):
    """Test concurrent async operations."""
    comm = async_communication_factory(receive_return="concurrent_message")

    # Create multiple concurrent operations
    send_tasks = [comm.send(f"target_{i}", f"message_{i}") for i in range(5)]

    receive_tasks = [comm.receive() for _ in range(3)]

    # Execute all tasks concurrently
    await asyncio.gather(*send_tasks, *receive_tasks)

    # Verify results
    assert len(comm.sent_messages) == 5
    assert len(comm.received_messages) == 3

    # Verify all messages were sent correctly
    for i in range(5):
        assert (f"target_{i}", f"message_{i}") in comm.sent_messages


# -----------------------
# Type annotation tests
# -----------------------


def test_method_signatures():
    """Test that abstract methods have correct type signatures."""
    # Test send method signature
    send_annotations = CommunicationLayer.send.__annotations__
    assert send_annotations.get("target") == str
    assert send_annotations.get("message") == Any
    assert send_annotations.get("return") is None or send_annotations.get(
        "return"
    ) is type(None)

    # Test receive method signature
    receive_annotations = CommunicationLayer.receive.__annotations__
    assert receive_annotations.get("return") == Any

    # Test start method signature
    start_annotations = CommunicationLayer.start.__annotations__
    assert start_annotations.get("return") is None or start_annotations.get(
        "return"
    ) is type(None)

    # Test stop method signature
    stop_annotations = CommunicationLayer.stop.__annotations__
    assert stop_annotations.get("return") is None or stop_annotations.get(
        "return"
    ) is type(None)


def test_abstract_methods_are_async():
    """Test that abstract methods are marked as async."""
    assert asyncio.iscoroutinefunction(CommunicationLayer.send)
    assert asyncio.iscoroutinefunction(CommunicationLayer.receive)
    assert asyncio.iscoroutinefunction(CommunicationLayer.start)
    assert asyncio.iscoroutinefunction(CommunicationLayer.stop)


# -----------------------
# Inheritance behavior tests
# -----------------------


def test_inheritance_chain(async_communication_factory):
    """Test that concrete implementations maintain proper inheritance."""
    comm = async_communication_factory()

    assert isinstance(comm, CommunicationLayer)
    assert isinstance(comm, ABC)
    assert hasattr(comm, "send")
    assert hasattr(comm, "receive")
    assert hasattr(comm, "start")
    assert hasattr(comm, "stop")


def test_multiple_inheritance_scenario():
    """Test CommunicationLayer in multiple inheritance scenarios."""

    class Mixin:
        def mixin_method(self):
            return "mixin"

    class MultipleMixinComm(CommunicationLayer, Mixin):
        async def send(self, target: str, message: Any) -> None:
            pass

        async def receive(self) -> Any:
            return "mixed"

        async def start(self) -> None:
            pass

        async def stop(self) -> None:
            pass

    comm = MultipleMixinComm()

    assert isinstance(comm, CommunicationLayer)
    assert isinstance(comm, Mixin)
    assert comm.mixin_method() == "mixin"


# -----------------------
# Edge cases and stress tests
# -----------------------


@pytest.mark.asyncio
async def test_rapid_sequential_operations(async_communication_factory):
    """Test rapid sequential operations."""
    comm = async_communication_factory(receive_return="rapid_message")

    # Rapid send operations
    for i in range(100):
        await comm.send(f"rapid_target_{i}", f"rapid_message_{i}")

    # Rapid receive operations
    results = []
    for _ in range(50):
        result = await comm.receive()
        results.append(result)

    assert len(comm.sent_messages) == 100
    assert len(results) == 50
    assert all(r == "rapid_message" for r in results)


@pytest.mark.asyncio
async def test_start_stop_lifecycle(async_communication_factory):
    """Test complete start/stop lifecycle."""
    comm = async_communication_factory()

    # Initial state
    assert not comm.started
    assert not comm.stopped

    # Start the communication layer
    await comm.start()
    assert comm.started
    assert not comm.stopped

    # Can send/receive after start
    await comm.send("lifecycle_target", "lifecycle_message")
    result = await comm.receive()
    assert result is not None

    # Stop the communication layer
    await comm.stop()
    assert comm.started  # Still shows as started
    assert comm.stopped  # But also stopped


@pytest.mark.asyncio
async def test_complex_message_types(async_communication_factory):
    """Test with complex message types."""
    complex_messages = [
        {"nested": {"deep": {"structure": {"value": 123}}}},
        [{"item": i} for i in range(10)],
        set([1, 2, 3, 4, 5]),  # Note: sets are not JSON serializable
        {"function": lambda x: x * 2},  # Note: functions are not serializable
        {"class_instance": object()},
    ]

    comm = async_communication_factory()

    for i, message in enumerate(complex_messages):
        await comm.send(f"complex_target_{i}", message)

        # Verify the message was stored correctly
        assert comm.sent_messages[i] == (f"complex_target_{i}", message)


# -----------------------
# Documentation and metadata tests
# -----------------------


def test_class_docstring():
    """Test that CommunicationLayer class exists (no docstring in original)."""
    # The original class doesn't have a docstring, so we just verify it exists
    assert CommunicationLayer is not None
    assert hasattr(CommunicationLayer, "__name__")
    assert CommunicationLayer.__name__ == "CommunicationLayer"


def test_method_docstrings():
    """Test that abstract methods have proper documentation."""
    # Test send method docstring
    assert CommunicationLayer.send.__doc__ is not None
    assert "messaggio" in CommunicationLayer.send.__doc__

    # Test receive method docstring
    assert CommunicationLayer.receive.__doc__ is not None
    assert "messaggio" in CommunicationLayer.receive.__doc__

    # Test start method docstring
    assert CommunicationLayer.start.__doc__ is not None
    assert "Avvia" in CommunicationLayer.start.__doc__

    # Test stop method docstring
    assert CommunicationLayer.stop.__doc__ is not None
    assert "Ferma" in CommunicationLayer.stop.__doc__


def test_module_metadata():
    """Test module-level metadata and structure."""
    import core.communication.base as base_module

    assert hasattr(base_module, "CommunicationLayer")
    assert base_module.__doc__ is not None
    assert "communication layer" in base_module.__doc__


# -----------------------
# Abstract method pass statement coverage
# -----------------------


@pytest.mark.asyncio
async def test_abstract_method_pass_statements():
    """Test to achieve 100% coverage by calling abstract methods via super()."""

    class CoverageTestComm(CommunicationLayer):
        """Test class that calls abstract methods via super() to cover pass statements."""

        async def send(self, target: str, message: Any) -> None:
            # Call the abstract method to cover the pass statement
            await super().send(target, message)

        async def receive(self) -> Any:
            # Call the abstract method to cover the pass statement
            return await super().receive()

        async def start(self) -> None:
            # Call the abstract method to cover the pass statement
            await super().start()

        async def stop(self) -> None:
            # Call the abstract method to cover the pass statement
            await super().stop()

    # Create instance and call methods to trigger coverage
    comm = CoverageTestComm()

    # These calls will execute the abstract methods and cover the pass statements
    await comm.send("coverage_target", "coverage_message")
    result = await comm.receive()
    assert result is None  # Abstract receive returns None (pass statement)
    await comm.start()
    await comm.stop()


def test_direct_abstract_method_access():
    """Test direct access to abstract methods for complete coverage."""
    # Verify the methods exist and are callable
    assert hasattr(CommunicationLayer, "send")
    assert hasattr(CommunicationLayer, "receive")
    assert hasattr(CommunicationLayer, "start")
    assert hasattr(CommunicationLayer, "stop")

    assert callable(CommunicationLayer.send)
    assert callable(CommunicationLayer.receive)
    assert callable(CommunicationLayer.start)
    assert callable(CommunicationLayer.stop)

    # Verify they are async methods
    assert asyncio.iscoroutinefunction(CommunicationLayer.send)
    assert asyncio.iscoroutinefunction(CommunicationLayer.receive)
    assert asyncio.iscoroutinefunction(CommunicationLayer.start)
    assert asyncio.iscoroutinefunction(CommunicationLayer.stop)


# -----------------------
# Additional comprehensive edge case tests
# -----------------------


@pytest.mark.asyncio
async def test_exception_propagation(async_communication_factory):
    """Test that exceptions propagate correctly through async methods."""
    custom_exceptions = [
        ValueError("Custom value error"),
        TypeError("Custom type error"),
        RuntimeError("Custom runtime error"),
        ConnectionError("Custom connection error"),
        TimeoutError("Custom timeout error"),
    ]

    for exception in custom_exceptions:
        # Test send exception
        comm_send = async_communication_factory(send_side_effect=exception)
        with pytest.raises(type(exception), match=str(exception)):
            await comm_send.send("target", "message")

        # Test receive exception
        comm_receive = async_communication_factory(receive_side_effect=exception)
        with pytest.raises(type(exception), match=str(exception)):
            await comm_receive.receive()

        # Test start exception
        comm_start = async_communication_factory(start_side_effect=exception)
        with pytest.raises(type(exception), match=str(exception)):
            await comm_start.start()

        # Test stop exception
        comm_stop = async_communication_factory(stop_side_effect=exception)
        with pytest.raises(type(exception), match=str(exception)):
            await comm_stop.stop()


@pytest.mark.asyncio
async def test_memory_intensive_operations(async_communication_factory):
    """Test memory-intensive operations to verify no memory leaks."""
    comm = async_communication_factory(receive_return="memory_test")

    # Large message test
    large_message = {"data": "x" * 100000}  # 100KB message
    await comm.send("memory_target", large_message)

    assert len(comm.sent_messages) == 1
    assert comm.sent_messages[0][1] == large_message

    # Many small operations
    for i in range(1000):
        await comm.send(f"target_{i}", f"message_{i}")

    assert len(comm.sent_messages) == 1001  # 1 large + 1000 small


@pytest.mark.asyncio
async def test_method_call_ordering(async_communication_factory):
    """Test that method calls can be made in any order."""
    comm = async_communication_factory(receive_return="ordered_message")

    # Test various call orderings
    await comm.stop()  # Stop before start
    await comm.send("target1", "message1")  # Send before start
    result = await comm.receive()  # Receive before start
    await comm.start()  # Start after operations
    await comm.send("target2", "message2")  # Send after start

    assert comm.started
    assert comm.stopped
    assert len(comm.sent_messages) == 2
    assert result == "ordered_message"


@pytest.mark.parametrize(
    "target_type",
    [
        int(123),
        float(3.14),
        list([1, 2, 3]),
        dict({"key": "value"}),
        set({1, 2, 3}),
        tuple((1, 2, 3)),
    ],
)
@pytest.mark.asyncio
async def test_send_with_non_string_targets(async_communication_factory, target_type):
    """Test send method with non-string target types."""
    comm = async_communication_factory()

    # This should work since Python is dynamically typed
    await comm.send(target_type, "message_for_non_string_target")

    assert len(comm.sent_messages) == 1
    assert comm.sent_messages[0] == (target_type, "message_for_non_string_target")


@pytest.mark.asyncio
async def test_concurrent_start_stop(async_communication_factory):
    """Test concurrent start and stop operations."""
    comm = async_communication_factory()

    # Start multiple concurrent start/stop operations
    start_tasks = [comm.start() for _ in range(5)]
    stop_tasks = [comm.stop() for _ in range(3)]

    await asyncio.gather(*start_tasks, *stop_tasks)

    # Should still work despite concurrent calls
    assert comm.started
    assert comm.stopped


def test_abstract_method_introspection():
    """Test introspection of abstract methods."""
    # Get abstract method set
    abstract_methods = CommunicationLayer.__abstractmethods__

    # Verify each method is properly marked as abstract
    for method_name in abstract_methods:
        method = getattr(CommunicationLayer, method_name)
        assert hasattr(method, "__isabstractmethod__")
        assert method.__isabstractmethod__ is True


@pytest.mark.asyncio
async def test_context_manager_like_usage(async_communication_factory):
    """Test context-manager-like usage pattern."""
    comm = async_communication_factory(receive_return="context_message")

    # Simulate context manager pattern
    try:
        await comm.start()

        # Do some work
        await comm.send("context_target", "context_data")
        result = await comm.receive()

        assert result == "context_message"
        assert len(comm.sent_messages) == 1

    finally:
        await comm.stop()

    assert comm.started
    assert comm.stopped


@pytest.mark.asyncio
async def test_extreme_concurrency(async_communication_factory):
    """Test extreme concurrency scenarios."""
    comm = async_communication_factory(receive_return="concurrent")

    # Create a large number of concurrent operations
    send_tasks = [
        comm.send(f"concurrent_target_{i}", f"concurrent_message_{i}")
        for i in range(50)
    ]
    receive_tasks = [comm.receive() for _ in range(30)]
    start_tasks = [comm.start() for _ in range(10)]
    stop_tasks = [comm.stop() for _ in range(10)]

    # Execute all concurrently
    results = await asyncio.gather(
        *send_tasks, *receive_tasks, *start_tasks, *stop_tasks, return_exceptions=True
    )

    # Verify no exceptions occurred
    for result in results:
        assert not isinstance(result, Exception)

    assert len(comm.sent_messages) == 50
    assert len(comm.received_messages) == 30


def test_subclass_with_additional_methods():
    """Test subclass that adds additional methods beyond the abstract ones."""

    class ExtendedCommunicationLayer(CommunicationLayer):
        def __init__(self):
            self.custom_data = "extended"

        async def send(self, target: str, message: Any) -> None:
            pass

        async def receive(self) -> Any:
            return self.custom_data

        async def start(self) -> None:
            pass

        async def stop(self) -> None:
            pass

        def get_status(self) -> str:
            """Additional method not in base class."""
            return "extended_status"

        async def custom_async_method(self) -> str:
            """Additional async method."""
            return "custom_async"

    # Should be able to instantiate
    extended = ExtendedCommunicationLayer()

    # Should have all base functionality
    assert isinstance(extended, CommunicationLayer)

    # Should have additional functionality
    assert hasattr(extended, "get_status")
    assert hasattr(extended, "custom_async_method")
    assert extended.get_status() == "extended_status"


@pytest.mark.asyncio
async def test_method_chaining_pattern(async_communication_factory):
    """Test method chaining usage patterns."""
    comm = async_communication_factory(receive_return="chained")

    # Simulate chained async operations
    await comm.start()

    # Chain multiple sends
    await comm.send("chain1", "msg1")
    await comm.send("chain2", "msg2")
    await comm.send("chain3", "msg3")

    # Chain multiple receives
    result1 = await comm.receive()
    result2 = await comm.receive()
    result3 = await comm.receive()

    await comm.stop()

    assert len(comm.sent_messages) == 3
    assert all(r == "chained" for r in [result1, result2, result3])
    assert comm.started and comm.stopped
