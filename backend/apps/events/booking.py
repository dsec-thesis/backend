from dependency_injector.wiring import Provide, inject

from backend.apps.container import Container
from backend.contexts.booking import application as bookings
from backend.contexts.booking.domain import BookingRepository
from backend.contexts.parkinglot.domain import (
    BookingAccommodated,
    BookingRefused,
    DriverArrived,
    DriverLeft,
)
from backend.contexts.shared.domain import EventBus, ParkinglotId


@inject
def handle_booking_refused(
    event: BookingRefused,
    repo: BookingRepository = Provide[Container.booking_repository],
    bus: EventBus = Provide[Container.eventbus],
) -> None:
    return bookings.cancel_booking_by_parkinglot(
        booking_id=event.booking_id,
        parkinglot_id=ParkinglotId(event.aggregate_id),
        repo=repo,
        bus=bus,
    )


@inject
def handle_booking_accommodated(
    event: BookingAccommodated,
    repo: BookingRepository = Provide[Container.booking_repository],
    bus: EventBus = Provide[Container.eventbus],
) -> None:
    return bookings.accomodate(
        booking_id=event.booking_id,
        price=event.price,
        space_id=event.space_id,
        repo=repo,
        bus=bus,
    )


@inject
def handle_driver_arrived(
    event: DriverArrived,
    repo: BookingRepository = Provide[Container.booking_repository],
    bus: EventBus = Provide[Container.eventbus],
) -> None:
    return bookings.start(
        booking_id=event.booking_id,
        repo=repo,
        bus=bus,
    )


@inject
def handle_driver_left(
    event: DriverLeft,
    repo: BookingRepository = Provide[Container.booking_repository],
    bus: EventBus = Provide[Container.eventbus],
) -> None:
    return bookings.finish(
        booking_id=event.booking_id,
        repo=repo,
        bus=bus,
    )
