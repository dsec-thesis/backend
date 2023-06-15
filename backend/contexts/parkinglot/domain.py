from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Optional, Protocol

from pydantic import BaseModel, Field
import h3

from backend.contexts.shared.domain import (
    AggregateRoot,
    BookingId,
    DomainEvent,
    DriverId,
    OwnerId,
    ParkinglotId,
    ParkingSpaceId,
)

Price = Decimal


class Coordinates(BaseModel):
    lat: Decimal = Field(..., ge=-90, le=90)
    lng: Decimal = Field(..., gt=-180, le=180)


class ParkingSpace(BaseModel):
    id: ParkingSpaceId
    booked_by: Optional[DriverId] = None
    booked_from: Optional[datetime] = None
    booked_util: Optional[datetime] = None
    booking_id: Optional[BookingId] = None

    def is_booked(self) -> bool:
        return self.booked_by is not None

    def book(
        self,
        driver_id: DriverId,
        booking_id: BookingId,
        booking_duration: Optional[timedelta],
    ) -> None:
        self.booked_by = driver_id
        self.booking_id = booking_id
        self.booked_from = datetime.now()
        if booking_duration:
            self.booked_util = self.booked_from + booking_duration


class ParkinglotAggregate(AggregateRoot[ParkinglotId]):
    owner_id: OwnerId
    name: str
    street: str
    coordinates: Coordinates
    h3cell: str
    price: Price
    free_spaces: int = 0
    spaces: List[ParkingSpace] = Field(default_factory=list)

    @classmethod
    def create(
        cls,
        parkinglot_id: ParkinglotId,
        owner_id: OwnerId,
        name: str,
        street: str,
        coordinates: Coordinates,
        price: Price,
    ) -> "ParkinglotAggregate":
        parkinglot = cls(
            id=parkinglot_id,
            owner_id=owner_id,
            created_on=datetime.now(),
            updated_on=datetime.now(),
            name=name,
            street=street,
            coordinates=coordinates,
            h3cell=h3.latlng_to_cell(coordinates.lat, coordinates.lng, 8),
            price=price,
        )
        parkinglot.push_event(
            ParkinglotCreated(
                aggregate_id=parkinglot.id,
                owner_id=parkinglot.owner_id,
                name=parkinglot.name,
                street=parkinglot.street,
                coordinates=parkinglot.coordinates,
            )
        )
        return parkinglot

    def change_price(self, price: Price) -> None:
        self.price = price
        self.refresh_updated_on()

    def find_free_space(self) -> Optional[ParkingSpace]:
        return next((s for s in self.spaces if s.booking_id is None), None)

    def accommodate_booking(
        self,
        driver_id: DriverId,
        booking_id: BookingId,
        booking_duration: Optional[timedelta] = None,
    ) -> Optional[Price]:
        if not self.free_spaces:
            return None
        if not (free_space := self.find_free_space()):
            return None
        free_space.book(driver_id, booking_id, booking_duration)
        self.free_spaces -= 1
        self.refresh_updated_on()
        if not booking_duration:
            return None
        return self.price * Decimal(booking_duration.total_seconds())

    def register_spaces(self, space_ids: List[ParkingSpaceId]) -> None:
        spaces = [ParkingSpace(id=space_id) for space_id in space_ids]
        self.spaces.extend(spaces)
        for space in spaces:
            self.push_event(
                ParkingSpaceCreated(aggregate_id=self.id, space_id=space.id)
            )
        self.refresh_updated_on()


class ParkinglotCreated(DomainEvent[ParkinglotId]):
    owner_id: OwnerId
    name: str
    street: str
    coordinates: Coordinates


class BookingAccommodated(DomainEvent[ParkinglotId]):
    price: Price


class ParkingSpaceCreated(DomainEvent[ParkinglotId]):
    space_id: ParkingSpaceId


class ParkinglotRepository(Protocol):
    def save(self, parkinglot: ParkinglotAggregate) -> None:
        ...

    def get(
        self,
        parkinglot_id: ParkinglotId,
        owner_id: Optional[OwnerId] = None,
    ) -> Optional[ParkinglotAggregate]:
        ...

    def list(self, owner_id: OwnerId) -> List[ParkinglotAggregate]:
        ...
