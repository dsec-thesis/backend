from datetime import timedelta
from decimal import Decimal
from typing import List, Optional

from backend.contexts.booking.domain import (
    BookingAggregate,
    BookingRepository,
)
from backend.contexts.shared.domain import (
    BookingId,
    DriverId,
    EventBus,
    ParkingSpaceId,
    ParkinglotId,
)


def create_booking(
    booking_id: BookingId,
    driver_id: DriverId,
    parkinglot_id: ParkinglotId,
    description: str,
    duration: Optional[timedelta],
    repo: BookingRepository,
    bus: EventBus,
) -> None:
    if repo.get(booking_id, driver_id):
        return
    booking_aggregate = BookingAggregate.create(
        id=booking_id,
        driver_id=driver_id,
        parkinglot_id=parkinglot_id,
        duration=duration,
        description=description,
    )
    repo.save(booking_aggregate)
    bus.publish(booking_aggregate.pull_events())


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


def accomodate(
    booking_id: BookingId,
    price: Decimal,
    space_id: ParkingSpaceId,
    repo: BookingRepository,
    bus: EventBus,
) -> None:
    if not (booking := repo.get(booking_id)):
        return
    booking.accomodate(price, space_id)
    repo.save(booking)
    bus.publish(booking.pull_events())


def start(
    booking_id: BookingId,
    repo: BookingRepository,
    bus: EventBus,
) -> None:
    if not (booking := repo.get(booking_id)):
        return
    booking.start()
    repo.save(booking)
    bus.publish(booking.pull_events())


def finish(
    booking_id: BookingId,
    repo: BookingRepository,
    bus: EventBus,
) -> None:
    if not (booking := repo.get(booking_id)):
        return
    booking.finish()
    repo.save(booking)
    bus.publish(booking.pull_events())
