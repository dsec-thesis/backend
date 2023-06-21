from datetime import timedelta
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel

from backend.contexts.booking.domain import (
    BookingAggregate,
    BookingRepository,
)
from backend.contexts.shared.domain import BookingId, DriverId, EventBus, ParkinglotId


class CreateBookingCommand(BaseModel):
    booking_id: BookingId
    parkinglot_id: ParkinglotId
    description: str
    duration: Optional[timedelta] = None

    def handle(
        self,
        driver_id: DriverId,
        repo: BookingRepository,
        bus: EventBus,
    ):
        booking = BookingAggregate.create(
            self.booking_id,
            driver_id,
            self.parkinglot_id,
            self.duration,
            self.description,
        )
        repo.save(booking)
        bus.publish(booking.pull_events())


def cancel_booking_by_parkinglot(
    booking_id: BookingId,
    parkinglot_id: ParkinglotId,
    repo: BookingRepository,
    bus: EventBus,
) -> None:
    if not (booking := repo.get(booking_id)):
        return
    if booking.parkinglot_id != parkinglot_id:
        return
    booking.cancel()
    repo.save(booking)
    bus.publish(booking.pull_events())


def cancel_booking_by_driver(
    booking_id: BookingId,
    driver_id: DriverId,
    repo: BookingRepository,
    bus: EventBus,
) -> None:
    if not (booking := repo.get(booking_id, driver_id)):
        return
    booking.cancel()
    repo.save(booking)
    bus.publish(booking.pull_events())


def list_bookings(
    driver_id: DriverId,
    repo: BookingRepository,
) -> List[BookingAggregate]:
    return repo.list(driver_id)


def get_booking(
    driver_id: DriverId,
    booking_id: BookingId,
    repo: BookingRepository,
) -> Optional[BookingAggregate]:
    return repo.get(booking_id, driver_id)


def assign_price(
    booking_id: BookingId,
    price: Decimal,
    repo: BookingRepository,
    bus: EventBus,
) -> None:
    if not (booking := repo.get(booking_id)):
        return
    booking.assign_price(price)
    repo.save(booking)
    bus.publish(booking.pull_events())
