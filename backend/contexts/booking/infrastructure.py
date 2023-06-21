import json
from decimal import Decimal
from typing import Any, Dict, List, Optional

import boto3
from boto3.dynamodb.conditions import Attr, Key

from backend.contexts.booking.domain import (
    BookingAggregate,
    BookingRepository,
)
from backend.contexts.shared.domain import BookingId, DriverId


class DynamodbBookingRepository(BookingRepository):
    def __init__(self, table_name: str, inverted_index: str) -> None:
        self._inverted_index = inverted_index
        resource = boto3.resource("dynamodb")
        self._table = resource.Table(table_name)

    def save(self, booking: BookingAggregate) -> None:
        item = json.loads(
            booking.json(exclude={"id", "driver_id", "version"}),
            parse_float=Decimal,
        )

        self._table.put_item(
            Item={
                "pk": str(booking.driver_id),
                "sk": f"BOOKING::{booking.id}",
                "version": booking.version + 1,
                **item,
            },
            ConditionExpression=(
                Attr("version").not_exists() | Attr("version").eq(booking.version)
            ),
        )

    def get(
        self,
        booking_id: BookingId,
        driver_id: Optional[DriverId] = None,
    ) -> Optional[BookingAggregate]:
        driver_id = driver_id or self._resolve_driver(booking_id)
        if not driver_id:
            return None

        item = self._table.get_item(
            Key={
                "pk": str(driver_id),
                "sk": self._format_sk(booking_id),
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
            ),
            ScanIndexForward=False,
        )["Items"]

        return [self._item_to_booking(item) for item in items]

    def _item_to_booking(
        self,
        item: Dict[str, Any],
    ) -> BookingAggregate:
        item = {
            "id": item["sk"].split("::")[1],
            "driver_id": item["pk"],
            **item,
        }
        if duration := item.get("duration"):
            item["duration"] = int(duration)

        return BookingAggregate.parse_obj(item)

    def _format_sk(self, booking_id: BookingId) -> str:
        return f"BOOKING::{booking_id}"

    def _resolve_driver(self, booking_id: BookingId) -> Optional[DriverId]:
        items = self._table.query(
            IndexName=self._inverted_index,
            KeyConditionExpression=Key("sk").eq(self._format_sk(booking_id)),
        )["Items"]
        if not items:
            return None
        return BookingId.from_str(items[0]["pk"])


class RamBookingRepository(BookingRepository):
    def __init__(self) -> None:
        self.bookings: Dict[BookingId, BookingAggregate] = {}

    def save(self, booking: BookingAggregate) -> None:
        self.bookings[booking.id] = booking

    def get(
        self,
        booking_id: BookingId,
        driver_id: Optional[DriverId] = None,
    ) -> Optional[BookingAggregate]:
        return self.bookings.get(booking_id)

    def list(
        self,
        driver_id: DriverId,
    ) -> List[BookingAggregate]:
        return [b for b in self.bookings.values() if b.driver_id == driver_id]
