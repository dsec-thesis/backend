from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel

from backend.contexts.booking.domain import (
    BookingAggregate,
    BookingRepository,
    BookingState,
)
from backend.contexts.shared.domain import BookingId, DriverId, EventBus, ParkinglotId


class Booking(BaseModel):
    id: BookingId
    driver_id: DriverId
    parkinglot_id: ParkinglotId
    state: BookingState
    price: Optional[Decimal]


def create_booking(
    booking_id: BookingId,
    parkinglot_id: ParkinglotId,
    driver_id: DriverId,
    repo: BookingRepository,
    bus: EventBus,
) -> None:
    booking = BookingAggregate.create(booking_id, driver_id, parkinglot_id)
    repo.save(booking)
    bus.publish(booking.pull_events())


def list_bookings(
    driver_id: DriverId,
    repo: BookingRepository,
) -> List[Booking]:
    return [
        Booking(
            id=b.id,
            driver_id=b.driver_id,
            parkinglot_id=b.parkinglot_id,
            state=b.state,
            price=b.price,
        )
        for b in repo.list(driver_id)
    ]


def get_booking(
    driver_id: DriverId,
    booking_id: BookingId,
    repo: BookingRepository,
) -> Optional[Booking]:
    if not (booking := repo.get(driver_id, booking_id)):
        return None

    return Booking(
        id=booking.id,
        driver_id=booking.driver_id,
        parkinglot_id=booking.parkinglot_id,
        state=booking.state,
        price=booking.price,
    )
