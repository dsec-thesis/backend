from datetime import datetime
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
    duration: Optional[datetime] = None

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
