from typing import Dict, List, Protocol, Tuple, Type

from aws_lambda_typing.context import Context
from aws_lambda_typing.events import SNSEvent

from backend.contexts.booking.domain import BookingCreated
from backend.contexts.shared.domain import DomainEvent


class EventHandler(Protocol):
    def __call__(self, event: DomainEvent) -> None:
        ...


register: Dict[str, Tuple[Type[DomainEvent], List[EventHandler]]] = {
    "BookingCreated": (BookingCreated, [])
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
            event_handler(domain_event)
