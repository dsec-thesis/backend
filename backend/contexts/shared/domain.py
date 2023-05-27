from datetime import datetime
from typing import ClassVar, Generic, List, Protocol, TypeVar
import uuid

from pydantic import BaseModel, Field
from uuid import UUID, uuid4

EventData = TypeVar("EventData")


class BookingId(uuid.UUID):
    ...


class ParkinglotId(uuid.UUID):
    ...


class DriverId(uuid.UUID):
    ...


class OwnerId(uuid.UUID):
    ...


class DomainEvent(BaseModel, Generic[EventData]):
    NAME: ClassVar[str]
    aggregate_id: str
    data: EventData
    id: UUID = Field(default_factory=uuid4)
    created_on: datetime = Field(default_factory=datetime.now)


class EventBus(Protocol):
    def publish(self, events: List[DomainEvent]) -> None:
        ...
