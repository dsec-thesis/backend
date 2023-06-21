from datetime import timedelta
from decimal import Decimal
from enum import Enum
from typing import List, Optional, Protocol

from backend.contexts.shared.domain import (
    AggregateRoot,
    BookingId,
    DomainEvent,
    DriverId,
    ParkinglotId,
)


class BookingState(Enum):
    CREATED = "CREATED"
    ACCOMMODATED = "ACCOMMODATED"
    CANCELED = "CANCELED"


class AccommodatedBookingCanceled(DomainEvent):
    parkinglot_id: ParkinglotId


class BookingCanceled(DomainEvent):
    parkinglot_id: ParkinglotId


class BookingCreated(DomainEvent):
    parkinglot_id: ParkinglotId
    driver_id: DriverId
    duration: Optional[timedelta]


class BookingAggregate(AggregateRoot):
    id: BookingId
    driver_id: DriverId
    parkinglot_id: ParkinglotId
    description: str
    duration: Optional[timedelta]
    state: BookingState
    price: Optional[Decimal]

    @classmethod
    def create(
        cls,
        id: BookingId,
        driver_id: DriverId,
        parkinglot_id: ParkinglotId,
        duration: Optional[timedelta],
        description: str,
    ) -> "BookingAggregate":
        booking = cls(
            id=id,
            created_on=id.datetime,
            updated_on=id.datetime,
            driver_id=driver_id,
            parkinglot_id=parkinglot_id,
            description=description,
            duration=duration,
            state=BookingState.CREATED,
            price=None,
        )
        booking.push_event(
            BookingCreated(
                aggregate_id=str(booking.id),
                parkinglot_id=booking.parkinglot_id,
                driver_id=driver_id,
                duration=booking.duration,
            )
        )
        return booking

    def cancel(self) -> None:
        if self.state == BookingState.CANCELED:
            return
        if self.state == BookingState.ACCOMMODATED:
            self.push_event(
                AccommodatedBookingCanceled(
                    aggregate_id=str(self.id),
                    parkinglot_id=self.parkinglot_id,
                )
            )
        self.push_event(
            BookingCanceled(
                aggregate_id=str(self.id),
                parkinglot_id=self.parkinglot_id,
            )
        )
        self.state = BookingState.CANCELED
        self.refresh_updated_on()

    def assign_price(self, price: Decimal) -> None:
        self.price = price
        self.state = BookingState.ACCOMMODATED
        self.refresh_updated_on()

    def pay(self) -> None:
        ...


class BookingRepository(Protocol):
    def save(self, booking: BookingAggregate) -> None:
        ...

    def get(
        self,
        booking_id: BookingId,
        driver_id: Optional[DriverId] = None,
    ) -> Optional[BookingAggregate]:
        ...

    def list(
        self,
        driver_id: DriverId,
    ) -> List[BookingAggregate]:
        ...
