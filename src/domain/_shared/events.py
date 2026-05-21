"""Tüm domain event'lerinin temel sınıfı ve correlation context yönetimi."""

from __future__ import annotations

import contextvars
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

_correlation: contextvars.ContextVar[Optional[UUID]] = contextvars.ContextVar(
    "correlation_id", default=None
)


def current_correlation_id() -> Optional[UUID]:
    return _correlation.get()


class correlation_context:
    def __init__(self, cid: UUID | None = None) -> None:
        self._cid = cid or uuid4()
        self._token: contextvars.Token[Optional[UUID]] | None = None

    def __enter__(self) -> UUID:
        self._token = _correlation.set(self._cid)
        return self._cid

    def __exit__(self, *exc: object) -> None:
        assert self._token is not None
        _correlation.reset(self._token)


@dataclass(frozen=True, kw_only=True)
class DomainEvent:
    aggregate_id: str
    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    correlation_id: Optional[UUID] = field(default_factory=current_correlation_id)
