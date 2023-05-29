from datetime import datetime
from typing import Generic, List, Protocol, TypeVar
import uuid

from pydantic import BaseModel, Field, PrivateAttr
from uuid import UUID, uuid4

EventData = TypeVar("EventData")
AggregateId = TypeVar("AggregateId")


class BookingId(uuid.UUID):
    ...


class ParkinglotId(uuid.UUID):
    ...


class DriverId(uuid.UUID):
    ...


class OwnerId(uuid.UUID):
    ...


class ParkingSpaceId(uuid.UUID):
    ...


class DomainEvent(BaseModel, Generic[AggregateId]):
    id: UUID = Field(default_factory=uuid4)
    aggregate_id: AggregateId
    created_on: datetime = Field(default_factory=datetime.now)

    @property
    def event_name(self) -> str:
        return type(self).__name__


class EventBus(Protocol):
    def publish(self, events: List[DomainEvent]) -> None:
        ...


class AggregateRoot(BaseModel, Generic[AggregateId]):
    id: AggregateId
    version: int = 0
    _events: List[DomainEvent[AggregateId]] = PrivateAttr(default_factory=list)

    def pull_events(self) -> List[DomainEvent]:
        events = [e for e in self._events]
        self._events = []
        return events

    def push_event(self, event: DomainEvent[AggregateId]) -> None:
        self._events.append(event)
