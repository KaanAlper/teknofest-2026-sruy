"""AsyncEventBus birim testleri."""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from domain._shared.events import DomainEvent
from eventbus.async_bus import AsyncEventBus


@dataclass(frozen=True, kw_only=True)
class _Foo(DomainEvent):
    msg: str


@dataclass(frozen=True, kw_only=True)
class _Bar(DomainEvent):
    n: int


@pytest.mark.asyncio
async def test_subscribe_and_publish():
    bus = AsyncEventBus()
    received: list[_Foo] = []

    async def handler(e: DomainEvent) -> None:
        assert isinstance(e, _Foo)
        received.append(e)

    bus.subscribe(_Foo, handler)
    await bus.publish(_Foo(aggregate_id="x", msg="hi"))
    assert len(received) == 1
    assert received[0].msg == "hi"


@pytest.mark.asyncio
async def test_handler_exception_does_not_block_others():
    bus = AsyncEventBus()
    received: list[str] = []

    async def bad(_: DomainEvent) -> None:
        raise RuntimeError("boom")

    async def good(_: DomainEvent) -> None:
        received.append("ok")

    bus.subscribe(_Foo, bad)
    bus.subscribe(_Foo, good)
    await bus.publish(_Foo(aggregate_id="x", msg="."))
    assert received == ["ok"]


@pytest.mark.asyncio
async def test_unsubscribe():
    bus = AsyncEventBus()
    received: list[_Bar] = []

    async def h(e: DomainEvent) -> None:
        assert isinstance(e, _Bar)
        received.append(e)

    token = bus.subscribe(_Bar, h)
    await bus.publish(_Bar(aggregate_id="x", n=1))
    bus.unsubscribe(token)
    await bus.publish(_Bar(aggregate_id="x", n=2))
    assert len(received) == 1
