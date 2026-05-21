"""Sistemin omurgası: tip tabanlı asyncio publish/subscribe.

Bir modül, kendi event sınıfını içe aktarır ve `bus.publish(event)` ile yayar.
Dinlemek isteyen modül, başlangıçta `bus.subscribe(EventType, handler)` ile bağlanır.

Subclass kuralı: handler bir base event'e subscribe olursa, alt sınıf event'leri de alır.
Örn: `subscribe(DomainEvent, log_all)` tüm event'leri yakalar.
"""

from __future__ import annotations

import asyncio
import logging
from collections import defaultdict
from typing import Awaitable, Callable
from uuid import UUID, uuid4

from domain._shared.events import DomainEvent

log = logging.getLogger(__name__)

Handler = Callable[[DomainEvent], Awaitable[None]]


class SubscriptionToken:
    __slots__ = ("id", "event_type", "handler")

    def __init__(self, event_type: type[DomainEvent], handler: Handler) -> None:
        self.id: UUID = uuid4()
        self.event_type = event_type
        self.handler = handler


class AsyncEventBus:
    def __init__(self) -> None:
        self._subs: dict[type[DomainEvent], list[SubscriptionToken]] = defaultdict(list)

    def subscribe(self, event_type: type[DomainEvent], handler: Handler) -> SubscriptionToken:
        token = SubscriptionToken(event_type, handler)
        self._subs[event_type].append(token)
        log.debug("subscribe %s -> %s", event_type.__name__, handler.__qualname__)
        return token

    def unsubscribe(self, token: SubscriptionToken) -> None:
        self._subs[token.event_type] = [
            t for t in self._subs[token.event_type] if t.id != token.id
        ]

    async def publish(self, event: DomainEvent) -> None:
        handlers = self._collect_handlers(type(event))
        if not handlers:
            return
        await asyncio.gather(*(self._safe_call(h, event) for h in handlers))

    async def publish_many(self, events: list[DomainEvent]) -> None:
        for e in events:
            await self.publish(e)

    def _collect_handlers(self, event_cls: type[DomainEvent]) -> list[Handler]:
        out: list[Handler] = []
        for cls, tokens in self._subs.items():
            if issubclass(event_cls, cls):
                out.extend(t.handler for t in tokens)
        return out

    async def _safe_call(self, handler: Handler, event: DomainEvent) -> None:
        try:
            await handler(event)
        except Exception:
            log.exception("handler %s patladı, event=%s", handler.__qualname__, type(event).__name__)
