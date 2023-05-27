from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from typing import ClassVar, List, Optional, Protocol

from pydantic import BaseModel

from backend.contexts.shared.domain import (
    BookingId,
    DomainEvent,
    DriverId,
    ParkinglotId,
)


class BookingState(Enum):
    CREATED = "CREATED"
    ACCOMMODATED = "ACCOMMODATED"
    REFUSED = "REFUSED"
    CANCELED = "CANCELED"


class AccommodatedBookingCanceledData(BaseModel):
    parkinglot_id: ParkinglotId


class AccommodatedBookingCanceled(DomainEvent[AccommodatedBookingCanceledData]):
    NAME: ClassVar[str] = "AccommodatedBookingCanceled"


class BookingCanceledData(BaseModel):
    parkinglot_id: ParkinglotId


class BookingCanceled(DomainEvent[BookingCanceledData]):
    NAME: ClassVar[str] = "AccommodatedBookingCanceled"


@dataclass
class BookingCreatedData:
    parkinglot_id: ParkinglotId


class BookingCreated(DomainEvent[BookingCreatedData]):
    NAME: ClassVar[str] = "BookingCreated"


@dataclass
class BookingAggregate:
    id: BookingId
    driver_id: DriverId
    parkinglot_id: ParkinglotId
    state: BookingState
    version: int
    price: Optional[Decimal]
    events: List[DomainEvent] = field(default_factory=list)

    @classmethod
    def create(
        cls,
        id: BookingId,
        driver_id: DriverId,
        parkinglot_id: ParkinglotId,
    ) -> "BookingAggregate":
        booking = cls(
            id=id,
            driver_id=driver_id,
            parkinglot_id=parkinglot_id,
            state=BookingState.CREATED,
            version=0,
            price=None,
            events=[],
        )
        booking.events.append(
            BookingCreated(
                aggregate_id=str(booking.id),
                data=BookingCreatedData(
                    parkinglot_id=booking.parkinglot_id,
                ),
            )
        )
        return booking

    def cancel(self) -> None:
        if self.state == BookingState.CANCELED:
            return
        if self.state == BookingState.ACCOMMODATED:
            self.events.append(
                AccommodatedBookingCanceled(
                    aggregate_id=str(self.id),
                    data=AccommodatedBookingCanceledData(
                        parkinglot_id=self.parkinglot_id,
                    ),
                )
            )
        self.events.append(
            BookingCanceled(
                aggregate_id=str(self.id),
                data=BookingCanceledData(
                    parkinglot_id=self.parkinglot_id,
                ),
            )
        )
        self.state = BookingState.CANCELED

    def assign_price(self, price: Decimal) -> None:
        self.price = price
        self.state = BookingState.ACCOMMODATED

    def pay(self) -> None:
        ...


class BookingRepository(Protocol):
    def save(self, booking: BookingAggregate) -> None:
        ...

    def get(
        self,
        driver_id: DriverId,
        booking_id: BookingId,
    ) -> Optional[BookingAggregate]:
        ...

    def list(
        self,
        driver_id: DriverId,
    ) -> List[BookingAggregate]:
        ...
