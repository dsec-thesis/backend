from typing import Any, Dict, List, Protocol, Tuple, Type

from aws_lambda_typing.context import Context
from aws_lambda_typing.events import SNSEvent

from backend.apps.container import Container
from backend.apps.events.booking import handle_booking_refused
from backend.apps.events.parkinglot import handle_booking_created
from backend.contexts.booking.domain import (
    AccommodatedBookingCanceled,
    BookingCanceled,
    BookingCreated,
)
from backend.contexts.parkinglot.domain import (
    BookingAccommodated,
    BookingRefused,
    ParkinglotCreated,
    ParkingSpaceCreated,
)
from backend.contexts.shared.domain import DomainEvent


class EventHandler(Protocol):
    __name__: str

    def __call__(self, event: Any) -> None:
        ...


def null_handler(event: Any) -> None:
    ...


container = Container()

register: Dict[str, Tuple[Type[DomainEvent], List[EventHandler]]] = {
    "BookingCreated": (BookingCreated, [handle_booking_created]),
    "BookingCanceled": (BookingCanceled, [null_handler]),
    "AccommodatedBookingCanceled": (AccommodatedBookingCanceled, [null_handler]),
    "BookingRefused": (BookingRefused, [handle_booking_refused]),
    "ParkinglotCreated": (ParkinglotCreated, [null_handler]),
    "BookingAccommodated": (BookingAccommodated, [null_handler]),
    "ParkingSpaceCreated": (ParkingSpaceCreated, [null_handler]),
}


def handler(event: SNSEvent, context: Context):
    for record in event["Records"]:
        event_name = record["Sns"]["MessageAttributes"]["name"]["Value"]
        raw_event = record["Sns"]["Message"]

        event_type, event_handlers = register.get(event_name, (None, None))
        if not (event_type and event_handlers):
            continue

        domain_event = event_type.parse_raw(raw_event)
        for event_handler in event_handlers:
            print(f"event: {event_name} | handler: {event_handler.__name__}")
            event_handler(domain_event)
