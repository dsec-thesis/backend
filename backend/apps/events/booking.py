from dependency_injector.wiring import Provide, inject

from backend.apps.container import Container
from backend.contexts.booking.application import (
    assign_price,
    cancel_booking_by_parkinglot,
)
from backend.contexts.booking.domain import BookingRepository
from backend.contexts.parkinglot.domain import BookingAccommodated, BookingRefused
from backend.contexts.shared.domain import EventBus, ParkinglotId


@inject
def handle_booking_refused(
    event: BookingRefused,
    repo: BookingRepository = Provide[Container.booking_repository],
    bus: EventBus = Provide[Container.eventbus],
) -> None:
    return cancel_booking_by_parkinglot(
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
    return assign_price(
        booking_id=event.booking_id,
        price=event.price,
        repo=repo,
        bus=bus,
    )
