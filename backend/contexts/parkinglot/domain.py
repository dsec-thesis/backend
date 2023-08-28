from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Optional, Protocol
from uuid import UUID

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
    internal_id: int
    booked_by: Optional[DriverId] = None
    booked_from: Optional[datetime] = None
    booked_util: Optional[datetime] = None
    booking_id: Optional[BookingId] = None
    driver_arrival_time: Optional[datetime] = None

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

    def take(self):
        self.driver_arrival_time = datetime.now()

    def release(self) -> None:
        self.booked_by = None
        self.booked_from = None
        self.booked_util = None
        self.booking_id = None
        self.driver_arrival_time = None


class ParkinglotAggregate(AggregateRoot):
    id: ParkinglotId
    owner_id: OwnerId
    name: str
    street: str
    coordinates: Coordinates
    h3cell: str
    price: Price
    concentrator_id: Optional[UUID]
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
            concentrator_id=None,
        )
        parkinglot.push_event(
            ParkinglotCreated(
                aggregate_id=str(parkinglot.id),
                owner_id=parkinglot.owner_id,
                name=parkinglot.name,
                street=parkinglot.street,
                coordinates=parkinglot.coordinates,
            )
        )
        return parkinglot

    def register_concentrator(self, concentrator_id: UUID) -> None:
        self.concentrator_id = concentrator_id

    def change_price(self, price: Price) -> None:
        self.price = price

    def find_free_space(self) -> Optional[ParkingSpace]:
        return next((s for s in self.spaces if s.booking_id is None), None)

    def accommodate_booking(
        self,
        driver_id: DriverId,
        booking_id: BookingId,
        booking_duration: Optional[timedelta] = None,
    ) -> None:
        if not self.free_spaces:
            self.push_event(
                BookingRefused(aggregate_id=str(self.id), booking_id=booking_id)
            )
            return None
        if not (free_space := self.find_free_space()):
            self.push_event(
                BookingRefused(aggregate_id=str(self.id), booking_id=booking_id)
            )
            return None
        free_space.book(driver_id, booking_id, booking_duration)
        self.free_spaces -= 1
        self.push_event(
            BookingAccommodated(
                aggregate_id=str(self.id),
                booking_id=booking_id,
                price=self.price,
                space_id=free_space.id,
            )
        )

    def find_space(self, space_id: ParkingSpaceId) -> Optional[ParkingSpace]:
        return next((s for s in self.spaces if s.id == space_id), None)

    def take_space(self, space_id: ParkingSpaceId) -> None:
        if not (space := self.find_space(space_id)):
            return None
        if not space.booking_id or not space.booked_by:
            self.push_event(
                DriverArrivedAtUnBookedSpace(
                    aggregate_id=str(self.id),
                    space_id=space.id,
                )
            )
            return None
        space.take()
        self.push_event(
            DriverArrived(
                aggregate_id=str(self.id),
                space_id=space.id,
                driver_id=space.booked_by,
                booking_id=space.booking_id,
            )
        )
        return None

    def register_spaces(self, space_ids: List[ParkingSpaceId]) -> None:
        initial_internal_id = len(self.spaces)
        spaces = [
            ParkingSpace(id=space_id, internal_id=initial_internal_id + i)
            for i, space_id in enumerate(space_ids)
        ]
        self.free_spaces += len(spaces)
        self.spaces.extend(spaces)
        for space in spaces:
            self.push_event(
                ParkingSpaceCreated(aggregate_id=str(self.id), space_id=space.id)
            )

    def release_space(self, space_id: ParkingSpaceId) -> None:
        if not (space := self.find_space(space_id)):
            return None
        if not space.booked_by or not space.booking_id:
            return None
        self.push_event(
            DriverLeft(
                aggregate_id=str(self.id),
                space_id=space.id,
                driver_id=space.booked_by,
                booking_id=space.booking_id,
            )
        )
        space.release()
        self.free_spaces += 1
        return None


class ParkinglotCreated(DomainEvent):
    owner_id: OwnerId
    name: str
    street: str
    coordinates: Coordinates


class BookingAccommodated(DomainEvent):
    booking_id: BookingId
    price: Price
    space_id: ParkingSpaceId


class BookingRefused(DomainEvent):
    booking_id: BookingId


class ParkingSpaceCreated(DomainEvent):
    space_id: ParkingSpaceId


class DriverArrivedAtUnBookedSpace(DomainEvent):
    space_id: ParkingSpaceId


class DriverArrived(DomainEvent):
    space_id: ParkingSpaceId
    driver_id: DriverId
    booking_id: BookingId


class DriverLeft(DomainEvent):
    space_id: ParkingSpaceId
    driver_id: DriverId
    booking_id: BookingId


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
