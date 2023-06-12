from typing import List, Optional

from backend.contexts.booking.domain import (
    BookingAggregate,
    BookingRepository,
)
from backend.contexts.shared.domain import BookingId, DriverId, EventBus, ParkinglotId


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
) -> List[BookingAggregate]:
    return repo.list(driver_id)


def get_booking(
    driver_id: DriverId,
    booking_id: BookingId,
    repo: BookingRepository,
) -> Optional[BookingAggregate]:
    return repo.get(driver_id, booking_id)
