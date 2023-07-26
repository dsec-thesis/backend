import uuid
from datetime import datetime
from typing import List, Protocol, TypeVar

import ulid
from pydantic import BaseModel, Field, PrivateAttr
from pydantic.json import ENCODERS_BY_TYPE

EventData = TypeVar("EventData")
AggregateId = TypeVar("AggregateId")


class ULID(ulid.ULID):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        return v if isinstance(v, ULID) else ULID.from_str(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(
            type="string",
            format="ulid",
            examples=[str(ULID()), str(ULID())],
        )


ENCODERS_BY_TYPE[ULID] = str


class BookingId(ULID):
    ...


class ParkinglotId(uuid.UUID):
    ...


class DriverId(uuid.UUID):
    ...


class OwnerId(uuid.UUID):
    ...


class ParkingSpaceId(uuid.UUID):
    ...


class DomainEvent(BaseModel):
    id: ULID = Field(default_factory=ULID)
    aggregate_id: str

    @property
    def event_name(self) -> str:
        return type(self).__name__

    class Config:
        json_encoders = {
            ULID: lambda v: str(v),
        }


class EventBus(Protocol):
    def publish(self, events: List[DomainEvent]) -> None:
        ...


class AggregateRoot(BaseModel):
    version: int = 0
    created_on: datetime
    updated_on: datetime
    _events: List[DomainEvent] = PrivateAttr(default_factory=list)

    def pull_events(self) -> List[DomainEvent]:
        events = [e for e in self._events]
        self._events = []
        return events

    def push_event(self, event: DomainEvent) -> None:
        self._events.append(event)

    def refresh_updated_on(self) -> None:
        self.updated_on = datetime.now()

    class Config:
        json_encoders = {
            ULID: lambda v: str(v),
            datetime: lambda v: v.timestamp(),
        }
