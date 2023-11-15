from dependency_injector.wiring import Provide, inject

from backend.apps.container import Container
from backend.contexts.booking.domain import AccommodatedBookingCanceled, BookingCreated
from backend.contexts.parkinglot import application as parkinglots
from backend.contexts.parkinglot.domain import ParkinglotRepository
from backend.contexts.shared.domain import BookingId, EventBus


@inject
def handle_booking_created(
    event: BookingCreated,
    repo: ParkinglotRepository = Provide[Container.parkinglot_repository],
    bus: EventBus = Provide[Container.eventbus],
) -> None:
    return parkinglots.accomodate_booking(
        booking_id=BookingId.from_str(event.aggregate_id),
        parkinglot_id=event.parkinglot_id,
        driver_id=event.driver_id,
        booking_duration=event.duration,
        repo=repo,
        bus=bus,
    )


@inject
def handle_accommodated_booking_canceled(
    event: AccommodatedBookingCanceled,
    repo: ParkinglotRepository = Provide[Container.parkinglot_repository],
    bus: EventBus = Provide[Container.eventbus],
) -> None:
    return parkinglots.release_space(
        parkinglot_id=event.parkinglot_id,
        space_id=event.space_id,
        repo=repo,
        bus=bus,
    )
