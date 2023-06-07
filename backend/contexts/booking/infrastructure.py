from typing import Any, Dict, List, Optional, Tuple

import boto3
from boto3.dynamodb.conditions import Attr

from backend.contexts.booking.domain import (
    BookingAggregate,
    BookingRepository,
    BookingState,
)
from backend.contexts.shared.domain import BookingId
from backend.contexts.shared.domain import ParkinglotId
from backend.contexts.shared.domain import DriverId
from boto3.dynamodb.conditions import Attr, Key


class DynamodbBookingRepository(BookingRepository):
    def __init__(self, table_name: str) -> None:
        resource = boto3.resource("dynamodb")
        self._table = resource.Table(table_name)

    def save(self, booking: BookingAggregate) -> None:
        self._table.put_item(
            Item={
                "pk": str(booking.driver_id),
                "sk": f"BOOKING::{booking.id}",
                "parkinglot_id": str(booking.parkinglot_id),
                "state": booking.state.value,
                "version": booking.version + 1,
                "price": booking.price,
            },
            ConditionExpression=(
                Attr("version").not_exists() | Attr("version").eq(booking.version)
            ),
        )

    def get(
        self,
        driver_id: DriverId,
        booking_id: BookingId,
    ) -> Optional[BookingAggregate]:
        item = self._table.get_item(
            Key={
                "pk": str(driver_id),
                "sk": f"BOOKING::{booking_id}",
            }
        )["Item"]

        return self._item_to_booking(item) if item else None

    def list(
        self,
        driver_id: DriverId,
    ) -> List[BookingAggregate]:
        items = self._table.query(
            KeyConditionExpression=(
                Key("pk").eq(str(driver_id)) & Key("sk").begins_with("BOOKING::")
            )
        )["Items"]

        return [self._item_to_booking(item) for item in items]

    def _item_to_booking(
        self,
        item: Dict[str, Any],
    ) -> BookingAggregate:
        return BookingAggregate(
            id=BookingId(item["sk"].split("::")[1]),  # type: ignore
            driver_id=DriverId(item["pk"]),  # type: ignore
            parkinglot_id=ParkinglotId(item["parkinglot_id"]),  # type: ignore
            state=BookingState(item["state"]),
            version=item["version"],  # type: ignore
            price=item["price"],  # type: ignore
        )


class RamBookingRepository(BookingRepository):
    def __init__(self) -> None:
        self.bookings: Dict[Tuple[DriverId, BookingId], BookingAggregate] = {}

    def save(self, booking: BookingAggregate) -> None:
        self.bookings[(booking.driver_id, booking.id)] = booking

    def get(
        self,
        driver_id: DriverId,
        booking_id: BookingId,
    ) -> Optional[BookingAggregate]:
        return self.bookings.get((driver_id, booking_id))

    def list(
        self,
        driver_id: DriverId,
    ) -> List[BookingAggregate]:
        return [b for b in self.bookings.values() if b.driver_id == driver_id]
