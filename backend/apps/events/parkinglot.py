from dependency_injector.wiring import Provide, inject

from backend.apps.container import Container
from backend.contexts.booking.domain import BookingCreated
from backend.contexts.parkinglot.application import AccommodateBookingCommand
from backend.contexts.parkinglot.domain import ParkinglotRepository
from backend.contexts.shared.domain import BookingId, EventBus


@inject
def handle_booking_created(
    event: BookingCreated,
    repo: ParkinglotRepository = Provide[Container.parkinglot_repository],
    bus: EventBus = Provide[Container.eventbus],
) -> None:
    command = AccommodateBookingCommand(
        booking_id=BookingId.from_str(event.aggregate_id),
        booking_duration=event.duration,
        parkinglot_id=event.parkinglot_id,
    )
    return command.handle(driver_id=event.driver_id, repo=repo, bus=bus)
